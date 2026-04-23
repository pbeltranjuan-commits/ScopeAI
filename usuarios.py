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
        tab1, tab2 = st.tabs(["Entrar", "Registrar-se"])
        with tab1:
            u = st.text_input("Usuari", key="l_u")
            p = st.text_input("Contrasenya", type="password", key="l_p")
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
            new_u = st.text_input("Nou Usuari", key="r_u")
            new_p = st.text_input("Nova Contrasenya", type="password", key="r_p")
            if st.button("Crear Compte"):
                df = pd.read_csv(DB_USERS)
                if new_u in df['usuario'].astype(str).values:
                    st.error("L'usuari ja existeix.")
                else:
                    new_row = {'usuario': new_u, 'password': new_p, 'ip': "0.0.0.0", 'ultimo_uso_gratis': ""}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DB_USERS, index=False)
                    st.success("Compte creat! Ja pots entrar.")
        st.stop()

def verificar_cuota():
    # Forcem lectura neta del CSV
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    user_row = df[df['usuario'] == st.session_state.user]
    
    if user_row.empty:
        return False
        
    ultimo_uso = str(user_row.iloc[0]['ultimo_uso_gratis']).strip()
    # Si la data guardada és igual a la d'avui, retorna False (BLOQUEJAT)
    return ultimo_uso != hoy

def registrar_uso_gratis():
    df = pd.read_csv(DB_USERS)
    hoy = str(date.today())
    df.loc[df['usuario'] == st.session_state.user, 'ultimo_uso_gratis'] = hoy
    df.to_csv(DB_USERS, index=False)
    st.cache_data.clear()
