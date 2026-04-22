import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# 1. CONFIGURACIÓ DE L'API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Config de pàgina (Això SEMPRE ha de ser la primera línia de codi)
st.set_page_config(page_title="ScopeAI Ultimate 2026", layout="wide", page_icon="💎")

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

# --- BARRA LATERAL (Amb selector de models de Gemini) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    
    # Aquí tens el que deies: Triar el "cervell" de Gemini
    model_triat = st.selectbox(
        "🧠 Model de Gemini",
        ["gemini-1.5-pro", "gemini-1.5-flash"],
        help="Pro: Màxima intel·ligència. Flash: Màxima velocitat."
    )
    
    st.markdown("---")
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "Sense inventari."
    
    st.markdown("---")
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    # GPS (Foto 3)
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "📍 Carrer de la Riera, Mataró" if incloure_gps else "Ubicació Manual"
    st.caption(f"Localització: {loc_actual}")
    
    st.markdown("---")
    # Urgència
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- PANELL CENTRAL ---
st.title("🏗️ ScopeAI: Smart Engineering")

# 1. DASHBOARD (Foto 2)
if st.session_state.history:
    st.markdown("### 📊 Dashboard d'Estat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pressupostos", len(df_h))
    c2.metric("Estalvi CO2 (ESG)", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 100%")
    st.line_chart(df_h.set_index("Hora")["Estat"].apply(lambda x: 1))

# 2. NOVA INSPECCIÓ I AJUDA (Foto 1)
st.subheader("📸 Captura d'Avaria")

with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.write("1. **Llum:** Activa el flaix. 2. **Zoom:** Apropa't al nus. 3. **Àudio:** Parla mentre graves.")

col_main, col_side = st.columns([2, 1])

with col_main:
    notas = st.text_area("Notes manuals", placeholder="Descriu l'avaria o deixa que l'IA escolti el vídeo...")
    archivo = st.file_uploader("Vídeo o Foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_side:
    if es_urgent: st.error("MODO URGÈNCIA: ON")
    st.info(f"Cervell actiu: **{model_triat}**")

if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI AMB GEMINI"):
        with st.status(f"Analitzant amb {model_triat}..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Utilitzem el model seleccionat a la sidebar
                model = genai.GenerativeModel(model_triat)
                
                prompt = f"""
                ERES UN INGENIERO EXPERTO. UBICACIÓN: {loc_actual} | NOTAS: {notas}
                1. SEGURIDAD: Si hay peligro, avisa con "!!! ALERTA DE SEGURIDAD !!!".
                2. DIAGNÓSTICO: Analiza video/audio y crea presupuesto triple usando {inv_data}.
                3. COSTES: Visita {p_final_visita}€, Mano obra {c_hora}€/h.
                4. ESG: Ahorro CO2. 5. PEDIDO: Lista materiales para proveedor.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    if "!!!" in respuesta.text:
                        st.warning(f"⚠️ {respuesta.text.split('!!!')[1]}")
                    
                    st.markdown("### 📋 Resultat de l'Anàlisi")
                    st.markdown(respuesta.text)
                    
                    st.markdown("---")
                    t_pdf, t_reg = st.tabs(["📄 PDF", "💾 Guardar"])
                    with t_pdf:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt = (f"REPORT {loc_actual}\n\n" + respuesta.text).encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt)
                        pdf.output("Report.pdf")
                        st.download_button("Baixar PDF", open("Report.pdf", "rb"), file_name="Informe.pdf")
                    with t_reg:
                        if st.button("Registrar al Dashboard"):
                            st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Estat": "OK"})
                            st.success("Guardat!")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)
            except Exception as e:
                st.error(f"Error: {e}")
