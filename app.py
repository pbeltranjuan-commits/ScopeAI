import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import tempfile
import os

# Configuración de seguridad desde Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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
            st.success("Cuenta creada. Ya puedes iniciar sesión.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.title("ScopeAI")

with st.sidebar:
    st.header("Configuración")
    excel_file = st.file_uploader("Subir inventario de precios (Excel)", type=['xlsx'])
    inventario_text = ""
    if excel_file:
        df = pd.read_excel(excel_file)
        inventario_text = df.to_string()
        st.success("Inventario cargado")

st.subheader("Datos de la avería")
mides = st.text_area("Formulario de medidas y desperfectos (Opcional)")

archivo = st.file_uploader("Subir vídeo de la avería", type=['mp4', 'mov', 'avi'])

if archivo is not None:
    st.video(archivo)
    
    if st.button("Generar Factura y Presupuesto"):
        with st.spinner("Procesando vídeo... Esto puede tardar 1-2 minutos."):
            try:
                # 1. Crear archivo temporal para evitar errores de subida
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # 2. Subir a Google
                video_up = genai.upload_file(path=temp_path)
                while video_up.state.name == "PROCESSING":
                    time.sleep(3)
                    video_up = genai.get_file(video_up.name)

                # 3. LÓGICA DE MODELOS (Si uno falla, prueba el otro)
                modelos_a_probar = ['gemini-1.5-flash', 'gemini-1.5-pro']
                respuesta_ia = None
                error_acumulado = ""

                prompt = f"""
                ACTÚA COMO UN PERITO EXPERTO. Analiza el vídeo y genera un presupuesto detallado.
                DATOS ADICIONALES: {mides}
                INVENTARIO DEL CLIENTE: {inventario_text}
                INSTRUCCIONES:
                1. Identifica materiales y avería.
                2. Prioriza precios del INVENTARIO. Si no están, busca precios de mercado.
                3. COSTES: 60€ visita + 45€/h + Materiales + 21% IVA.
                Responde en ESPAÑOL de forma profesional.
                """

                for nombre_modelo in modelos_a_probar:
                    try:
                        st.info(f"Intentando con modelo: {nombre_modelo}...")
                        model = genai.GenerativeModel(nombre_modelo)
                        respuesta_ia = model.generate_content([prompt, video_up])
                        if respuesta_ia:
                            break # Si funciona, salimos del bucle
                    except Exception as e:
                        error_acumulado += f"\n- Error en {nombre_modelo}: {str(e)}"
                        continue

                if respuesta_ia:
                    resultado_final = respuesta_ia.text
                    st.markdown("### Resultado del Análisis")
                    st.write(resultado_final)

                    # 4. Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt="PRESUPUESTO ScopeAI", ln=1, align='C')
                    pdf.ln(10)
                    texto_pdf = resultado_final.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, txt=texto_pdf)
                    
                    nombre_pdf = "presupuesto.pdf"
                    pdf.output(nombre_pdf)
                    with open(nombre_pdf, "rb") as f:
                        st.download_button("📥 Descargar PDF", f, file_name="Presupuesto_ScopeAI.pdf")
                else:
                    st.error(f"No ha funcionado ningún modelo. Detalles: {error_acumulado}")

                # Limpiar archivo temporal
                os.unlink(temp_path)

            except Exception as e:
                st.error(f"Error general: {e}")
