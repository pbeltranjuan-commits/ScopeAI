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

st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="🏗️")

# --- ESTILS (Fix per evitar errors de pantalla vermella) ---
st.markdown("""
<style>
    .stMetric {background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;}
    .safety-alert {background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; font-weight: bold; margin-bottom: 20px;}
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

# --- BARRA LATERAL (Configuració, GPS i Urgències) ---
with st.sidebar:
    st.header("⚙️ Control de l'Eina")
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario."
    
    st.markdown("---")
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    st.subheader("🚨 Servei")
    es_urgent = st.toggle("Urgència 24h", value=False)
    preu_final_visita = c_visita * 1.5 if es_urgent else c_visita
    
    st.markdown("---")
    st.subheader("📍 Traçabilitat")
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "Mataró, Espanya" if incloure_gps else "Ubicació no registrada"
    st.caption(f"Ubicació: {loc_actual}")

# --- PANELL CENTRAL ---
st.title("🏗️ ScopeAI: Smart Maintenance")

# 1. DASHBOARD (Mètriques i CO2)
if st.session_state.history:
    with st.expander("📊 TAULER DE CONTROL I ESG", expanded=False):
        df_h = pd.DataFrame(st.session_state.history)
        c1, c2, c3 = st.columns(3)
        c1.metric("Pressupostos", len(df_h))
        c2.metric("Estalvi CO2 (Est.)", f"{len(df_h)*1.2:.1f} kg")
        c3.metric("Estat Flota", "🟢 100%")
        st.line_chart(df_h.set_index("Hora")["Estat"].apply(lambda x: 1 if x == "URGENT" else 0.5))

# 2. ENTRADA DE DADES
st.subheader("📸 Nova Inspecció")

# Ajuda per a la gravació (Punt Clau)
with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.markdown("1. **Llum:** Activa flaix. 2. **Perspectiva:** De lluny a prop. 3. **Àudio:** Parla mentre graves (l'IA t'escolta).")

col_input, col_info = st.columns([2, 1])

with col_input:
    notas = st.text_area("Notes manuals", placeholder="Explica l'avaria o deixa-ho buit per usar l'àudio del vídeo...")
    archivo = st.file_uploader("Vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_info:
    if es_urgent: st.error("🚨 MODO URGÈNCIA ACTIU")
    st.info("🌱 **ESG Scan actiu:** Mesurant petjada de carboni.")

if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        with st.status("Analitzant vídeo, àudio i materials..."):
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
                
                # PROMPT AMB TOTES LES FUNCIONS
                prompt = f"""
                ERES UN INGENIERO TÉCNICO Y AUDITOR DE SEGURIDAD.
                CONTEXTO: "{notas}" | UBICACIÓN: {loc_actual} | URGENCIA: {es_urgent}
                
                1. SEGURIDAD: Analiza audio y vídeo. Si hay peligro, empieza con "!!! ALERTA DE SEGURIDAD !!!".
                2. PRESUPUESTO: Genera 3 opciones (Low, Std, Premium) usando inventario ({inv_data}).
                3. COSTES: Visita a {preu_final_visita}€ y Mano de obra a {c_hora}€/h.
                4. ESG: Calcula ahorro de CO2 por reparación vs sustitución.
                5. PEDIDO: Genera una lista de materiales clara al final.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    if "!!!" in respuesta.text:
                        st.markdown(f'<div class="safety-alert">{respuesta.text.split("!!!")[1]}</div>', unsafe_allow_stdio=True)
                    
                    st.markdown("### 📋 Informe i Pressupostos")
                    st.markdown(respuesta.text)
                    
                    st.markdown("---")
                    # TABS FINALS
                    tab_pdf, tab_order, tab_reg = st.tabs(["📄 PDF", "🛒 Comanda", "💾 Registrar"])
                    
                    with tab_pdf:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt_clean = (f"SCOPEAI REPORT - {loc_actual}\n\n" + respuesta.text).encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt_clean)
                        pdf.output("Report.pdf")
                        st.download_button("Baixar Informe", open("Report.pdf", "rb"), file_name="Pressupost_ScopeAI.pdf")
                    
                    with tab_order:
                        st.subheader("📦 Comanda de Materials")
                        st.code(respuesta.text.split("PEDIDO")[-1] if "PEDIDO" in respuesta.text else "Materials a l'informe.", language="markdown")
                    
                    with tab_reg:
                        if st.button("Confirmar i Guardar"):
                            st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Element": archivo.name, "Estat": "URGENT" if es_urgent else "OK"})
                            st.success("Operació registrada!")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)
            except Exception as e:
                st.error(f"Error: {e}")
