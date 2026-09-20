import sqlite3
import streamlit as st

# --- CONFIGURAÇÃO DE SEGURANÇA ---
SENHA_MESTRE = st.secrets.get("SENHA_MESTRE", "sua_senha_padrao")


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
st.title("🎸 Diário de Álbuns de Metal")
st.write(
    "Gerencie o seu registo pessoal de álbuns e subgéneros de metal favoritos."
)

# Conexão à Base de Dados SQLite
conn = sqlite3.connect("albuns.db", check_same_thread=False)
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS albuns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artista TEXT NOT NULL,
        album TEXT NOT NULL,
        categoria TEXT,
        nota INTEGER,
        comentario TEXT
    )
""")
conn.commit()

# Garantir compatibilidade caso a base de dados antiga não tenha a coluna categoria
try:
  cursor.execute("ALTER TABLE albuns ADD COLUMN categoria TEXT")
  conn.commit()
except sqlite3.OperationalError:
  pass  # A coluna já existe

# Lista de subgéneros de metal para escolher
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
    "Navegação", ["Ver Álbuns", "Adicionar Álbum", "Gerir / Editar"]
)

if menu == "Ver Álbuns":
  st.subheader("📚 Meus Registos de Metal")

  # Filtro por categoria na visualização
  filtro_cat = st.selectbox(
      "Filtrar por Subgénero:", ["Todos"] + subgeneros_metal
  )

  if filtro_cat == "Todos":
    cursor.execute(
        "SELECT artista, album, categoria, nota, comentario FROM albuns"
    )
  else:
    cursor.execute(
        "SELECT artista, album, categoria, nota, comentario FROM albuns WHERE"
        " categoria = ?",
        (filtro_cat,),
    )

  dados = cursor.fetchall()

  if dados:
    for artista, album, categoria, nota, comentario in dados:
      cat_texto = f"[{categoria}]" if categoria else "[Sem Categoria]"
      with st.expander(f"{cat_texto} {artista} - {album} (Nota: {nota}/10)"):
        st.write(f"**Subgénero:** {categoria}")
        st.write(f"**Comentário:** {comentario}")
  else:
    st.info("Ainda não existem álbuns registados com este filtro.")

elif menu == "Adicionar Álbum":
  st.subheader("➕ Adicionar Novo Álbum de Metal")

  with st.form("form_adicionar"):
    artista = st.text_input("Artista / Banda")
    album = st.text_input("Nome do Álbum")
    categoria = st.selectbox("Subgénero de Metal", subgeneros_metal)
    nota = st.slider("Nota", 1, 10, 8)
    comentario = st.text_area("Comentário / Análise")
    submit = st.form_submit_button("Guardar Álbum")

    if submit:
      if artista and album:
        cursor.execute(
            "INSERT INTO albuns (artista, album, categoria, nota, comentario)"
            " VALUES (?, ?, ?, ?, ?)",
            (artista, album, categoria, nota, comentario),
        )
        conn.commit()
        st.success(f"Álbum '{album}' guardado com sucesso!")
      else:
        st.warning("Por favor, preencha pelo menos o artista e o álbum.")

elif menu == "Gerir / Editar":
  st.subheader("⚙️ Editar ou Apagar Registos")
  cursor.execute("SELECT id, artista, album FROM albuns")
  registos = cursor.fetchall()

  if registos:
    opcoes = {f"{art} - {alb} (ID: {id_})": id_ for id_, art, alb in registos}
    escolha = st.selectbox("Selecione o álbum para gerir:", list(opcoes.keys()))
    id_selecionado = opcoes[escolha]

    cursor.execute(
        "SELECT artista, album, categoria, nota, comentario FROM albuns WHERE id"
        " = ?",
        (id_selecionado,),
    )
    art_atual, alb_atual, cat_atual, nota_atual, com_atual = cursor.fetchone()

    # Descobrir o índice atual do selectbox
    cat_index = (
        subgeneros_metal.index(cat_atual)
        if cat_atual in subgeneros_metal
        else 0
    )

    with st.form("form_editar"):
      novo_artista = st.text_input("Artista / Banda", value=art_atual)
      novo_album = st.text_input("Nome do Álbum", value=alb_atual)
      nova_categoria = st.selectbox(
          "Subgénero de Metal", subgeneros_metal, index=cat_index
      )
      nova_nota = st.slider("Nota", 1, 10, value=int(nota_atual))
      novo_comentario = st.text_area(
          "Comentário / Análise", value=com_atual if com_atual else ""
      )

      col1, col2 = st.columns(2)
      atualizar = col1.form_submit_button("Atualizar Álbum")
      apagar = col2.form_submit_button("Apagar Álbum")

      if atualizar:
        cursor.execute(
            "UPDATE albuns SET artista = ?, album = ?, categoria = ?, nota = ?,"
            " comentario = ? WHERE id = ?",
            (
                novo_artista,
                novo_album,
                nova_categoria,
                nova_nota,
                novo_comentario,
                id_selecionado,
            ),
        )
        conn.commit()
        st.success("Álbum atualizado com sucesso!")
      elif apagar:
        cursor.execute("DELETE FROM albuns WHERE id = ?", (id_selecionado,))
        conn.commit()
        st.success("Álbum apagado com sucesso!")
  else:
    st.info("Não há álbuns para gerir.")
