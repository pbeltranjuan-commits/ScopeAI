import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# 1. Configuración de API (Se mantiene igual)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Technical", layout="wide")
st.title("ScopeAI")

# --- SISTEMA DE ACCESO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    u = st.text_input("Usuario")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- BARRA LATERAL (Configuración de precios) ---
with st.sidebar:
    st.header("Configuración")
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario cargado."
    
    st.markdown("---")
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

# --- PANEL CENTRAL ---
st.subheader("Datos")
notas = st.text_area("Información técnica / Observaciones adicionales")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info(f"Archivo listo: {archivo.name}")
    
    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Ingeniería en marcha: Calculando y buscando enlaces externos..."):
            try:
                # 2. Gestión de archivo para móvil
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # Subida a Google
                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # 3. EL PROMPT REFORZADO (La clave de los materiales y links)
                # Usamos 1.5 Pro porque es el más "obediente" con búsquedas
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                prompt = f"""
                ERES UN INGENIERO TÉCNICO Y PERITO ESPECIALISTA EN INSTALACIONES.
                
                TAREA 1: Identificación Visual.
                Analiza el archivo adjunto. Identifica materiales dañados, medidas y patologías.
                
                TAREA 2: Memoria de Ingeniería.
                Aplica fórmulas reales (Bernoulli, Darcy-Weisbach, cálculo de caudales o transmitancia térmica). 
                RESULTADOS DISCRECIONALES, NO PROBABILÍSTICOS.
                
                TAREA 3: Presupuesto y Búsqueda de Materiales (OBLIGATORIA).
                - Paso 1: Busca precios en este Inventario Excel: {inv_data}
                - Paso 2: SI EL MATERIAL NO ESTÁ EN EL EXCEL, es OBLIGATORIO navegar por internet (Leroy Merlin, Amazon España, Bricomart, etc.).
                - Paso 3: Para cada material de sustitución, indica: NOMBRE, PRECIO DE MERCADO y LINK directo de compra.
                
                FORMATO DEL PRESUPUESTO FINAL:
                - Visita y Desplazamiento: {c_visita}€
                - Mano de Obra: {c_hora}€/h x [Horas estimadas]
                - Materiales: [Lista detallada con PRECIOS y LINKS]
                - Total con 21% IVA.

                IDIOMA: ESPAÑOL. SE TÉCNICO Y RIGUROSO.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("### Informe de Ingeniería y Presupuesto")
                    st.markdown(respuesta.text)
                    
                    # 4. Generación de PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    # Limpieza de caracteres para el PDF
                    txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=txt_pdf)
                    pdf.output("Informe_ScopeAI.pdf")
                    with open("Informe_ScopeAI.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe con Enlaces", f, file_name="Informe_ScopeAI.pdf")

                # Limpieza final
                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
