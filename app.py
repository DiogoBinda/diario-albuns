import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração inicial da página
st.set_page_config(
    page_title="Diário de Álbuns",
    page_icon="🎵",
    layout="wide"
)

# Conexão com o Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")

# Função para carregar os dados
def carregar_dados():
    try:
        # Substitua "albuns" pelo nome exato da sua tabela se for diferente
        response = supabase.table("albuns").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar álbuns: {e}")
        return []

# --- CABEÇALHO PRINCIPAL ---
st.title("🎵 Diário de Álbuns")
st.caption("Catálogo público de álbuns, avaliações e comentários")

dados = carregar_dados()

if dados:
    df = pd.DataFrame(dados)
    
    # Métricas no topo
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Total de Álbuns", len(df))
    with col_m2:
        if "nota" in df.columns:
            st.metric("Média de Notas", round(pd.to_numeric(df["nota"], errors="coerce").mean(), 1))

    st.markdown("---")
    
    # Exibe a coleção em tabela com ajuste de largura
    st.subheader("📚 Coleção de Álbuns")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualização detalhada em cards (com comentários em destaque)
    st.markdown("---")
    st.subheader("💬 Resenhas e Comentários")
    
    for idx, album in enumerate(dados):
        nome = album.get("nome") or album.get("titulo") or "Álbum sem título"
        banda = album.get("banda") or album.get("artista") or "Banda não informada"
        nota = album.get("nota", "N/A")
        genero = album.get("genero", "")
        comentario = album.get("comentario") or album.get("resenha") or album.get("obs") or "Sem comentários registrados."
        
        with st.expander(f"⭐ {nota}/10 — **{nome}** ({banda})"):
            if genero:
                st.caption(f"**Gênero:** {genero}")
            st.write(f"**Comentário / Resenha:** {comentario}")

else:
    st.warning("Nenhum dado encontrado na tabela. Verifique se o nome da tabela no código é o mesmo do Supabase.")

# --- BARRA LATERAL (ADMIN) ---
st.sidebar.header("⚙️ Painel de Administração")
senha = st.sidebar.text_input("Senha para adicionar/editar:", type="password")

if senha == "Atheusts123": # Troque pela sua senha
    st.sidebar.success("Acesso autorizado!")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Novo Registo")
    
    with st.sidebar.form("form_add", clear_on_submit=True):
        col_nome = st.text_input("Nome/Título do Álbum")
        col_banda = st.text_input("Banda/Artista")
        col_genero = st.text_input("Gênero/Estilo")
        col_nota = st.number_input("Nota", min_value=1.0, max_value=10.0, step=0.5, value=10.0)
        col_comentario = st.text_area("Comentário / Resenha")
        
        salvar = st.form_submit_button("Salvar")
        if salvar:
            # Ajuste o nome da chave "comentario" caso a coluna no Supabase tenha outro nome (ex: "resenha")
            novo = {
                "nome": col_nome,
                "banda": col_banda,
                "genero": col_genero,
                "nota": col_nota,
                "comentario": col_comentario
            }
            try:
                supabase.table("albuns").insert(novo).execute()
                st.sidebar.success("Salvo com sucesso!")
                st.rerun()
            except Exception as err:
                st.sidebar.error(f"Erro ao salvar: {err}")
