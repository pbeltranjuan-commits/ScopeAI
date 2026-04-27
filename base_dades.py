import streamlit as st
import pandas as pd

def carregar_historial_sql(usuari):
    """Llegeix les últimes 20 inspeccions de la base de dades SQL."""
    try:
        # Utilitza la connexió 'postgresql' que hem configurat als Secrets
        conn = st.connection("postgresql", type="sql")
        
        # Fem la consulta a la taula que vas crear a Supabase
        query = f"SELECT data, hora, tipus, cost_estimat FROM inspeccions WHERE usuari = '{usuari}' ORDER BY id DESC LIMIT 20;"
        df = conn.query(query, ttl=0) # ttl=0 per tenir dades fresques sempre
        
        return df.to_dict('records')
    except Exception as e:
        # Si falla, retornem una llista buida perquè l'app no es trenqui
        return []

def guardar_inspeccio_sql(usuari, tipus, cost):
    """Guarda una nova inspecció a la base de dades eterna de Supabase."""
    try:
        conn = st.connection("postgresql", type="sql")
        with conn.session as s:
            # Preparem la inserció de dades
            query = "INSERT INTO inspeccions (usuari, tipus, cost_estimat) VALUES (:u, :t, :c);"
            s.execute(query, {"u": usuari, "t": tipus, "c": cost})
            s.commit()
        return True
    except Exception as e:
        st.error(f"❌ Error crític al guardar a SQL: {e}")
        return False
