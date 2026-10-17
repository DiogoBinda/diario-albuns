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
st.caption("Catálogo público de álbuns e avaliações")

dados = carregar_dados()

if dados:
    df = pd.DataFrame(dados)
    
    # Exibe métricas no topo
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Total de Álbuns", len(df))
    with col_m2:
        if "nota" in df.columns:
            st.metric("Média de Notas", round(pd.to_numeric(df["nota"], errors="coerce").mean(), 1))

    st.markdown("---")
    
    # Exibe a tabela interativa com todos os seus dados
    st.subheader("📚 Coleção")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Nenhum dado encontrado na tabela. Verifique se o nome da tabela no código é o mesmo do Supabase.")

# --- BARRA LATERAL (ADMIN) ---
st.sidebar.header("⚙️ Painel de Administração")
senha = st.sidebar.text_input("Senha para adicionar/editar:", type="password")

# Coloque a sua senha aqui
if senha == "Atheusts123":
    st.sidebar.success("Acesso autorizado!")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Novo Registo")
    
    with st.sidebar.form("form_add", clear_on_submit=True):
        col1 = st.text_input("Nome/Título do Álbum")
        col2 = st.text_input("Banda/Artista")
        col3 = st.text_input("Gênero/Estilo")
        col4 = st.number_input("Nota", min_value=1.0, max_value=10.0, step=0.5, value=10.0)
        
        salvar = st.form_submit_button("Salvar")
        if salvar:
            # Ajuste as chaves abaixo para os nomes exatos das colunas no seu Supabase
            novo = {
                "nome": col1,
                "banda": col2,
                "genero": col3,
                "nota": col4
            }
            try:
                supabase.table("albuns").insert(novo).execute()
                st.sidebar.success("Salvo com sucesso!")
                st.rerun()
            except Exception as err:
                st.sidebar.error(f"Erro ao salvar: {err}")
