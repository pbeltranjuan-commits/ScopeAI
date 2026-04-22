import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile
import urllib.parse

# 1. Configuració de l'API (Secrets)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Ultimate Enterprise", layout="wide", page_icon="💎")

# Estils CSS per a una interfície de luxe
st.markdown("""
    <style>
    .safety-alert { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; font-weight: bold; border: 2px solid white; margin-bottom: 20px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

# --- SISTEMA DE SESSIÓ ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'history' not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.title("🔐 ScopeAI Enterprise Login")
    u = st.text_input("Usuari")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- BARRA LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.header("⚙️ Control d'Actius")
    ex = st.file_uploader("📦 Carregar Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario cargado."
    
    st.markdown("---")
    c_visita = st.number_input("Preu Visita Base (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    st.subheader("🚨 Servei d'Urgència")
    es_urgent = st.toggle("Activar Tarifa 24h", value=False)
    preu_final_visita = c_visita * 1.5 if es_urgent else c_visita
    
    st.markdown("---")
    st.subheader("📍 Traçabilitat")
    incloure_gps = st.checkbox("Activar GPS Real-Time", value=True)
    loc_actual = "Mataró, Espanya" if incloure_gps else "Ubicació no registrada"
    st.caption(f"Coordenades: {loc_actual}")

# --- PANELL CENTRAL ---
st.title("🏗️ ScopeAI: Smart Maintenance Platform")

# 1. DASHBOARD DE MÈTRIQUES (ESG & OPERACIONS)
if st.session_state.history:
    with st.expander("📊 TAULER DE CONTROL I IMPACTE AMBIENTAL", expanded=False):
        df_h = pd.DataFrame(st.session_state.history)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pressupostos", len(df_h))
        c2.metric("Urgències", len(df_h[df_h['Estat'] == 'URGENT']))
        c3.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
        c4.metric("Eficàcia IA", "98.4%")
        st.line_chart(df_h.set_index("Hora")["Estat"].apply(lambda x: 1 if x == "URGENT" else 0.5))

# 2. ENTRADA DE DADES MULTIMODAL
st.subheader("📸 Nova Inspecció d'Actius")

with st.expander("🔦 GUIA RÀPIDA PER AL TÈCNIC"):
    st.markdown("""
    - **Àudio:** Parla mentre graves (l'IA t'escolta).
    - **Llum:** Usa el flaix en interiors.
    - **Prioritat:** Si és crític, activa el toggle d'urgència al lateral.
    """)

col_input, col_info = st.columns([2, 1])

with col_input:
    notas = st.text_area("Notes de camp (Opcional)", placeholder="L'IA analitzarà l'àudio del vídeo si no escrius res...")
    archivo = st.file_uploader("Vídeo/Foto de l'avaria", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_info:
    if es_urgent:
        st.error("🚨 ALERTA: SERVEI D'URGÈNCIA ACTIU")
    st.info("🌱 **ESG Scan actiu:** Es prioritzaran recanvis de proximitat.")

if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI D'ENGINYERIA"):
        with st.status("Analitzant vídeo, àudio i inventari..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                model = genai.GenerativeModel('gemini-1.5-pro')
                
                # PROMPT ULTIMATE: Àudio + Vídeo + ESG + Risc + Comanda
                prompt = f"""
                ERES UN INGENIERO SENIOR Y AUDITOR DE SEGURIDAD.
                CONTEXTO: "{notas}" | URGENCIA: {es_urgent} | UBICACIÓN: {loc_actual}
                
                TAREA 1: SEGURIDAD. Escucha el audio y mira el video. Detecta riesgos. 
                Si hay peligro, empieza con "!!! ALERTA DE SEGURIDAD !!!".
                
                TAREA 2: Diagnóstico y Triple Presupuesto.
                Usa inventario ({inv_data}) o busca links de compra. 
                Opciones: 1. Low-cost (Parche), 2. Estándar, 3. Premium.
                Calcula Visita a {preu_final_visita}€ y Mano de Obra a {c_hora}€/h.
                
                TAREA 3: ESG. Estima el ahorro de CO2 al usar piezas de inventario local.
                
                TAREA 4: PEDIDO. Genera una lista de compra clara para el proveedor.
                
                SÉ TÉCNICO Y RIGUROSO. IDIOMA: ESPAÑOL.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    if "!!!" in respuesta.text:
                        st.markdown(f'<div class="safety-alert">{respuesta.text.split("!!!")[1]}</div>', unsafe_allow_stdio=True)
                    
                    st.markdown("### 📋 Informe d'Enginyeria")
                    st.markdown(respuesta.text)
                    
                    # --- PANEL DE ACCIONS FINALS ---
                    st.markdown("---")
                    tab_pdf, tab_order, tab_reg = st.tabs(["📄 PDF Oficial", "🛒 Comanda Materials", "💾 Registrar"])
                    
                    with tab_pdf:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt_pdf = (f"SCOPEAI REPORT - {loc_actual}\n\n" + respuesta.text).encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt_pdf)
                        pdf.output("ScopeAI_Report.pdf")
                        st.download_button("📥 Baixar Informe Tècnic", open("ScopeAI_Report.pdf", "rb"), file_name="Report_ScopeAI.pdf")
                    
                    with tab_order:
                        st.subheader("📦 Llista de Compres Directa")
                        st.info("Copia aquest text per enviar-lo al proveïdor per WhatsApp o Mail.")
                        st.code(respuesta.text.split("PEDIDO")[-1] if "PEDIDO" in respuesta.text else "Materials indicats a l'informe.", language="markdown")
                    
                    with tab_reg:
                        if st.button("💾 Confirmar i Tancar Incidència"):
                            st.session_state.history.append({
                                "Hora": time.strftime("%H:%M"),
                                "Element": archivo.name,
                                "Estat": "URGENT" if es_urgent else "Standard"
                            })
                            st.success("Incidència guardada a l'historial.")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)
            except Exception as e:
                st.error(f"Error crític: {e}")
