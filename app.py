import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# 1. CONFIGURACIÓ DE L'API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Gemini Multi-Model", layout="wide", page_icon="💎")

# --- SISTEMA DE SESSIÓ ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'history' not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.title("🔐 ScopeAI Enterprise Login")
    u = st.text_input("Usuari")
    if st.button("Entrar"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- FUNCIONALITAT DE MODELS (Tots els disponibles) ---
def get_available_models():
    try:
        # Busquem models que suportin generació de contingut (multimodals)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except:
        return ["models/gemini-1.5-pro-latest", "models/gemini-1.5-flash-latest"]

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    
    available_models = get_available_models()
    model_triat = st.selectbox(
        "🧠 Tria qualsevol model Gemini",
        available_models,
        index=0,
        help="Aquí surten tots els models disponibles a la teva API Key."
    )
    
    st.markdown("---")
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "Sense inventari."
    
    st.markdown("---")
    c_visita = st.number_input("Preu Visita Base (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    # GPS i Localització
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "📍 Mataró, Espanya" if incloure_gps else "Ubicació Manual"
    st.caption(f"Localització: {loc_actual}")
    
    st.markdown("---")
    # Urgència
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- PANELL CENTRAL ---
st.title("🏗️ ScopeAI: Multi-Model Engineering")

# 1. DASHBOARD
if st.session_state.history:
    st.markdown("### 📊 Dashboard d'Estat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(df_h))
    c2.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Flota", "🟢 Activa")

# 2. INSPECCIÓ
st.subheader("📸 Captura d'Avaria")
with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.write("1. Flaix actiu. 2. Perspectiva de lluny a prop. 3. Descriu l'avaria parlant.")

col_in, col_info = st.columns([2, 1])
with col_in:
    notas = st.text_area("Notes manuals", placeholder="Explica l'avaria...")
    archivo = st.file_uploader("Vídeo o Foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    if st.button(f"🚀 EXECUTAR AMB {model_triat.split('/')[-1].upper()}"):
        with st.status(f"Connectant amb {model_triat}..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # Pujada de fit
