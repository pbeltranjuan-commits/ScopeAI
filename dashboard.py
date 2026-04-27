import streamlit as st
import pandas as pd

def mostrar_dashboard_premium(historial):
    if not historial:
        st.info("📊 Encara no hi ha dades per mostrar al Dashboard.")
        return

    # Convertim l'historial en un DataFrame per treballar millor
    df = pd.DataFrame(historial)

    # --- MÈTRIQUES DE CAPÇALERA ---
    st.markdown("### 📈 Rendiment Operatiu")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Total Inspeccions", len(df))
    with c2:
        # Calculem estalvi estimat de CO2 (ex: 1.2kg per inspecció evitada)
        total_co2 = len(df) * 1.2
        st.metric("Estalvi CO2", f"{total_co2:.1f} kg", delta="♻️ Sostenible")
    with c3:
        # Simulació de temps estalviat
        temps_total = len(df) * 45 # 45 minuts per cada una
        st.metric("Temps Guanyat", f"{temps_total//60}h {temps_total%60}m")
    with c4:
        st.metric("Estat Flota", "🟢 100%", delta="OPTIMAL")

    st.markdown("---")

    # --- GRÀFIQUES MODULARS ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("**EVOLUCIÓ DE COSTOS (€)**")
        # Gràfica lineal simple (Streamlit native per mantenir el look clean)
        chart_data = pd.DataFrame({
            "Inspecció": range(1, len(df) + 1),
            "Cost Estimat": [150, 220, 180, 250, 210][:len(df)] # Exemple
        })
        st.line_chart(chart_data.set_index("Inspecció"), color="#18181B")

    with col_right:
        st.write("**DISTRIBUCIÓ D'AVARIES**")
        # Gràfica de barres de tipus d'avaria
        tipus_data = pd.DataFrame({
            "Tipus": ["Elèctrica", "Mecànica", "Estructura", "Altres"],
            "Casos": [5, 3, 2, 1]
        })
        st.bar_chart(tipus_data.set_index("Tipus"), color="#3F3F46")