import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# Configuración API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Technical", layout="wide")
st.title("ScopeAI: Ingeniería y Peritaje")

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    u = st.text_input("Usuario")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- CONFIGURACIÓN TÉCNICA ---
with st.sidebar:
    st.header("Configuración")
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = ""
    if ex:
        inv_data = pd.read_excel(ex).to_string()
    
    st.markdown("---")
    coste_visita = st.number_input("Precio Visita (€)", value=60.0)
    coste_hora = st.number_input("Precio Hora (€)", value=45.0)

st.subheader("Datos")
notas = st.text_area("Descripción / Medidas", placeholder="Ej: Cálculo de caudal, tubería cobre 15mm...")
video = st.file_uploader("Subir archivo", type=['mp4', 'mov', 'jpg', 'png'])

if video:
    st.video(video)
    if st.button("EJECUTAR CÁLCULOS"):
        with st.status("Procesando cálculos discrecionales..."):
            try:
                # 1. Crear temporal con extensión correcta
                suffix = ".mp4" if "video" in video.type else ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(video.read())
                    temp_path = tfile.name

                # 2. Subir forzando el MIME TYPE (Esto arregla tu error)
                mime_type = video.type if video.type else "video/mp4"
                v_up = genai.upload_file(path=temp_path, mime_type=mime_type)
                
                while v_up.state.name == "PROCESSING":
                    time.sleep(2)
                    v_up = genai.get_file(v_up.name)

                # 3. Modelos (Prioridad al nuevo Gemini 2.0 Flash)
                modelos = ['gemini-2.0-flash', 'gemini-1.5-pro']
                respuesta = None

                prompt = f"""
                ACTÚA COMO INGENIERO EXPERTO. Resultados DISCRECIONALES (No probabilísticos).
                DATOS ADICIONALES: {notas}
                INVENTARIO: {inv_data}
                
                REGLAS DE CÁLCULO:
                1. IDENTIFICACIÓN: Usa el vídeo para determinar diámetros y materiales.
                2. FÓRMULAS: Aplica fórmulas de ingeniería (Bernoulli, Darcy-Weisbach, Hazen-Williams) para justificar mediciones.
                3. PRECIOS: Prioriza Excel. Si no existe, busca precios de mercado en tiempo real.
                4. MANO DE OBRA: Visita {coste_visita}€, Hora {coste_hora}€.
                
                ENTREGABLE: Memoria de cálculos + Presupuesto desglosado + IVA. ESPAÑOL.
                """

                for m_name in modelos:
                    try:
                        m = genai.GenerativeModel(m_name)
                        respuesta = m.generate_content([prompt, v_up])
                        if respuesta: break
                    except: continue

                if respuesta:
                    st.markdown("---")
                    st.markdown(respuesta.text)
                    
                    # PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    pdf.multi_cell(0, 5, txt=respuesta.text.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.output("informe.pdf")
                    with open("informe.pdf", "rb") as f:
                        st.download_button("📥 Informe PDF", f, file_name="ScopeAI_Informe.pdf")
                
                os.unlink(temp_path)

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
