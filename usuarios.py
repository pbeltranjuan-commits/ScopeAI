import streamlit as st
import pandas as pd
from datetime import date
import os

DB_USERS = "usuarios_db.csv"

def inicializar_db():
    """Crea la base de dades si no existeix amb les columnes necessàries."""
    if not os.path.exists(DB_USERS):
        df = pd.DataFrame(columns=['usuario', 'password', 'ip', 'ultimo_uso_gratis'])
        df.to_csv(DB_USERS, index=False)

def get_remote_ip():
    """Obté la IP de l'usuari per evitar multi-comptes per xarxa."""
    from streamlit.web.server.websocket_headers import _get_websocket_headers
    headers = _get_websocket_headers()
    return headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]

def gestionar_sesion():
    """Gestiona el Login i el Registre d'usuaris."""
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
                if new_u in df['usuario'].astype(str).values:
                    st.error("Aquest nom d'usuari ja existeix.")
                else:
                    new_row = {'usuario': new_u, 'password': new_p, 'ip': current_ip, 'ultimo_uso_gratis': ""}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DB_USERS, index=False)
                    st.success("Compte creat! Ja pots iniciar sessió.")
        st.stop()

def verificar_cuota():
    """
    Comprova si l'usuari ja ha gastat el crèdit avui.
    Retorna True si pot analitzar gratis, False si ha de pagar.
    """
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    
    # Busquem la fila de l'usuari loguejat
    user_data = df[df['usuario'] == st.session_state.user]
    
    if user_data.empty:
        return False
    
    # Netegem la dada de la data per evitar errors de format
    ultimo_uso = str(user_data.iloc[0]['ultimo_uso_gratis']).strip()
    
    if ultimo_uso == hoy:
        return False  # BLOQUEJA: Ja ha fet l'anàlisi d'avui
    return True  # PASSA: Encara no ha gastat el crèdit

def registrar_uso_gratis():
    """Registra la data d'avui com a últim ús per a l'usuari actual."""
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    
    # Busquem l'índex de l'usuari i actualitzem la seva data
    if st.session_state.user in df['usuario'].values:
        df.loc[df['usuario'] == st.session_state.user, 'ultimo_uso_gratis'] = hoy
        df.to_csv(DB_USERS, index=False)
