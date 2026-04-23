import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# --- IMPORTACIONS DELS TEUS NOUS MÒDULS ---
from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago
from ingenieria import obtener_manual_formulas

# 1. CONFIGURACIÓ DE L'API I PÀGINA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")

# --- LOGIN OBLIGATORI (Ara gestionat des de usuarios.py) ---
gestionar_sesion()

st.title("🏗️ ScopeAI Enterprise")

# Inicialitzar historial de la sessió
if 'history' not in st.session_state: 
    st.session_state.history = []

# --- CONFIGURACIÓ SIDEBAR (Recuperat el selector de models i GPS) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.get('user', 'Desconegut')}**")
    
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

# --- DASHBOARD (Mantenim les mètriques d'estalvi de CO2) ---
if st.session_state.history:
    st.markdown("### 📊 Resum d'Activitat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(df_h))
    c2.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 Operativa")
    st.markdown("---")

# --- ENTRADA DE DADES (Amb ajudes visuals) ---
st.subheader("📸 Nova Inspecció")

with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.write("1. Flaix actiu. 2. Perspectiva de lluny a prop. 3. Descriu l'avaria parlant.")

col_in, col_alert = st.columns([2, 1])
with col_in:
    notas = st.text_area("Información técnica", placeholder="Escriu o deixa que l'IA escolti el vídeo...")
    archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_alert:
    if es_urgent: st.error("TARIFA D'URGÈNCIA ACTIVA")
    st.info(f"Model actiu: {model_triat.split('/')[-1]}")

# --- LÒGICA DE L'ANÀLISI ---
if archivo:
    st.success(f"Arxiu detectat: {archivo.name}")
    
    if st.button("🚀 EJECUTAR ANÀLISI COMPLETA"):
        # 1. Comprovem la quota
        pot_anar_gratis = verificar_cuota()
        pago_ok = False
        
        if not pot_anar_gratis:
            # Si no té gratis, cridem a pagos.py
            pago_ok = mostrar_pago()
            if not pago_ok:
                st.warning("🔒 Operació bloquejada. Superat el límit diari. Si us plau, realitza el pagament.")
                st.stop() # Aturem l'execució si no s'ha marcat el pagament

        # 2. Execució real (Només si el "policia" el deixa passar)
        with st.status(f"🔍 Analitzant amb {model_triat}..."):
            try:
                # Gestió de fitxer temporal
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # Pujada a l'API de Google
                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Carreguem fórmules d'enginyeria
                manual_tecnic = obtener_manual_formulas()

                model = genai.GenerativeModel(model_name=model_triat)
                
                # PROMPT ORIGINAL MILLORAT (Amb multi-cerca i fórmules)
                prompt = f"""
                ERES UN INGENIERO SENIOR Y PERITO.
                UBICACIÓN: {loc_actual} | URGENCIA: {es_urgent}
                FÓRMULAS DE APOYO: {manual_tecnic}
                INVENTARIO EXCEL: {inv_data}
                COSTES: Visita {p_final_visita}€, Mano obra {c_hora}€/h.

                TAREA:
                1. IA SAFETY SCAN: Avisa si hay peligro con "!!! ALERTA DE SEGURIDAD !!!".
                2. DIAGNÓSTICO: Identifica materiales y daños.
                3. BÚSQUEDA MULTI-WEB (CRÍTICO): 
                   - Busca recambios en Amazon Business, RS Components, ManoMano y Bauhaus.
                   - Proporciona al menos 2 enlaces reales por artículo.
                4. PRESUPUESTO: Desglose con IVA 21%.
                5. ESG: Calcula ahorro de CO2.
                6. RESPONDE EN CATALÀ.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("---")
                    st.markdown(respuesta.text)
                    
                    # --- GENERACIÓ DE PDF ---
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt_pdf = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt_pdf)
                        pdf_path = "informe.pdf"
                        pdf.output(pdf_path)
                        
                        st.download_button("📥 Baixar Informe PDF", open(pdf_path, "rb"), file_name=f"ScopeAI_{archivo.name}.pdf")
                    except Exception as pdf_e:
                        st.error(f"Error generant PDF: {pdf_e}")

                    # --- REGISTRE I REFRESC ---
                    if pot_anar_gratis:
                        registrar_uso_gratis()
                        st.success("Crèdit gratuït consumit. Refrescant sistema de quota...")
                        time.sleep(2)
                        st.rerun() # Clau per bloquejar el proper intent
                    
                    st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Estat": "OK"})

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error crític: {str(e)}")
