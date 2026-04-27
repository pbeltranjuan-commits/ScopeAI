import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile

# --- 1. IMPORTACIONS SEGURES ---
from estils import aplicar_estils_personalitzats, caixa_analisi
from prompts import obtener_prompt_ingenieria
from generador_pdf import crear_pdf_professional

# Intentem importar la base de dades, si no existeix, creem una funció buida per no trencar l'app
try:
    from base_dades import guardar_inspeccio_gsheets
except ImportError:
    def guardar_inspeccio_gsheets(*args): pass

# --- 2. CONFIGURACIÓ ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Enterprise", layout="wide", page_icon="🏗️")
aplicar_estils_personalitzats()

st.title("🏗️ ScopeAI Enterprise")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    # Si no tens usuarios.py, posem un usuari per defecte
    usuari_actual = st.session_state.get('user', 'Tècnic_Demo')
    st.write(f"👤 Usuari: **{usuari_actual}**")
    
    model_triat = st.selectbox("🧠 Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    st.markdown("---")
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)

# --- 4. INTERFÍCIE ---
st.subheader("📸 Nova Inspecció")
col_a, col_b = st.columns([2,1])

with col_a:
    notas = st.text_area("Informació tècnica", placeholder="Descriu l'avaria...")
    archivo = st.file_uploader("Pujar evidència", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_b:
    st.info("📍 Carrer de la Riera, Mataró")
    if es_urgent: st.error("TARIFA D'URGÈNCIA")

# --- 5. LÒGICA D'EXECUCIÓ ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI"):
        with st.status("🛠️ Analitzant..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Cridem al motor de prompts
                prompt = obtener_prompt_ingenieria("Mataró", es_urgent, notas, "Inventari buit", c_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                res = model.generate_content([prompt, file_uploaded])
                
                if res.text:
                    st.markdown("---")
                    caixa_analisi("Informe d'Enginyeria", "🔍", res.text)
                    
                    # Generem el PDF
                    pdf_bytes = crear_pdf_professional(res.text, usuari_actual)
                    st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name="informe.pdf")
                    
                    # Intentem guardar a l'històric
                    guardar_inspeccio_gsheets(usuari_actual, "Avaria", 100.0)

                os.unlink(temp_path)
            except Exception as e:
                st.error(f"Error: {e}")
