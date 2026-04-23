# usuarios.py
import streamlit as st
import pandas as pd
from datetime import date
import os

DB_USERS = "usuarios_db.csv"

def inicializar_db():
    if not os.path.exists(DB_USERS):
        df = pd.DataFrame(columns=['usuario', 'password', 'ip', 'ultimo_uso_gratis'])
        df.to_csv(DB_USERS, index=False)

def get_remote_ip():
    from streamlit.web.server.websocket_headers import _get_websocket_headers
    headers = _get_websocket_headers()
    return headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]

def gestionar_sesion():
    inicializar_db()
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.title("🔐 Accés ScopeAI")
        tab1, tab2 = st.tabs(["Entrar", "Registrar-se"])
        with tab1:
            u = st.text_input("Usuari", key="login_u")
            p = st.text_input("Contrasenya", type="password", key="login_p")
            if st.button("Iniciar Sessió"):
                df = pd.read_csv(DB_USERS)
                user_data = df[(df['usuario'] == u) & (df['password'] == p)]
                if not user_data.empty:
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Usuari o contrasenya incorrectes")
        with tab2:
            new_u = st.text_input("Nou Usuari", key="reg_u")
            new_p = st.text_input("Nova Contrasenya", type="password", key="reg_p")
            if st.button("Crear Compte"):
                df = pd.read_csv(DB_USERS)
                current_ip = get_remote_ip()
                if current_ip in df['ip'].astype(str).values and current_ip != "127.0.0.1":
                    st.error("Ja existeix un compte vinculat a aquesta IP.")
                elif new_u in df['usuario'].astype(str).values:
                    st.error("Aquest nom d'usuari ja està agafat.")
                else:
                    new_row = {'usuario': new_u, 'password': new_p, 'ip': current_ip, 'ultimo_uso_gratis': ""}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DB_USERS, index=False)
                    st.success("Compte creat correctament!")
        st.stop()

# --- AQUÍ ESTÀ EL CANVI IMPORTANT ---
def verificar_cuota():
    # Forcem la lectura del fitxer cada vegada que algú prem el botó
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    
    user_row = df[df['usuario'] == st.session_state.user]
    if user_row.empty:
        return False
        
    # Agafem la dada i la convertim a text per comparar-la bé
    ultimo_uso = str(user_row.iloc[0]['ultimo_uso_gratis'])
    
    if ultimo_uso == hoy:
        return False  # BLOQUEJAT: Ja ha gastat el gratis d'avui
    return True  # OK: Pot fer l'anàlisi gratis

def registrar_uso_gratis():
    df = pd.read_csv(DB_USERS)
    idx = df[df['usuario'] == st.session_state.user].index[0]
    df.at[idx, 'ultimo_uso_gratis'] = str(date.today())
    df.to_csv(DB_USERS, index=False)
