import streamlit as st
import pandas as pd

def mostrar_historial_detallat(historial):
    """Crea una taula visualment atractiva amb l'historial de SQL."""
    st.subheader("📋 Registre d'Inspeccions")
    
    if not historial:
        st.info("Encara no hi ha cap inspecció registrada a la base de dades.")
        return

    # Convertim la llista de diccionaris a un DataFrame de Pandas
    df = pd.DataFrame(historial)
    
    # Posem icones segons el tipus d'avaria
    def aplicar_icona(tipus):
        if "Mecànica" in tipus: return "⚙️ Mecànica"
        if "Elèctrica" in tipus: return "⚡ Elèctrica"
        return f"🔍 {tipus}"

    df['Tipus'] = df['Tipus'].apply(aplicar_icona)
    
    # Estilitzem la taula
    st.dataframe(
        df,
        column_config={
            "Data": st.column_config.TextColumn("📅 Data"),
            "Hora": st.column_config.TextColumn("🕒 Hora"),
            "Tipus": st.column_config.TextColumn("🏷️ Categoria"),
            "Cost Estimats (€)": st.column_config.NumberColumn("💰 Cost Est.", format="%.2f €"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Botó per netejar la vista (opcional)
    if st.button("🗑️ Refrescar llista"):
        st.rerun()