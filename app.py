import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile
from fpdf import FPDF

# --- 1. IMPORTACIONS DELS TEUS MÒDULS ---
from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago
from ingenieria import obtener_manual_formulas
from estils import aplicar_estils_personalitzats, caixa_analisi
from prompts import obtener_prompt_ingenieria
from generador_pdf import crear_pdf_professional
from dashboard import mostrar_dashboard_premium  # <--- NOU BLOC

# Intentem importar la base de dades
try:
    from base_dades import guardar_inspeccio_gsheets
except ImportError:
    def guardar_inspeccio_gsheets(*args): pass

# --- 2. CONFIGURACIÓ DE L'API I PÀGINA ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")

# Apliquem el disseny Premium (Negre & Blanc)
aplicar_estils_personalitzats()

# LOGIN OBLIGATORI
gestionar_sesion()

st.title("🏗️ ScopeAI Enterprise")

# Inicialitzar historial de la sessió
if 'history' not in st.session_state: 
    st.session_state.history = []

# --- 3. CONFIGURACIÓ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.get('user', 'pol123')}**")
    
    try:
        models_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        models_disponibles = ["models/gemini-1.5-pro-latest", "models/gemini-1.5-flash-latest"]
    
    model_triat = st.selectbox("🧠 Model de Gemini", models_disponibles)
    
    st.markdown("---")
    ex = st.file_uploader("📦 Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario local disponible."
    
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "📍 Carrer de la Riera, Mataró" if incloure_gps else "Ubicació Manual"
    st.caption(f"Localització: {loc_actual}")
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- 4. DASHBOARD MODULAR PREMIUM (Substitueix l'antic) ---
if st.session_state.history:
    mostrar_dashboard_premium(st.session_state.history)
    st.markdown("---")

# --- 5. ENTRADA DE DADES ---
st.subheader("📸 Nova Inspecció")
with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.write("1. Flaix actiu. 2. Perspectiva de lluny a prop. 3. Descriu l'avaria parlant.")

col_in, col_alert = st.columns([2, 1])
with col_in:
    notas = st.text_area("Informació tècnica", placeholder="Escriu o descriu l'avaria...")
    archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_alert:
    if es_urgent: st.error("TARIFA D'URGÈNCIA ACTIVA")
    st.info(f"Model actiu: {model_triat.split('/')[-1]}")

# --- 6. LÒGICA DE L'ANÀLISI ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        pot_anar_gratis = verificar_cuota()
        
        if not pot_anar_gratis:
            if not mostrar_pago():
                st.warning("🔒 Operació bloquejada. Superat el límit diari.")
                st.stop()

        with st.status(f"🔍 Analitzant amb {model_triat}..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                prompt = obtener_prompt_ingenieria(loc_actual, es_urgent, notas, inv_data, p_final_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("---")
                    caixa_analisi("Diagnòstic Oficial ScopeAI", "🔍", respuesta.text)
                    
                    # GUARDEM A L'HISTORIAL PER AL DASHBOARD
                    st.session_state.history.append({
                        "Hora": time.strftime("%H:%M"), 
                        "Data": time.strftime("%d/%m/%Y"),
                        "Tipus": "Inspecció Tècnica"
                    })

                    pdf_bytes = crear_pdf_professional(respuesta.text, st.session_state.get('user', 'pol123'))
                    
                    st.download_button(
                        label="📥 Baixar Informe PDF Professional",
                        data=pdf_bytes,
                        file_name=f"Informe_{st.session_state.get('user', 'pol123')}.pdf",
                        mime="application/pdf"
                    )

                    guardar_inspeccio_gsheets(st.session_state.get('user', 'pol123'), "Avaria Tècnica", 150.0)

                    if pot_anar_gratis:
                        registrar_uso_gratis()
                        st.success("Crèdit gratuït consumit.")
                        time.sleep(1)
                        st.rerun()

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error crític: {str(e)}")
