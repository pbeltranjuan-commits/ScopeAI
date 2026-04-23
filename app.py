from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago

# 1. Forzar Login
gestionar_sesion()

# 2. En el botón de "EJECUTAR ANÁLISIS", pones esto:
if st.button("EJECUTAR ANÁLISIS"):
    tiene_gratis = verificar_cuota()
    
    if tiene_gratis:
        # AQUÍ VA TU CÓDIGO DE ANÁLISIS...
        registrar_uso_gratis() # Marcar que ya lo ha usado hoy
    else:
        # Si no tiene gratis, chequeamos pago
        if mostrar_pago():
             # AQUÍ VA TU CÓDIGO DE ANÁLISIS (Si ha pagado)...
             pass
import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# 1. CONFIGURACIÓ DE L'API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")
st.title("🏗️ ScopeAI Enterprise")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'history' not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    col_l1, col_l2 = st.columns([1, 2])
    with col_l1:
        u = st.text_input("Usuari")
        if st.button("Entrar"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- CONFIGURACIÓ SIDEBAR (Amb selector de models i GPS) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    
    # Millora: Selector de tots els models
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
    # Millora: GPS i Urgència
    incloure_gps = st.checkbox("Capturar GPS", value=True)
    loc_actual = "📍 Carrer de la Riera, Mataró" if incloure_gps else "Ubicació Manual"
    st.caption(f"Localització: {loc_actual}")
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- DASHBOARD (Millora acordada) ---
if st.session_state.history:
    st.markdown("### 📊 Resum d'Activitat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(df_h))
    c2.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 Operativa")
    st.markdown("---")

# --- ENTRADA DE DADES ---
st.subheader("📸 Nova Inspecció")

# Millora: Ajuda per a la gravació (Foto 1)
with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.write("1. Flaix actiu. 2. Perspectiva de lluny a prop. 3. Descriu l'avaria parlant.")

col_in, col_alert = st.columns([2, 1])
with col_in:
    notas = st.text_area("Información técnica", placeholder="Escriu o deixa que l'IA escolti el vídeo...")
    archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_alert:
    if es_urgent: st.error("TARIFA D'URGÈNCIA ACTIVA")
    st.info(f"Model: {model_triat.split('/')[-1]}")

if archivo:
    st.success(f"Arxiu detectat: {archivo.name}")
    
    if st.button("🚀 EJECUTAR ANÀLISI COMPLETA"):
        with st.status(f"Analitzant amb {model_triat}..."):
            try:
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                model = genai.GenerativeModel(model_name=model_triat)
                
                # PROMPT FINAL: Inclou cerca externa i enllaços
                prompt = f"""
                ERES INGENIERO DE INSTALACIONES Y PERITO. 
                UBICACIÓN: {loc_actual} | URGENCIA: {es_urgent}
                DATOS TÉCNICOS: {notas}
                INVENTARIO EXCEL: {inv_data}
                COSTES: Visita {p_final_visita}€, Mano obra {c_hora}€/h.
                
                TAREA:
                1. IA SAFETY SCAN: Avisa si hay peligro con "!!! ALERTA DE SEGURIDAD !!!".
                2. DIAGNÓSTICO: Identifica materiales y daños mediante video/audio.
                3. BÚSQUEDA DE MATERIALES (CRÍTICO): 
                   - Si el material necesario NO está en el Inventario Excel, DEBES buscar en internet.
                   - Proporciona el nombre del recambio y un ENLACE web (URL) real de compra o referencia.
                4. PRESUPUESTO: Desglose con IVA 21%.
                5. ESG: Calcula ahorro estimado de CO2.
                6. RESPONDE EN CATALÀ.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("---")
                    # Mostrar alerta de seguretat si n'hi ha
                    if "!!!" in respuesta.text:
                        st.warning(f"⚠️ {respuesta.text.split('!!!')[1]}")
                    
                    st.markdown(respuesta.text)
                    
                    # PDF i Registre
                    t_pdf, t_reg = st.tabs(["📥 Baixar Informe", "💾 Registrar"])
                    
                    with t_pdf:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt_pdf)
                        pdf.output("informe.pdf")
                        with open("informe.pdf", "rb") as f:
                            st.download_button("Descargar Informe PDF", f, file_name=f"ScopeAI_{archivo.name}.pdf")
                    
                    with t_reg:
                        if st.button("Guardar al Dashboard"):
                            st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Estat": "OK"})
                            st.success("Registrat correctament!")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error crític: {str(e)}")
