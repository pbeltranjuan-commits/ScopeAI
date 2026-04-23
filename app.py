import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# --- IMPORTACIONS DE SEGURETAT ---
try:
    from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
    from pagos import mostrar_pago
    from ingenieria import obtener_manual_formulas
except ImportError:
    st.error("🚨 ERROR: Falten fitxers al GitHub (ingenieria.py, usuarios.py o pagos.py). Puja'ls tots!")
    st.stop()

# 1. CONFIGURACIÓ DE L'API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")

# --- LOGIN I CONTROL D'IP ---
gestionar_sesion()

st.title("🏗️ ScopeAI Enterprise")

if 'history' not in st.session_state: st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.get('user')}**")
    
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
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita
    loc_actual = "📍 Carrer de la Riera, Mataró"

# --- DASHBOARD ---
if st.session_state.history:
    st.markdown("### 📊 Resum d'Activitat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(df_h))
    c2.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 Operativa")
    st.markdown("---")

# --- INSPECCIÓ ---
st.subheader("📸 Nova Inspecció")
notas = st.text_area("Información técnica", placeholder="Descripció de l'avaria...")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    if st.button("🚀 EJECUTAR ANÀLISI COMPLETA"):
        # CONTROL DE QUOTA I PAGAMENT
        tiene_gratis = verificar_cuota()
        pago_realizado = False
        
        if not tiene_gratis:
            pago_realizado = mostrar_pago()
            
        if tiene_gratis or pago_realizado:
            with st.status("🔍 Buscant materials en múltiples webs i calculant..."):
                try:
                    suffix = os.path.splitext(archivo.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                        tfile.write(archivo.read())
                        temp_path = tfile.name

                    file_uploaded = genai.upload_file(path=temp_path)
                    while file_uploaded.state.name == "PROCESSING":
                        time.sleep(2)
                        file_uploaded = genai.get_file(file_uploaded.name)

                    formulas = obtener_manual_formulas()

                    model = genai.GenerativeModel(model_name=model_triat)
                    
                    # PROMPT MILLORAT PER EVITAR LINKS MORTS I CERCA MULTI-WEB
                    prompt = f"""
                    ERES UN INGENIERO EXPERTO.
                    USA ESTAS FÓRMULAS: {formulas}
                    
                    INSTRUCCIONES CRÍTICAS DE BÚSQUEDA:
                    1. Si el material no está en este Excel: {inv_data}
                    2. DEBES buscar el recambio exacto en Google.
                    3. No te limites a Leroy Merlin. Busca en: Amazon Business, RS Components, ManoMano, Bauhaus, y Distribuidores Industriales.
                    4. Para cada artículo, verifica mentalmente que el LINK EXISTE. Proporciona al menos 2 opciones de compra con URLs reales.
                    
                    ESTRUCTURA DEL INFORME:
                    - !!! ALERTA DE SEGURIDAD !!! (Si aplica)
                    - Diagnóstico técnico detallado.
                    - Listado de materiales con Enlaces Directos de Compra.
                    - Presupuesto: Visita ({p_final_visita}€) + MO ({c_hora}€/h) + Materiales + IVA 21%.
                    - Responde en CATALÀ.
                    """

                    respuesta = model.generate_content([prompt, file_uploaded])
                    
                    if respuesta.text:
                        st.markdown(respuesta.text)
                        
                        # GENERACIÓ DE PDF SEGURA
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        clean_text = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=clean_text)
                        pdf_path = "informe.pdf"
                        pdf.output(pdf_path)
                        
                        with open(pdf_path, "rb") as f:
                            st.download_button("📥 Baixar Informe PDF", f, file_name="Informe_ScopeAI.pdf")

                        # SI ERA GRATIS, MARQUEM COM A GASTAT I REFRESCQUEM
                        if tiene_gratis:
                            registrar_uso_gratis()
                            st.success("Crèdit gratuït consumit.")
                            time.sleep(1)
                            st.rerun()

                    os.unlink(temp_path)
                    genai.delete_file(file_uploaded.name)

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("🔒 Superat el límit diari. Paga 1€ per desbloquejar aquest anàlisi.")
