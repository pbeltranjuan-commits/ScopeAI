import streamlit as st
import pandas as pd

def mostrar_dashboard_premium(historial):
    """Genera les mètriques i el gràfic d'evolució des del SQL."""
    if not historial:
        st.info("Esperant dades per generar estadístiques...")
        return

    # 1. PREPARACIÓ DE DADES
    df = pd.DataFrame(historial)
    
    # Assegurem que el cost sigui numèric
    col_cost = "Cost Estimats (€)"
    if col_cost in df.columns:
        df[col_cost] = pd.to_numeric(df[col_cost], errors='coerce').fillna(0)
    else:
        # Si la columna té un altre nom per error, la creem buida per no petar
        df[col_cost] = 0.0

    # 2. CÀLCUL DE MÈTRIQUES
    total_inspeccions = len(df)
    facturacio_total = df[col_cost].sum()
    mitjana_ticket = facturacio_total / total_inspeccions if total_inspeccions > 0 else 0
    
    # 3. DISSENY DE TARGETES (KPIs)
    st.markdown("### 📈 Panell de Rendiment")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(label="Inspeccions Totals", value=total_inspeccions, delta="Historial actiu")
    with c2:
        st.metric(label="Volum de Negoci", value=f"{facturacio_total:,.2f} €", delta="Estimació ROI")
    with c3:
        st.metric(label="Ticket Mitjà", value=f"{mitjana_ticket:,.2f} €")

    # 4. GRÀFIC D'EVOLUCIÓ (L'historial visual)
    st.markdown("#### 📅 Evolució de la Facturació")
    
    # Invertim l'ordre per al gràfic (de més vell a més nou)
    df_chart = df.iloc[::-1].reset_index()
    
    # Gràfic d'àrea professional
    st.area_chart(df_chart[col_cost], use_container_width=True)

    # 5. DISTRIBUCIÓ PER TIPUS (Mecànica vs Elèctrica)
    if "Tipus" in df.columns:
        with st.expander("🔍 Veure distribució per avaria"):
            distribucio = df["Tipus"].value_counts()
            st.bar_chart(distribucio)
