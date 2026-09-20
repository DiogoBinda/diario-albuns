import sqlite3
import streamlit as st

# 1. Configuração da Base de Dados SQLite
def init_db():
    conn = sqlite3.connect("albuns.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS albuns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL,
            ano INTEGER,
            nota INTEGER,
            comentario TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 2. Interface do Utilizador (Streamlit)
st.title("🎵 O Meu Diário de Álbuns")
st.write("Registe, avalie e edite os álbuns que ouve, com notas de 1 a 5 estrelas e comentários.")

# Barra lateral para adicionar novos álbuns
st.sidebar.header("Adicionar Novo Álbum")
with st.sidebar.form("form_album", clear_on_submit=True):
    titulo = st.text_input("Título do Álbum")
    artista = st.text_input("Artista")
    ano = st.number_input("Ano de Lançamento", min_value=1900, max_value=2030, value=2026)
    nota = st.slider("Nota (Estrelas)", min_value=1, max_value=5, value=5)
    comentario = st.text_area("Comentário / Resenha")
    
    submitted = st.form_submit_button("Guardar Álbum")
    
    if submitted:
        if titulo and artista:
            conn = sqlite3.connect("albuns.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO albuns (titulo, artista, ano, nota, comentario) VALUES (?, ?, ?, ?, ?)",
                           (titulo, artista, ano, nota, comentario))
            conn.commit()
            conn.close()
            st.sidebar.success(f"Álbum '{titulo}' guardado com sucesso!")
            st.rerun()
        else:
            st.sidebar.error("Por favor, preencha pelo menos o título e o artista.")

# 3. Listagem e Edição dos Álbuns Guardados
st.header("Os Seus Álbuns Avaliados")

conn = sqlite3.connect("albuns.db")
cursor = conn.cursor()
cursor.execute("SELECT id, titulo, artista, ano, nota, comentario FROM albuns ORDER BY id DESC")
albuns = cursor.fetchall()
conn.close()

if not albuns:
    st.info("Ainda não tem álbuns registados. Adicione o primeiro na barra lateral!")
else:
    for album in albuns:
        album_id, titulo, artista, ano, nota, comentario = album
        
        with st.container():
            col1, col2, col3 = st.columns([2.5, 1, 1])
            with col1:
                st.subheader(f"*{titulo}* — {artista} ({ano})")
                estrelas = "⭐" * nota
                st.markdown(f"**Avaliação:** {estrelas} ({nota}/5)")
                if comentario:
                    st.write(f"*{comentario}*")
            with col2:
                # Botão para ativar a edição deste álbum específico
                if st.button("✏️ Editar", key=f"edit_btn_{album_id}"):
                    st.session_state[f"editando_{album_id}"] = True
            with col3:
                # Botão para apagar o álbum
                if st.button("🗑️ Apagar", key=f"del_{album_id}"):
                    conn = sqlite3.connect("albuns.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM albuns WHERE id = ?", (album_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()

            # Se o botão de editar foi clicado, mostra o formulário de alteração para este álbum
            if st.session_state.get(f"editando_{album_id}", False):
                with st.form(key=f"form_edit_{album_id}"):
                    st.write(f"### A editar: {titulo}")
                    novo_titulo = st.text_input("Novo Título", value=titulo)
                    novo_artista = st.text_input("Novo Artista", value=artista)
                    novo_ano = st.number_input("Novo Ano", min_value=1900, max_value=2030, value=int(ano))
                    nova_nota = st.slider("Nova Nota", min_value=1, max_value=5, value=int(nota), key=f"slider_{album_id}")
                    novo_comentario = st.text_area("Novo Comentário", value=comentario if comentario else "")
                    
                    col_salvar, col_cancelar = st.columns(2)
                    with col_salvar:
                        salvar_edicao = st.form_submit_button("💾 Salvar Alterações")
                    with col_cancelar:
                        cancelar_edicao = st.form_submit_button("❌ Cancelar")
                    
                    if salvar_edicao:
                        conn = sqlite3.connect("albuns.db")
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE albuns 
                            SET titulo = ?, artista = ?, ano = ?, nota = ?, comentario = ? 
                            WHERE id = ?
                        """, (novo_titulo, novo_artista, novo_ano, nova_nota, novo_comentario, album_id))
                        conn.commit()
                        conn.close()
                        st.session_state[f"editando_{album_id}"] = False
                        st.success("Álbum atualizado com sucesso!")
                        st.rerun()
                        
                    if cancelar_edicao:
                        st.session_state[f"editando_{album_id}"] = False
                        st.rerun()

            st.divider()