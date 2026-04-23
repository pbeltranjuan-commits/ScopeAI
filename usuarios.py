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
    # Obté la IP per evitar que un sol usuari creï mil comptes
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
                # Bloqueig per IP: Només un compte per connexió
                if current_ip in df['ip'].astype(str).values and current_ip != "127.0.0.1":
                    st.error("Ja existeix un compte vinculat a aquesta IP.")
                elif new_u in df['usuario'].astype(str).values:
                    st.error("Aquest nom d'usuari ja està agafat.")
                else:
                    new_row = {'usuario': new_u, 'password': new_p, 'ip': current_ip, 'ultimo_uso_gratis': ""}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DB_USERS, index=False)
                    st.success("Compte creat correctament! Ja pots entrar.")
        st.stop()

def verificar_cuota():
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    idx = df[df['usuario'] == st.session_state.user].index[0]
    
    # Comprova si la data de l'últim ús gratis és avui
    if str(df.at[idx, 'ultimo_uso_gratis']) == hoy:
        return False # No té gratis, ha de pagar
    return True # Té l'ús gratis de 24h disponible

def registrar_uso_gratis():
    df = pd.read_csv(DB_USERS)
    idx = df[df['usuario'] == st.session_state.user].index[0]
    df.at[idx, 'ultimo_uso_gratis'] = str(date.today())
    df.to_csv(DB_USERS, index=False)