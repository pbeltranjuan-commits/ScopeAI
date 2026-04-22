import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os

# Configuración de API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Technical", layout="wide")
st.title("ScopeAI: Ingeniería y Peritaje")

# --- LOGIN SIMPLIFICADO ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    u = st.text_input("Usuario")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- SIDEBAR: EXCEL Y CONFIGURACIÓN ---
with st.sidebar:
    st.header("Configuración Técnica")
    ex = st.file_uploader("Subir Inventario Precios (Excel)", type=['xlsx'])
    inv_data = ""
    if ex:
        df = pd.read_excel(ex)
        inv_data = df.to_string()
        st.success("Inventario cargado")
    
    st.markdown("---")
    st.header("Costes de Mano de Obra")
    coste_visita = st.number_input("Precio Visita (€)", value=60.0)
    coste_hora = st.number_input("Precio Hora (€)", value=45.0)

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datos de entrada")
    notas = st.text_area("Descripción técnica / Medidas", placeholder="Ej: Tubo de cobre 15mm, presión 3 bar...")
    video = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png'])

with col2:
    if video:
        st.video(video)
        if st.button("EJECUTAR CÁLCULOS DE INGENIERÍA"):
            with st.status("Procesando cálculos deterministas..."):
                try:
                    # Guardar temporal
                    with open("temp_file", "wb") as f:
                        f.write(video.getbuffer())
                    
                    # Subir a Gemini
                    v_up = genai.upload_file(path="temp_file")
                    while v_up.state.name == "PROCESSING":
                        time.sleep(2)
                        v_up = genai.get_file(v_up.name)

                    # PROMPT TÉCNICO DE INGENIERÍA
                    model = genai.GenerativeModel('gemini-1.5-pro') # Usamos Pro para cálculos complejos
                    prompt = f"""
                    Eres un Ingeniero de Instalaciones y Perito. 
                    Analiza el archivo y los datos: {notas}.
                    
                    TAREAS:
                    1. IDENTIFICACIÓN DETERMINISTA: No especules. Identifica materiales y dimensiones.
                    2. FÓRMULAS DE INGENIERÍA: Aplica fórmulas reales (Hazen-Williams para pérdidas de carga, Darcy-Weisbach, o cálculo de caudales $$Q = A \cdot v$$). Muestra las fórmulas usadas.
                    3. BÚSQUEDA DE PRECIOS: Usa este inventario: {inv_data}. Si algo no está, busca en internet el precio actual.
                    4. PRESUPUESTO MANO DE OBRA: Usa Visita: {coste_visita}€ y Hora: {coste_hora}€.
                    
                    ESTRUCTURA DE RESPUESTA:
                    - Memoria Técnica (Fórmulas y Cálculos).
                    - Desglose de Materiales.
                    - Presupuesto Final (Base, IVA 21%, Total).
                    
                    RESPONDE EN ESPAÑOL TÉCNICO.
                    """
                    
                    res = model.generate_content([prompt, v_up])
                    st.markdown("---")
                    st.markdown(res.text)
                    
                    # PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    pdf.cell(200, 10, txt="INFORME TÉCNICO Y PRESUPUESTO - ScopeAI", ln=1, align='C')
                    clean_text = res.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=clean_text)
                    pdf.output("informe.pdf")
                    
                    with open("informe.pdf", "rb") as f:
                        st.download_button("Descargar Informe PDF", f, file_name="Informe_Tecnico.pdf")

                except Exception as e:
                    st.error(f"Error en el motor: {str(e)}")
