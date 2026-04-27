import streamlit as st
import pandas as pd
from sqlalchemy import text

def carregar_historial_sql(usuari):
    """Llegeix l'historial des de Supabase de forma segura."""
    try:
        conn = st.connection("postgresql", type="sql")
        # Fem una consulta neta i segura
        query = text("SELECT data, hora, tipus, cost_estimat FROM inspeccions WHERE usuari = :u ORDER BY id DESC LIMIT 20")
        
        with conn.session as session:
            result = session.execute(query, {"u": usuari})
            df = pd.DataFrame(result.fetchall(), columns=["Data", "Hora", "Tipus", "Cost Estimats (€)"])
            
            if df.empty:
                return []
            return df.to_dict('records')
    except Exception as e:
        # Això ens ajudarà a saber què falla exactament
        st.sidebar.error(f"Error llegint base dades: {e}")
        return []

def guardar_inspeccio_sql(usuari, tipus, cost):
    """Guarda una nova fila a la taula 'inspeccions' de Supabase."""
    try:
        conn = st.connection("postgresql", type="sql")
        with conn.session as session:
            # Preparem la consulta d'inserció
            query = text("""
                INSERT INTO inspeccions (usuari, tipus, cost_estimat) 
                VALUES (:u, :t, :c)
            """)
            session.execute(query, {"u": usuari, "t": tipus, "c": cost})
            session.commit()
        return True
    except Exception as e:
        st.error(f"Error guardant a base de dades: {e}")
        return False
