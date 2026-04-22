import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time

# Configuración con la clave de tus Secrets
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

# --- CONFIGURACIÓN TÉCNICA ---
with st.sidebar:
    ex = st.file_uploader("Inventario (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else ""
    st.markdown("---")
    c_visita = st.number_input("Precio Visita (€)", value=60.0)
    c_hora = st.number_input("Precio Hora (€)", value=45.0)

st.subheader("Datos")
notas = st.text_area("Información técnica / Fórmulas")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info(f"Archivo cargado: {archivo.name} ({archivo.size // 1024} KB)")

    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Detectando motores disponibles y calculando..."):
            try:
                # 1. BUSCAR MODELOS REALES DISPONIBLES EN TU CUENTA
                modelos_disponibles = [m.name for m in genai.list_models() 
                                      if 'generateContent' in m.supported_generation_methods]
                
                # Filtramos para priorizar los modelos Pro o Flash 1.5
                motores_validos = [m for m in modelos_disponibles if "1.5" in m or "2.0" in m]
                if not motores_validos: motores_validos = modelos_disponibles

                # 2. PREPARAR ARCHIVO (Envío directo de bytes)
                m_type = archivo.type if archivo.type else "video/mp4"
                blob = {"mime_type": m_type, "data": archivo.getvalue()}

                # 3. PROMPT DE INGENIERÍA DISCRECIONAL
                prompt = f"""
                ACTÚA COMO INGENIERO EXPERTO. RESULTADOS DISCRECIONALES.
                DATOS: {notas}. INVENTARIO: {inv_data}. 
                COSTES MANO OBRA: {c_visita}€ visita + {c_hora}€/h.
                MUESTRA CÁLCULOS: Aplica fórmulas reales (Bernoulli, caudales, presiones).
                IDOMA: ESPAÑOL.
                """

                # 4. INTENTO DE PROCESAMIENTO
                respuesta = None
                ultimo_error = ""

                for motor in motores_validos:
                    try:
                        st.write(f"Probando motor: {motor}...")
                        model = genai.GenerativeModel(motor)
                        respuesta = model.generate_content([prompt, blob])
                        if respuesta: break
                    except Exception as e:
                        ultimo_error = str(e)
                        continue

                if respuesta:
                    st.success("¡Análisis completado!")
                    st.markdown(respuesta.text)
                    
                    # Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    pdf_text = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt=pdf_text)
                    pdf.output("informe.pdf")
                    with open("informe.pdf", "rb") as f:
                        st.download_button("📥 Descargar Informe PDF", f, file_name="Informe_ScopeAI.pdf")
                else:
                    st.error(f"Ningún motor ha funcionado. Error: {ultimo_error}")

            except Exception as e:
                st.error(f"Error general: {str(e)}")
