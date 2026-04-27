import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile

# --- 1. IMPORTACIONS DELS TEUS BLOCS DE NOTES ---
from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago
from ingenieria import obtener_manual_formulas
from estils import aplicar_estils_personalitzats, caixa_analisi
from prompts import obtener_prompt_ingenieria
from generador_pdf import crear_pdf_professional  # <--- EL NOU SECRETARI DE PDFS!

# --- 2. CONFIGURACIÓ I ESTILS ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")
aplicar_estils_personalitzats()

# --- 3. GESTIÓ D'USUARI ---
gestionar_sesion()

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🏗️ ScopeAI Enterprise")

# --- 4. SIDEBAR (Configuració Tècnica) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.user}**")
    
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        models = ["models/gemini-1.5-pro-latest", "models/gemini-1.5-flash-latest"]
    
    model_triat = st.selectbox("🧠 Model de Gemini", models)
    
    st.markdown("---")
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hi ha inventari local disponible."
    
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "📍 Carrer de la Riera, Mataró" if incloure_gps else "Ubicació Manual"
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- 5. DASHBOARD ---
if st.session_state.history:
    st.markdown("### 📊 Resum d'Activitat")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(st.session_state.history))
    c2.metric("Estalvi CO2", f"{len(st.session_state.history)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 Operativa")
    st.markdown("---")

# --- 6. INTERFÍCIE D'INSPECCIÓ ---
st.subheader("📸 Nova Inspecció")
with st.expander("🔦 CONSELLS DE GRAVACIÓ"):
    st.write("Usa flaix, grava detalls i explica l'avaria en veu alta.")

col_a, col_b = st.columns([2,1])
with col_a:
    notas = st.text_area("Informació tècnica", placeholder="Escriu aquí o descriu l'avaria...")
    archivo = st.file_uploader("Pujar vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_b:
    if es_urgent: st.error("TARIFA D'URGÈNCIA ACTIVA")
    st.info(f"📍 {loc_actual}")

# --- 7. BOTÓ D'EXECUTAR ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        pot_anar_gratis = verificar_cuota()
        
        if not pot_anar_gratis:
            if not mostrar_pago():
                st.warning("🔒 Límit diari assolit. Si us plau, confirma el pagament de 1€.")
                st.stop()

        with st.status("🚀 Processant anàlisi d'enginyeria..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Prompt des de prompts.py
                prompt = obtener_prompt_ingenieria(loc_actual, es_urgent, notas, inv_data, p_final_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                res = model.generate_content([prompt, file_uploaded])
                
                if res.text:
                    st.markdown("---")
                    # Resultat visual elegant
                    caixa_analisi("Diagnòstic d'Enginyeria", "🔍", res.text)
                    
                    # --- GENERACIÓ DEL PDF PROFESSIONAL ---
                    # Cridem al nou fitxer que hem creat abans
                    pdf_bytes = crear_pdf_professional(res.text, st.session_state.user)
                    
                    st.download_button(
                        label="📥 Baixar Informe Professional PDF",
                        data=pdf_bytes,
                        file_name=f"Informe_ScopeAI_{st.session_state.user}_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )

                    if pot_anar_gratis:
                        registrar_uso_gratis()
                        st.success("Crèdit gratuït utilitzat. Refrescant...")
                        time.sleep(2)
                        st.rerun() 

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error crític: {e}")
