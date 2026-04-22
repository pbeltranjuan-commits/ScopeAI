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
        with st.status("Ingeniería y búsqueda de enlaces en marcha..."):
            try:
                # 1. Proceso de subida robusto para móvil
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # 2. PROMPT REFORZADO CON BÚSQUEDA EXTERNA Y LINKS
                # Usamos el motor 2.0 Flash o 1.5 Pro para máxima capacidad de búsqueda
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                prompt = f"""
                ERES UN INGENIERO TÉCNICO Y PERITO JUDICIAL ESPECIALISTA EN REFORMAS.
                
                TAREA 1: Identificación Visual.
                Analiza el archivo adjunto. Identifica materiales dañados y dimensiones.
                
                TAREA 2: Memoria de Ingeniería.
                Usa fórmulas reales (Bernoulli para fluidos, Darcy-Weisbach para pérdidas de presión, o cálculos de transmitancia térmica si es una ventana). 
                DAME RESULTADOS DISCRECIONALES, NO PROBABILÍSTICOS.
                
                TAREA 3: Presupuesto y Búsqueda de Materiales (CRÍTICO).
                - Busca precios en este Excel: {inv_data}
                - SI EL MATERIAL NO ESTÁ EN EL EXCEL: Es OBLIGATORIO que navegues por internet y encuentres el precio de mercado actual en España (Leroy Merlin, Bricomart, Amazon, etc.).
                - PARA CADA MATERIAL: Incluye obligatoriamente el NOMBRE, PRECIO y el LINK directo al producto.
                
                DESGLOSE FINAL:
                - Visita y Desplazamiento: {c_visita}€
                - Mano de Obra: {c_hora}€/h x [Horas calculadas]
                - Materiales: [Lista con nombres, precios y LINKS]
                - Total con 21% IVA.

                IDIOMA: ESPAÑOL. RESPONDE CON RIGOR TÉCNICO.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("### Informe Técnico con Enlaces")
                    st.markdown(respuesta.text)
                    
                    # 3. Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    # Limpiamos el texto para el PDF
                    txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=txt_pdf)
                    pdf.output("ScopeAI_Final.pdf")
                    with open("ScopeAI_Final.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe con Enlaces", f, file_name="ScopeAI_Final.pdf")

                # Limpieza de archivos en el servidor y en Google
                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
