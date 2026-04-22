import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# Configuración de API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Technical", layout="wide")
st.title("ScopeAI")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("Usuario") and st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuración")
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else ""
    st.markdown("---")
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

# --- ENTRADA ---
st.subheader("Datos")
notas = st.text_area("Información técnica / Observaciones")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Ingeniería en marcha: Calculando y buscando enlaces..."):
            try:
                # 1. Proceso de subida robusto
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # 2. EL MODELO Y EL PROMPT (Ahora con enlaces)
                # Usamos gemini-2.0-flash que es el mejor navegando
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""
                ERES UN INGENIERO DE INSTALACIONES Y PERITO JUDICIAL.
                
                TAREA 1: Identifica materiales y daños mediante visión artificial.
                TAREA 2: Aplica FÓRMULAS DE INGENIERÍA (caudal, presiones, secciones) para justificar la reparación.
                TAREA 3: BÚSQUEDA DE MATERIALES.
                   - Si el material NO está en este Excel: {inv_data}
                   - DEBES buscar en internet el precio actual en España.
                   - ES OBLIGATORIO añadir el LINK (URL) del producto (Leroy Merlin, Amazon, etc.).
                
                ESTRUCTURA DEL INFORME:
                - Memoria Técnica (Cálculos y Fórmulas).
                - Presupuesto desglosado:
                    * Visita: {c_visita}€
                    * Mano de obra: {c_hora}€/h
                    * Materiales: [Nombre] - [Precio] - [LINK AL PRODUCTO]
                - TOTAL con IVA 21%.

                IDIOMA: ESPAÑOL. SÉ DETERMINISTA.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("### Informe de Ingeniería y Presupuesto")
                    st.markdown(respuesta.text)
                    
                    # 3. PDF (Nota: los links en PDF a veces son texto plano, pero se copian)
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=txt_pdf)
                    pdf.output("informe_links.pdf")
                    with open("informe_links.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe con Enlaces", f, file_name="ScopeAI_Final.pdf")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error: {str(e)}")
