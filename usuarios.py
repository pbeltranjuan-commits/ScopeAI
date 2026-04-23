import streamlit as st
import pandas as pd
from datetime import date
import os

DB_USERS = "usuarios_db.csv"

def inicializar_db():
    if not os.path.exists(DB_USERS):
        df = pd.DataFrame(columns=['usuario', 'password', 'ip', 'ultimo_uso_gratis'])
        df.to_csv(DB_USERS, index=False)

def gestionar_sesion():
    inicializar_db()
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("🔐 Accés ScopeAI")
        u = st.text_input("Usuari")
        p = st.text_input("Contrasenya", type="password")
        if st.button("Entrar"):
            df = pd.read_csv(DB_USERS)
            user_data = df[(df['usuario'] == u) & (df['password'] == p)]
            if not user_data.empty:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Dades incorrectes")
        st.stop()

def verificar_cuota():
    """Retorna True si pot anar gratis, False si ha de pagar."""
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    user_row = df[df['usuario'] == st.session_state.user]
    
    if user_row.empty: return False
    
    ultimo_uso = str(user_row.iloc[0]['ultimo_uso_gratis']).strip()
    return ultimo_uso != hoy

def registrar_uso_gratis():
    """Marca que l'usuari ja ha gastat el seu crèdit d'avui."""
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    df.loc[df['usuario'] == st.session_state.user, 'ultimo_uso_gratis'] = hoy
    df.to_csv(DB_USERS, index=False)
    st.cache_data.clear()
