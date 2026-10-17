import streamlit as st
# (importe aqui também as suas bibliotecas do Supabase, pandas, etc.)

# 1. Configuração da página (deve ser sempre a primeira instrução do Streamlit)
st.set_page_config(
    page_title="Heavy Metal Vault",
    page_icon="🤘",
    layout="wide"
)

# 2. Estilo Visual (Preto, Azul e Vermelho)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    h1, h2, h3 {
        color: #66fcf1 !important;
    }
    strong {
        color: #ff2e63 !important;
    }
    .stButton > button {
        background-color: #ff2e63 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1f2833 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ÁREA PÚBLICA (Visível para qualquer pessoa)
# ==========================================
st.title("🤘 Catálogo de Álbuns de Heavy Metal")
st.write("Explore a minha coleção de álbuns, notas e subgêneros.")

# Aqui coloca o seu código atual que puxa os dados do Supabase e mostra a tabela ou os cards
# Exemplo:
# dados_albuns = carregar_dados_do_supabase()
# st.dataframe(dados_albuns) # Ou a sua visualização personalizada


# ==========================================
# PAINEL DE ADMINISTRAÇÃO (Na Barra Lateral)
# ==========================================
st.sidebar.title("⚙️ Painel de Controlo")
st.sidebar.write("Apenas para o administrador.")

# Campo de senha isolado na barra lateral
senha_admin = st.sidebar.text_input("Senha de acesso:", type="password")

# Substitua "a_sua_senha" pela palavra-passe que desejar
if senha_admin == "a_sua_senha":
    st.sidebar.success("Modo de edição ativo!")
    
    st.sidebar.subheader("Adicionar Novo Álbum")
    # Os inputs e botões para inserir dados no Supabase ficam aqui dentro
    novo_disco = st.sidebar.text_input("Nome do Álbum")
    nova_banda = st.sidebar.text_input("Banda")
    
    if st.sidebar.button("Guardar no Supabase"):
        # O seu código para inserir no Supabase
        st.sidebar.success("Álbum guardado com sucesso!")
elif senha_admin:
    st.sidebar.error("Senha incorreta.")
