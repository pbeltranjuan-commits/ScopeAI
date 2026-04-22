import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time

# Configuració IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # Nota: Gemini 2.5 encara no està obert a l'API pública, usem Flash que és el més ràpid per a vídeos.

st.set_page_config(page_title="ScopeAI", layout="wide")

# --- SISTEMA DE SESSIÓ (Molt bàsic per començar) ---
if 'autenticat' not in st.session_state:
    st.session_state.autenticat = False

if not st.session_state.autenticat:
    st.title("Inici de Sessió / Crear Compte")
    usuari = st.text_input("Usuari")
    clau = st.text_input("Contrasenya", type="password")
    if st.button("Entrar"):
        st.session_state.autenticat = True
        st.rerun()
    st.stop() # Atura la web aquí si no està loguejat

# --- APP PRINCIPAL ---
st.title("ScopeAI: Gestió Professional d'Avarias")

# 1. PUJAR INVENTARI EXCEL (Preus de referència)
with st.sidebar:
    st.header("Configuració")
    excel_file = st.file_uploader("Puja l'inventari/tarifari (Excel)", type=['xlsx'])
    inventari_text = ""
    if excel_file:
        df = pd.read_excel(excel_file)
        inventari_text = df.to_string()
        st.success("Inventari carregat")

# 2. FORMULARI DE MIDES (Opcional)
with st.expander("📝 Formulari de mides i desperfectes (Opcional)"):
    mides = st.text_area("Introdueix mides o detalls observats a simple vista")

# 3. PUJAR VÍDEO I PROCESSAR
archivo = st.file_uploader("Puja el vídeo de l'avaria", type=['mp4', 'mov'])

if archivo is not None:
    if st.button("Processar Factura i Pressupost"):
        with st.spinner("Analitzant vídeo, Excel i Internet..."):
            # Guardar vídeo temporal
            with open("temp_video.mp4", "wb") as f:
                f.write(archivo.getbuffer())
            
            video_up = genai.upload_file(path="temp_video.mp4")
            while video_up.state.name == "PROCESSING":
                time.sleep(2)
                video_up = genai.get_file(video_up.name)

            # PROMPT INTEGRAT (Vídeo + Excel + Formulari + Internet)
            prompt = f"""
            ACTUA COM UN PÈRIT EXPERT.
            Analitza el vídeo i el formulari adjunt.
            Dades del formulari: {mides}
            Inventari de preus del client: {inventari_text}
            
            INSTRUCCIONS:
            1. Identifica materials i avaria.
            2. Si el material és a l'inventari, usa aquest preu. 
            3. Si NO és a l'inventari, busca a internet preus de mercat actuals.
            4. Genera un pressupost: 60€ visita + 45€/h + Materials + IVA.
            Respon en Català de forma neta.
            """

            resposta = model.generate_content([prompt, video_up])
            resultat_text = resposta.text
            st.write(resultat_text)

            # 4. GENERAR PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="PRESSUPOST PROFESSIONAL - ScopeAI", ln=1, align='C')
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=resultat_text.encode('latin-1', 'replace').decode('latin-1'))
            
            pdf_output = "pressupost_scopeai.pdf"
            pdf.output(pdf_output)
            
            with open(pdf_output, "rb") as f:
                st.download_button("📥 Descarregar Pressupost en PDF", f, file_name="Pressupost.pdf")
