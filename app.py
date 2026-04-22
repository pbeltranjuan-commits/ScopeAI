import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time

# 1. Provar la clau que tens als Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI", layout="wide")
st.title("ScopeAI")

# --- LOGIN SIMPLE ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("Usuari") and st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- CONFIGURACIÓ ---
with st.sidebar:
    ex = st.file_uploader("Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else ""
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)

st.subheader("Datos")
notas = st.text_area("Informació tècnica")
archivo = st.file_uploader("Subir archivo", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info(f"Arxiu llest: {archivo.name} ({archivo.size // 1024} KB)")

    if st.button("EJECUTAR ANÁLISIS"):
        with st.status("Buscant motor disponible i calculant..."):
            try:
                # Preparem el fitxer per enviar-lo directament (evita errors de tipus)
                m_type = archivo.type if archivo.type else "video/mp4"
                blob = {"mime_type": m_type, "data": archivo.getvalue()}

                # LLISTA DE MOTORS PER ORDRE DE PRIORITAT
                motors_a_probar = [
                    'gemini-1.5-flash', 
                    'models/gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'models/gemini-1.5-pro',
                    'gemini-2.0-flash-exp'
                ]
                
                respuesta = None
                error_final = ""

                prompt = f"""
                ACTUA COM ENGINYER EXPERT. SIGUES DETERMINISTA.
                Dades: {notas}. Inventari: {inv_data}. 
                Costes: {c_visita}€ visita + {c_hora}€/h.
                Aplica fórmules d'enginyeria (Bernoulli, caudals, etc.) i pressupost real.
                Idioma: ESPAÑOL.
                """

                # EL BUCLE QUE BUSCA EL MOTOR QUE FUNCIONI
                for m_name in motors_a_probar:
                    try:
                        model = genai.GenerativeModel(m_name)
                        respuesta = model.generate_content([prompt, blob])
                        if respuesta: break
                    except Exception as e:
                        error_final = str(e)
                        continue # Si falla, prova el següent motor

                if respuesta:
                    st.success(f"Analitzat amb èxit!")
                    st.markdown(respuesta.text)
                    
                    # Generar el PDF per descarregar
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    pdf.multi_cell(0, 5, txt=respuesta.text.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.output("informe.pdf")
                    with open("informe.pdf", "rb") as f:
                        st.download_button("📥 Descarregar PDF", f, file_name="Informe_ScopeAI.pdf")
                else:
                    st.error(f"Cap motor ha funcionat. Últim error: {error_final}")

            except Exception as e:
                st.error(f"Error crític: {str(e)}")
