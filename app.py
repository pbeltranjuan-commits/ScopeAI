import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# Configuración de API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI", layout="wide")
st.title("ScopeAI")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("Usuario") and st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- CONFIGURACIÓN ---
with st.sidebar:
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else ""
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

st.subheader("Datos")
notas = st.text_area("Información técnica")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.success(f"Archivo detectado: {archivo.name}")
    
    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Subiendo y procesando... No cierres el navegador"):
            try:
                # 1. GUARDAR EN ARCHIVO TEMPORAL (Obligatorio para subida oficial)
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # 2. SUBIDA ASÍNCRONA (Método robusto para archivos grandes en móvil)
                st.write("Enviando archivo a Google...")
                file_uploaded = genai.upload_file(path=temp_path)
                
                # Esperar a que Google termine de procesar el video
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)
                
                if file_uploaded.state.name == "FAILED":
                    st.error("Error en el servidor de Google al procesar el vídeo.")
                    st.stop()

                # 3. LLAMADA AL MOTOR (Usamos 1.5 Flash por velocidad en móvil)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                ERES INGENIERO DE INSTALACIONES.
                DATOS TÉCNICOS: {notas}
                INVENTARIO: {inv_data}
                MANO OBRA: Visita {c_visita}€, Hora {c_hora}€.
                
                TAREA:
                - Identifica materiales y daños.
                - Aplica fórmulas de ingeniería (caudales, presiones) de forma DETERMINISTA.
                - Genera presupuesto final con IVA 21%.
                - RESPONDE EN ESPAÑOL.
                """

                st.write("Generando cálculos de ingeniería...")
                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("---")
                    st.markdown(respuesta.text)
                    
                    # 4. PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=txt_pdf)
                    pdf.output("informe.pdf")
                    with open("informe.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe", f, file_name="Informe_ScopeAI.pdf")

                # Limpieza
                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error: {str(e)}")
