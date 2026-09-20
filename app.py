import sqlite3
import streamlit as st

# --- CONFIGURAÇÃO DE SEGURANÇA (Lida do cofre seguro do Streamlit Cloud) ---
# Certifique-se de configurar a variável SENHA_MESTRE nas "Secrets" do Streamlit Cloud.
SENHA_MESTRE = st.secrets.get("SENHA_MESTRE", "sua_senha_padrao")


# Função para verificar a autenticação
def check_password():
  def password_entered():
    if st.session_state["password"] == SENHA_MESTRE:
      st.session_state["password_correct"] = True
      del st.session_state["password"]  # Não guarda a senha na sessão por segurança
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    # Primeiro acesso: mostra a caixa de texto da senha
    st.title("🔒 Diário de Álbuns - Acesso Restrito")
    st.text_input(
        "Introduza a senha de acesso:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    return False
  elif not st.session_state["password_correct"]:
    # Senha errada
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
    # Senha correta
    return True


# Bloqueia a aplicação inteira se a senha estiver incorreta
if not check_password():
  st.stop()

# --- APLICAÇÃO PRINCIPAL (Só abre após inserir a senha correta) ---
st.title("🎵 Diário de Álbuns Musicais")
st.write(
    "Bem-vindo ao seu espaço pessoal de avaliação e registo de álbuns"
    " musicais."
)

# Conexão à Base de Dados SQLite local
conn = sqlite3.connect("albuns.db", check_same_thread=False)
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS albuns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artista TEXT NOT NULL,
        album TEXT NOT NULL,
        nota INTEGER,
        comentario TEXT
    )
""")
conn.commit()

# Menu lateral para navegação
menu = st.sidebar.selectbox(
    "Navegação", ["Ver Álbuns", "Adicionar Álbum", "Gerir / Editar"]
)

if menu == "Ver Álbuns":
  st.subheader("📚 Meus Registos")
  cursor.execute("SELECT artista, album, nota, comentario FROM albuns")
  dados = cursor.fetchall()

  if dados:
    for artista, album, nota, comentario in dados:
      with st.expander(f"{artista} - {album} (Nota: {nota}/10)"):
        st.write(f"**Comentário:** {comentario}")
  else:
    st.info("Ainda não existem álbuns registados.")

elif menu == "Adicionar Álbum":
  st.subheader("➕ Adicionar Novo Álbum")

  with st.form("form_adicionar"):
    artista = st.text_input("Artista / Banda")
    album = st.text_input("Nome do Álbum")
    nota = st.slider("Nota", 1, 10, 7)
    comentario = st.text_area("Comentário / Análise")
    submit = st.form_submit_button("Guardar Álbum")

    if submit:
      if artista and album:
        cursor.execute(
            "INSERT INTO albuns (artista, album, nota, comentario) VALUES"
            " (?, ?, ?, ?)",
            (artista, album, nota, comentario),
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

    # Buscar dados atuais do álbum selecionado
    cursor.execute(
        "SELECT artista, album, nota, comentario FROM albuns WHERE id = ?",
        (id_selecionado,),
    )
    art_atual, alb_atual, nota_atual, com_atual = cursor.fetchone()

    with st.form("form_editar"):
      novo_artista = st.text_input("Artista / Banda", value=art_atual)
      novo_album = st.text_input("Nome do Álbum", value=alb_atual)
      nova_nota = st.slider("Nota", 1, 10, value=int(nota_atual))
      novo_comentario = st.text_area(
          "Comentário / Análise", value=com_atual if com_atual else ""
      )

      col1, col2 = st.columns(2)
      atualizar = col1.form_submit_button("Atualizar Álbum")
      apagar = col2.form_submit_button("Apagar Álbum")

      if atualizar:
        cursor.execute(
            "UPDATE albuns SET artista = ?, album = ?, nota = ?, comentario = ?"
            " WHERE id = ?",
            (
                novo_artista,
                novo_album,
                nova_nota,
                novo_comentario,
                id_selecionado,
            ),
        )
        conn.commit()
        st.success("Álbum atualizado com sucesso! Atualize a página para ver.")
      elif apagar:
        cursor.execute("DELETE FROM albuns WHERE id = ?", (id_selecionado,))
        conn.commit()
        st.success("Álbum apagado com sucesso! Atualize a página para ver.")
  else:
    st.info("Não há álbuns para gerir.")
