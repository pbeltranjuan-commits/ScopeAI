import streamlit as st
import pandas as pd

def mostrar_dashboard_premium(historial):
    """Genera les targetes de resum a partir de les dades de SQL."""
    if not historial:
        return

    # Convertim l'historial (llista de dicts) en DataFrame
    df = pd.DataFrame(historial)

    # 1. Càlcul de mètriques
    total_inspeccions = len(df)
    
    # Sumem la columna de costos (ens assegurem que sigui numèrica)
    try:
        # El nom de la columna ha de coincidir amb el que retorna el SQL a base_dades.py
        col_cost = "Cost Estimats (€)"
        total_facturat = df[col_cost].astype(float).sum()
    except:
        total_facturat = 0.0

    # 2. Disseny visual amb columnes (Targetes)
    st.markdown("### 📈 Resum d'Activitat")
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric(
            label="Total Inspeccions", 
            value=total_inspeccions, 
            delta="Memòria SQL Activa",
            delta_color="normal"
        )
        
    with m2:
        st.metric(
            label="Facturació Estimada", 
            value=f"{total_facturat:,.2f} €",
            delta="Dades Reals",
            delta_color="normal"
        )
        
    with m3:
        # Càlcul de mitjana per inspecció
        mitjana = total_facturat / total_inspeccions if total_inspeccions > 0 else 0
        st.metric(
            label="Mitjana per Treball", 
            value=f"{mitjana:,.2f} €"
        )

    # 3. Gràfic ràpid d'evolució (Opcional)
    if total_inspeccions > 1:
        with st.expander("📊 Veure tendència"):
            # Preparem dades pel gràfic
            df_grafic = df.copy()
            df_grafic = df_grafic.sort_index(ascending=False) # Invertim perquè el gràfic vagi d'esquerra a dreta
            st.line_chart(df_grafic[col_cost])
