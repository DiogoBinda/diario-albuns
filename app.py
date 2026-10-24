import streamlit as st
from supabase import create_client

# Configuração da página
st.set_page_config(
    page_title="Diário de Álbuns", page_icon="🎵", layout="wide"
)

# Inicializar cliente Supabase (usando st.secrets)
@st.cache_resource
def init_supabase():
  url = st.secrets["supabase"]["url"]
  key = st.secrets["supabase"]["key"]
  return create_client(url, key)


supabase = init_supabase()

# Título principal
st.markdown("<h1>🎵 Diário de Álbuns</h1>", unsafe_allow_html=True)
st.write("Catálogo público de álbuns, avaliações e comentários")

# Formulário na barra lateral
st.sidebar.markdown("### Novo Registo")
with st.sidebar.form("form_album", clear_on_submit=True):
  nome_album = st.text_input("Nome/Título do Álbum")
  banda_artista = st.text_input("Banda/Artista")
  genero = st.text_input("Gênero/Estilo")
  nota = st.number_input("Nota", min_value=0.0, max_value=10.0, step=0.5)
  comentario = st.text_area("Comentário / Resenha")

  submit_button = st.form_submit_button("Salvar")

  if submit_button:
    if not nome_album or not banda_artista:
      st.error("Por favor, preencha o nome do álbum e da banda/artista.")
    else:
      try:
        # AQUI ESTÁ A CORREÇÃO: Usar 'artista' em vez de 'banda'
        dados = {
            "album": nome_album,
            "artista": banda_artista,
            "categoria": genero,
            "nota": nota,
            "comentario": comentario,
        }
        supabase.table("albums").insert(dados).execute()
        st.success("Álbum salvo com sucesso!")
        st.rerun()
      except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# Buscar dados da tabela 'albums'
try:
  response = supabase.table("albums").select("*").execute()
  dados_albuns = response.data
except Exception as e:
  st.error(f"Erro ao carregar dados: {e}")
  dados_albuns = []

# Métricas no topo
total_albuns = len(dados_albuns)
if total_albuns > 0:
  media_notas = sum(item.get("nota", 0) for item in dados_albuns) / total_albuns
else:
  media_notas = 0.0

col1, col2 = st.columns(2)
with col1:
  st.metric("Total de Álbuns", total_albuns)
with col2:
  st.metric("Média de Notas", f"{media_notas:.1f}")

st.markdown("---")

# Tabela de Coleção de Álbuns
st.markdown("### 📚 Coleção de Álbuns")
if dados_albuns:
  st.dataframe(dados_albuns, use_container_width=True)
else:
  st.info("Ainda não existem álbuns registados.")

# Seção de Resenhas e Comentários
st.markdown("### 💬 Resenhas e Comentários")
for item in dados_albuns:
  est_nota = item.get("nota", 0)
  est_album = item.get("album", "Sem título")
  est_artista = item.get("artista", "Desconhecido")
  est_comentario = item.get("comentario", "")

  with st.expander(f"⭐ {est_nota}/10 — {est_album} ({est_artista})"):
    st.write(
        f"**Comentário:** {est_comentario if est_comentario else 'Sem comentário.'}"
    )
