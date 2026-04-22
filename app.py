import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# 1. Configuración - Usamos el modelo que SABEMOS que te funciona
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_NAME = 'gemini-1.5-flash' 

st.set_page_config(page_title="ScopeAI", layout="wide")
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
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario."
    st.markdown("---")
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

# --- DATOS ---
st.subheader("Datos")
notas = st.text_area("Información técnica")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Calculando y buscando materiales..."):
            try:
                # Proceso de archivo para que Google no de error de Mime Type
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_up = genai.upload_file(path=temp_path)
                while file_up.state.name == "PROCESSING":
                    time.sleep(2)
                    file_up = genai.get_file(file_up.name)

                # EL PROMPT: Ingeniería + Búsqueda si no hay Excel + Links
                prompt = f"""
                ACTÚA COMO INGENIERO. 
                1. Usa fórmulas de ingeniería (Bernoulli, caudales) para el análisis.
                2. Busca materiales en este Excel: {inv_data}
                3. SI EL MATERIAL NO ESTÁ EN EL EXCEL, búscalo en internet (Leroy Merlin, Amazon, etc.).
                4. PARA CADA MATERIAL: Pon el nombre, el precio y el LINK directo de compra.
                5. PRESUPUESTO: Visita {c_visita}€ + {c_hora}€/h + Materiales + 21% IVA.
                
                IDIOMA: ESPAÑOL.
                """

                model = genai.GenerativeModel(MODEL_NAME)
                res = model.generate_content([prompt, file_up])
                
                if res.text:
                    st.markdown(res.text)
                    
                    # Generar PDF
                    pdf = FPDF()
                    pdf.add
