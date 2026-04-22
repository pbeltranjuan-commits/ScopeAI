import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time

# Configuración API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Technical", layout="wide")
st.title("ScopeAI")

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    u = st.text_input("Usuario")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuración")
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = ""
    if ex:
        df = pd.read_excel(ex)
        inv_data = df.to_string()
    
    st.markdown("---")
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

# --- ENTRADA ---
st.subheader("Datos")
notas = st.text_area("Información técnica / Fórmulas deseadas")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info(f"Archivo cargado: {archivo.name} ({archivo.size // 1024} KB)")

    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Calculando ingeniería..."):
            try:
                # 1. DETECCIÓN MANUAL AGRESIVA DE MIME TYPE
                m_type = "video/mp4" # Default
                if archivo.name.lower().endswith(('.jpg', '.jpeg')): m_type = "image/jpeg"
                elif archivo.name.lower().endswith('.png'): m_type = "image/png"
                elif archivo.name.lower().endswith('.mov'): m_type = "video/quicktime"

                # 2. LECTURA DIRECTA DE BYTES (Saltamos el error de 'Unknown mime type')
                # Enviamos el contenido como una lista de partes directamente
                blob = {
                    "mime_type": m_type,
                    "data": archivo.getvalue()
                }

                # 3. MODELO DE ALTA PRECISIÓN
                model = genai.GenerativeModel('gemini-1.5-pro')

                prompt = f"""
                ERES UN INGENIERO DE INSTALACIONES MECÁNICAS.
                DATOS TÉCNICOS: {notas}
                INVENTARIO PRECIOS: {inv_data}
                
                PROTOCOLO:
                1. Determina medidas reales (discrecionales) del vídeo/imagen.
                2. Usa fórmulas de ingeniería (Bernoulli, Darcy, Manning, etc.) para validar el daño o la instalación.
                3. Genera presupuesto: Visita {c_visita}€ + {c_hora}€/h + Materiales (Excel o internet) + 21% IVA.
                4. Incluye sección "Memoria de Cálculo" con fórmulas en LaTeX.
                
                IDIOMA: ESPAÑOL. SÉ DETERMINISTA, NO PROBABILÍSTICO.
                """

                # Enviamos los bytes directamente en la llamada
                res = model.generate_content([prompt, blob])
                
                if res:
                    st.markdown("---")
                    st.markdown(res.text)

                    # PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    pdf_text = res.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=pdf_text)
                    pdf.output("informe.pdf")
                    with open("informe.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe PDF", f, file_name="Informe_Tecnico.pdf")

            except Exception as e:
                st.error(f"Fallo en el motor de ingeniería: {str(e)}")
                st.warning("Consejo: Si el error persiste, intenta subir una FOTO en lugar de un vídeo para descartar problemas de ancho de banda.")
