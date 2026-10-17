import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Heavy Metal Vault",
    page_icon="🤘",
    layout="wide"
)

# ==========================================
# 2. CONEXÃO COM O SUPABASE
# ==========================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")

# Função para buscar todos os álbuns da tabela
def carregar_albuns():
    try:
        response = supabase.table("albuns").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return []

# ==========================================
# 3. ESTILO CSS PERSONALIZADO (PRETO, AZUL E VERMELHO)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    h1, h2, h3 {
        color: #66fcf1 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    strong {
        color: #ff2e63 !important;
    }
    .stButton > button {
        background-color: #ff2e63 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #e02353 !important;
        box-shadow: 0px 0px 10px rgba(255, 46, 99, 0.6);
    }
    section[data-testid="stSidebar"] {
        background-color: #1f2833 !important;
    }
    .album-card {
        background-color: #1f2833;
        padding: 18px;
        border-radius: 8px;
        border-left: 5px solid #ff2e63;
        margin-bottom: 15px;
    }
    .album-title {
        color: #66fcf1;
        margin: 0;
        font-size: 1.3rem;
    }
    .album-info {
        color: #c5c6c7;
        margin: 5px 0;
    }
    .album-rating {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ff2e63;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. ÁREA PÚBLICA (Visível para todo mundo)
# ==========================================
st.title("🤘 Catálogo de Álbuns de Heavy Metal")
st.write("Explore a coleção de álbuns, notas de 1 a 10 e subgêneros.")

dados_albuns = carregar_albuns()

# Filtros
st.subheader("🔍 Filtrar Catálogo")
col_filtro1, col_filtro2 = st.columns(2)

subgeneros_disponiveis = ["Todos"] + sorted(list({a.get("genero") for a in dados_albuns if a.get("genero")})) if dados_albuns else ["Todos"]

with col_filtro1:
    subgenero_sel = st.selectbox("Filtrar por Subgênero:", subgeneros_disponiveis)

with col_filtro2:
    nota_sel = st.selectbox("Filtrar por Nota:", ["Todas", "10", "9+", "8+", "7+"])

albuns_filtrados = dados_albuns.copy() if dados_albuns else []

if subgenero_sel != "Todos":
    albuns_filtrados = [a for a in albuns_filtrados if a.get("genero") == subgenero_sel]

if nota_sel != "Todas":
    limite_nota = float(nota_sel.replace("+", ""))
    albuns_filtrados = [a for a in albuns_filtrados if float(a.get("nota", 0)) >= limite_nota]

# Exibição dos Álbuns
st.markdown("---")
st.subheader(f"📚 Álbuns Cadastrados ({len(albuns_filtrados)})")

if albuns_filtrados:
    cols = st.columns(2)
    for idx, album in enumerate(albuns_filtrados):
        col_atual = cols[idx % 2]
        with col_atual:
            st.markdown(f"""
            <div class="album-card">
                <div class="album-title">{album.get('nome', 'Sem título')}</div>
                <div class="album-info"><strong>Banda:</strong> {album.get('banda', 'N/A')} | <strong>Subgênero:</strong> {album.get('genero', 'N/A')}</div>
                <div class="album-rating">🔥 Nota: {album.get('nota', 'N/A')} / 10</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Nenhum álbum encontrado com os filtros selecionados.")

# ==========================================
# 5. PAINEL DE ADMINISTRAÇÃO (Na Barra Lateral)
# ==========================================
st.sidebar.title("⚙️ Painel de Controlo")
st.sidebar.write("Área exclusiva do administrador.")

senha_admin = st.sidebar.text_input("Senha de acesso:", type="password")
SENHA_CORRETA = "Atheusts123"

if senha_admin == SENHA_CORRETA:
    st.sidebar.success("Modo de Administração Ativo!")
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ Adicionar Novo Álbum")
    
    with st.sidebar.form("form_novo_album", clear_on_submit=True):
        nome_input = st.text_input("Nome do Álbum")
        banda_input = st.text_input("Banda / Artista")
        genero_input = st.text_input("Subgênero (ex: Thrash Metal)")
        nota_input = st.slider("Nota", min_value=1.0, max_value=10.0, value=10.0, step=0.5)
        
        btn_salvar = st.form_submit_button("Guardar no Supabase")
        
        if btn_salvar:
            if nome_input and banda_input:
                novo_registro = {
                    "nome": nome_input,
                    "banda": banda_input,
                    "genero": genero_input,
                    "nota": nota_input
                }
                try:
                    supabase.table("albuns").insert(novo_registro).execute()
                    st.sidebar.success(f"'{nome_input}' salvo com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.sidebar.error(f"Erro ao salvar: {err}")
            else:
                st.sidebar.warning("Preencha ao menos o Nome e a Banda.")

elif senha_admin:
    st.sidebar.error("Senha incorreta.")
