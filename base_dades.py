import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

def guardar_inspeccio_gsheets(usuari, tipus, cost):
    """Guarda les dades en un Google Sheet compartit."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Llegim les dades actuals
        existing_data = conn.read(worksheet="Logs", ttl=0)
        
        # Creem la nova fila
        nova_fila = pd.DataFrame([{
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Usuari": usuari,
            "Tipus": tipus,
            "Cost Estimats (€)": cost
        }])
        
        # Combinem i actualitzem
        updated_df = pd.concat([existing_data, nova_fila], ignore_index=True)
        conn.update(worksheet="Logs", data=updated_df)
        return True
    except Exception as e:
        st.error(f"Error de connexió amb la base de dades: {e}")
        return False