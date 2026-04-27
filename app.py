import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile

# --- 1. IMPORTACIONS (Si no troba el fitxer, no peta) ---
from estils import aplicar_estils_personalitzats, caixa_analisi
try:
    from prompts import obtener_prompt_ingenieria
    from generador_pdf import crear_pdf_professional
except ImportError:
    st.error("⚠️ Falten fitxers a GitHub! Recorda pujar 'prompts.py' i 'generador_pdf.py'")

# --- 2. CONFIGURACIÓ ORIGINAL RECONSTRUÏDA ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Enterprise", layout="wide", page_icon="🏗️")
aplicar_estils_personalitzats()

st.title("🏗️ ScopeAI Enterprise")

# --- 3. SIDEBAR (Tot el que tenies abans) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.get('user', 'Usuari')}**")
    
    # Models de Gemini (Com a la teva imatge e5cc50.png)
    model_triat = st.selectbox("🧠 Model de Gemini", ["gemini-1.5-flash", "gemini-1.5-pro"])
    
    st.markdown("---")
    # Gestió de l'inventari Excel
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hi ha inventari disponible."
    
    # Preus originals
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- 4. COS DE L'APP ---
st.subheader("📸 Nova Inspecció")
with st.expander("🔦 CONSELLS DE GRAVACIÓ"):
    st.write("Usa flaix, grava detalls i explica l'avaria en veu alta.")

col_a, col_b = st.columns([2,1])
with col_a:
    notas = st.text_area("Informació tècnica", placeholder="Escriu aquí o descriu l'avaria...")
    archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_b:
    st.info("📍 Carrer de la Riera, Mataró")
    if es_urgent: st.error("TARIFA D'URGÈNCIA ACTIVA")

# --- 5. EXECUCIÓ ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        with st.status("🚀 Processant..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Connectem amb el bloc de prompts
                prompt = obtener_prompt_ingenieria("Mataró", es_urgent, notas, inv_data, p_final_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                res = model.generate_content([prompt, file_uploaded])
                
                if res.text:
                    st.markdown("---")
                    caixa_analisi("Diagnòstic d'Enginyeria", "🔍", res.text)
                    
                    # Generació del PDF professional
                    pdf_bytes = crear_pdf_professional(res.text, st.session_state.get('user', 'Admin'))
                    st.download_button("📥 Baixar Informe PDF", data=pdf_bytes, file_name="informe_v3.pdf")

                os.unlink(temp_path)
            except Exception as e:
                st.error(f"Error: {e}")
