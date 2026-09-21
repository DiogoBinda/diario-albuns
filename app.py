import streamlit as st
from supabase import create_client

# --- CONFIGURAÇÃO DE SEGURANÇA E SUPABASE ---
SENHA_MESTRE = st.secrets.get("SENHA_MESTRE", "sua_senha_padrao")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


# Inicializar o cliente do Supabase
@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()


# Função para verificar a autenticação
def check_password():
  def password_entered():
    if st.session_state["password"] == SENHA_MESTRE:
      st.session_state["password_correct"] = True
      del st.session_state["password"]
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    st.title("🔒 Diário de Álbuns - Acesso Restrito")
    st.text_input(
        "Introduza a senha de acesso:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    return False
  elif not st.session_state["password_correct"]:
    st.title("🔒 Diário de Álbuns - Acesso Restrito")
    st.text_input(
        "Introduza a senha de acesso:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    st.error("😕 Senha incorreta. Tente novamente.")
    return False
  else:
    return True


if not check_password():
  st.stop()

# --- APLICAÇÃO PRINCIPAL ---
st.title("🎸 Diário de Álbuns de Metal (Nuvem)")
st.write(
    "Gerencie, filtre por subgénero e avalie os seus álbuns favoritos de 1 a"
    " 10 com dados guardados na nuvem."
)

# Lista de subgéneros de metal
subgeneros_metal = [
    "Heavy Metal",
    "Thrash Metal",
    "Death Metal",
    "Black Metal",
    "Power Metal",
    "Doom Metal",
    "Progressive Metal",
    "Metalcore / Deathcore",
    "Folk / Viking Metal",
    "Outro",
]

# Menu lateral
menu = st.sidebar.selectbox(
    "Navegação", ["Ver / Filtrar Álbuns", "Adicionar Álbum", "Gerir / Editar"]
)

if menu == "Ver / Filtrar Álbuns":
  st.subheader("📚 Meus Registos e Filtros Avançados")

  st.markdown("### 🔍 Filtrar Catálogo")
  col_f1, col_f2 = st.columns(2)

  with col_f1:
    filtro_cat = st.selectbox(
        "Filtrar por Subgénero:", ["Todos"] + subgeneros_metal
    )

  with col_f2:
    filtro_nota = st.selectbox(
        "Filtrar por Nota:",
        ["Todas", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"],
    )

  # Construir consulta ao Supabase
  query = supabase.table("albuns").select("*")

  if filtro_cat != "Todos":
    query = query.eq("categoria", filtro_cat)

  if filtro_nota != "Todas":
    query = query.eq("nota", int(filtro_nota))

  response = query.execute()
  dados = response.data

  st.divider()

  if dados:
    st.write(f"A mostrar **{len(dados)}** álbuns encontrados:")
    for item in dados:
      artista = item.get("artista")
      album = item.get("album")
      categoria = item.get("categoria")
      nota = item.get("nota")
      comentario = item.get("comentario")

      cat_texto = f"[{categoria}]" if categoria else "[Sem Categoria]"
      nota_val = nota if nota else "?"
      with st.expander(
          f"{cat_texto} {artista} - {album}  |  Nota: {nota_val}/10"
      ):
        st.write(f"**Subgénero:** {categoria}")
        st.write(f"**Classificação:** {nota_val}/10")
        st.write(f"**Comentário:** {comentario}")
  else:
    st.info("Nenhum álbum encontrado com os filtros selecionados.")

elif menu == "Adicionar Álbum":
  st.subheader("➕ Adicionar Novo Álbum de Metal")

  with st.form("form_adicionar"):
    artista = st.text_input("Artista / Banda")
    album = st.text_input("Nome do Álbum")
    categoria = st.selectbox("Subgénero de Metal", subgeneros_metal)
    nota = st.slider("Nota (1 a 10)", 1, 10, 8)
    comentario = st.text_area("Comentário / Análise")
    submit = st.form_submit_button("Guardar Álbum")

    if submit:
      if artista and album:
        # Inserir no Supabase
        supabase.table("albuns").insert({
            "artista": artista,
            "album": album,
            "categoria": categoria,
            "nota": nota,
            "comentario": comentario,
        }).execute()
        st.success(f"Álbum '{album}' guardado com sucesso na nuvem!")
      else:
        st.warning("Por favor, preencha pelo menos o artista e o álbum.")

elif menu == "Gerir / Editar":
  st.subheader("⚙️ Editar ou Apagar Registos")

  response = supabase.table("albuns").select("id, artista, album").execute()
  registos = response.data

  if registos:
    opcoes = {
        f"{item['artista']} - {item['album']} (ID: {item['id']})": item["id"]
        for item in registos
    }
    escolha = st.selectbox("Selecione o álbum para gerir:", list(opcoes.keys()))
    id_selecionado = opcoes[escolha]

    res_detalhe = (
        supabase.table("albuns")
        .select("*")
        .eq("id", id_selecionado)
        .execute()
    )
    if res_detalhe.data:
      item_atual = res_detalhe.data[0]
      art_atual = item_atual.get("artista")
      alb_atual = item_atual.get("album")
      cat_atual = item_atual.get("categoria")
      nota_atual = item_atual.get("nota")
      com_atual = item_atual.get("comentario")

      cat_index = (
          subgeneros_metal.index(cat_atual)
          if cat_atual in subgeneros_metal
          else 0
      )
      nota_atual_val = int(nota_atual) if nota_atual else 8
      nota_index = min(max(nota_atual_val, 1), 10)

      with st.form("form_editar"):
        novo_artista = st.text_input("Artista / Banda", value=art_atual)
        novo_album = st.text_input("Nome do Álbum", value=alb_atual)
        nova_categoria = st.selectbox(
            "Subgénero de Metal", subgeneros_metal, index=cat_index
        )
        nova_nota = st.slider("Nota (1 a 10)", 1, 10, value=nota_index)
        novo_comentario = st.text_area(
            "Comentário / Análise", value=com_atual if com_atual else ""
        )

        col1, col2 = st.columns(2)
        atualizar = col1.form_submit_button("Atualizar Álbum")
        apagar = col2.form_submit_button("Apagar Álbum")

        if atualizar:
          supabase.table("albuns").update({
              "artista": novo_artista,
              "album": novo_album,
              "categoria": nova_categoria,
              "nota": nova_nota,
              "comentario": novo_comentario,
          }).eq("id", id_selecionado).execute()
          st.success("Álbum atualizado com sucesso na nuvem!")
        elif apagar:
          supabase.table("albuns").delete().eq(
              "id", id_selecionado
          ).execute()
          st.success("Álbum apagado com sucesso da nuvem!")
  else:
    st.info("Não há álbuns para gerir.")
