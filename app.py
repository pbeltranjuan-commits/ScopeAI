import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time

# Configuración de la IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="ScopeAI", layout="wide")

# --- SISTEMA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Acceso a ScopeAI")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
    
    with tab1:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            st.session_state.autenticado = True
            st.rerun()
    
    with tab2:
        st.info("Introduce tus datos para registrarte")
        nuevo_usuario = st.text_input("Nuevo Usuario")
        nueva_clave = st.text_input("Nueva Contraseña", type="password")
        if st.button("Registrarme"):
            st.success("Cuenta creada correctamente. Ya puedes iniciar sesión.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.title("ScopeAI")

# 1. CARGA DE INVENTARIO (EXCEL)
with st.sidebar:
    st.header("Configuración de Datos")
    excel_file = st.file_uploader("Subir inventario de precios (Excel)", type=['xlsx'])
    inventario_text = ""
    if excel_file:
        df = pd.read_excel(excel_file)
        inventario_text = df.to_string()
        st.success("Inventario cargado con éxito")

# 2. FORMULARIO DE MEDIDAS (OPCIONAL)
st.subheader("Datos de la avería")
mides = st.text_area("Formulario de medidas y desperfectos (Opcional)", 
                     placeholder="Ejemplo: Tubería de 15mm cortada, 3 metros de daño...")

# 3. SUBIDA DE VÍDEO Y PROCESAMIENTO
archivo = st.file_uploader("Subir vídeo de la avería", type=['mp4', 'mov'])

if archivo is not None:
    if st.button("Generar Factura y Presupuesto"):
        with st.spinner("La IA está analizando el vídeo y consultando precios..."):
            # Guardar vídeo temporal
            with open("temp_video.mp4", "wb") as f:
                f.write(archivo.getbuffer())
            
            video_up = genai.upload_file(path="temp_video.mp4")
            while video_up.state.name == "PROCESSING":
                time.sleep(2)
                video_up = genai.get_file(video_up.name)

            # PROMPT (Vídeo + Excel + Formulario + Internet)
            prompt = f"""
            ACTÚA COMO UN PERITO EXPERTO.
            Analiza el vídeo y los datos adjuntos para generar un presupuesto detallado.
            
            DATOS ADICIONALES: {mides}
            INVENTARIO DEL CLIENTE: {inventario_text}
            
            INSTRUCCIONES:
            1. Identifica materiales y el tipo de avería.
            2. Si el material existe en el INVENTARIO DEL CLIENTE, usa ese precio obligatoriamente.
            3. Si NO está en el inventario, busca en internet o usa precios de mercado actuales.
            4. ESTRUCTURA DEL PRESUPUESTO:
               - Descripción de los daños.
               - Desglose de materiales (Unidades/Metros y Precio).
               - Mano de obra: 60€ visita + 45€/h.
               - IVA (21%).
            Responde de forma profesional en ESPAÑOL.
            """

            respuesta = model.generate_content([prompt, video_up])
            resultado_final = respuesta.text
            
            st.markdown("### Resultado del Análisis")
            st.write(resultado_final)

            # 4. GENERACIÓN DE PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="PRESUPUESTO PROFESIONAL - ScopeAI", ln=1, align='C')
            pdf.ln(10)
            
            # Limpiar texto para que el PDF no falle con caracteres raros
            texto_pdf = resultado_final.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=texto_pdf)
            
            nombre_pdf = "presupuesto_scopeai.pdf"
            pdf.output(nombre_pdf)
            
            with open(nombre_pdf, "rb") as f:
                st.download_button("📥 Descargar Presupuesto en PDF", f, file_name="Presupuesto_ScopeAI.pdf")
