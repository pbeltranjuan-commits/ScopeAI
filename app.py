import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import tempfile
import os

# Configuración de seguridad
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI", layout="wide")

# --- SISTEMA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Acceso")
    tab1, tab2 = st.tabs(["Entrar", "Nuevo Registro"])
    with tab1:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Acceder"):
            st.session_state.autenticado = True
            st.rerun()
    with tab2:
        st.text_input("Nombre")
        st.text_input("Email")
        st.text_input("Crear Contraseña", type="password")
        if st.button("Crear Cuenta"):
            st.success("Cuenta creada.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.title("ScopeAI")

with st.sidebar:
    st.header("Configuración")
    excel_file = st.file_uploader("Subir Inventario (Excel)", type=['xlsx'])
    inventario_text = ""
    if excel_file:
        df = pd.read_excel(excel_file)
        inventario_text = df.to_string()
        st.success("Excel cargado")

# CAMBIO SOLICITADO: Solo "Datos"
st.subheader("Datos")
mides = st.text_area("Información adicional (Opcional)", placeholder="Introduce aquí medidas, materiales o detalles...")

archivo = st.file_uploader("Subir vídeo", type=['mp4', 'mov', 'avi'])

if archivo is not None:
    st.video(archivo)
    
    if st.button("Procesar"):
        with st.spinner("Analizando..."):
            try:
                # 1. Gestión del archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # 2. Subida a Google
                video_up = genai.upload_file(path=temp_path)
                while video_up.state.name == "PROCESSING":
                    time.sleep(2)
                    video_up = genai.get_file(video_up.name)

                # 3. Lógica de IA (Flash y Pro)
                modelos = ['gemini-1.5-flash', 'gemini-1.5-pro']
                respuesta_ia = None
                
                prompt = f"""
                ACTÚA COMO UN PERITO EXPERTO. Genera un presupuesto profesional.
                DATOS ADICIONALES: {mides}
                INVENTARIO: {inventario_text}
                
                REGLAS:
                1. Identifica daños y materiales en el vídeo.
                2. USA PRECIOS DEL INVENTARIO si existen. Si no, busca precios de mercado.
                3. TARIFAS: 60€ visita + 45€/h + Materiales + 21% IVA.
                4. Idioma: ESPAÑOL.
                """

                for m_name in modelos:
                    try:
                        model = genai.GenerativeModel(m_name)
                        respuesta_ia = model.generate_content([prompt, video_up])
                        if respuesta_ia: break
                    except:
                        continue

                if respuesta_ia:
                    st.markdown("### Resultado")
                    st.write(respuesta_ia.text)

                    # 4. Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt="PRESUPUESTO - ScopeAI", ln=1, align='C')
                    pdf.ln(10)
                    texto_limpio = respuesta_ia.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, txt=texto_limpio)
                    
                    pdf_file = "presupuesto.pdf"
                    pdf.output(pdf_file)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Descargar PDF", f, file_name="Presupuesto.pdf")
                
                os.unlink(temp_path) # Borrar temporal

            except Exception as e:
                st.error(f"Error: {e}")
