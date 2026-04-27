import streamlit as st
import pandas as pd

def carregar_historial_sql(usuari):
    try:
        # Intentem connectar
        conn = st.connection("postgresql", type="sql")
        query = f"SELECT data, hora, tipus, cost_estimat FROM inspeccions WHERE usuari = '{usuari}' ORDER BY id DESC LIMIT 20;"
        df = conn.query(query, ttl=0)
        return df.to_dict('records')
    except Exception as e:
        # SI AIXÒ SURT A L'APP, COPIA'M L'ERROR:
        st.error(f"🔴 Error de lectura SQL: {e}")
        return []

def guardar_inspeccio_sql(usuari, tipus, cost):
    try:
        conn = st.connection("postgresql", type="sql")
        with conn.session as s:
            query = "INSERT INTO inspeccions (usuari, tipus, cost_estimat) VALUES (:u, :t, :c);"
            s.execute(query, {"u": usuari, "t": tipus, "c": cost})
            s.commit()
        return True
    except Exception as e:
        st.error(f"🔴 Error de guardat SQL: {e}")
        return False
