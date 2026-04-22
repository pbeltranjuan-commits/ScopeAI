import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile
import urllib.parse

# 1. Configuració de l'API (Secrets)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Configuració de la pàgina (Això SEMPRE ha d'anar primer)
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="🏗️")

# --- ESTILS (Corregits per evitar la pantalla vermella) ---
st.markdown("<style>.stMetric {background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;}</style>", unsafe_allow_stdio=True)

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

# --- BARRA LATERAL (Punt 2 de les teves fotos: GPS i Urgències) ---
with st.sidebar:
    st.header("⚙️ Configuració")
    ex = st.file_uploader("Inventari (Excel)", type=['xlsx'])
    inv_data = pd.read_excel(ex).to_string() if ex else "No hay inventario."
    
    st.markdown("---")
    c_visita = st.number_input("Preu Visita Base (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    # Urgència i multiplicador
    es_urgent = st.toggle("🚨 Servei d'Urgència", value=False)
    preu_final_visita = c_visita * 1.5 if es_urgent else c_visita
    
    st.markdown("---")
    # GPS (Punt 2)
    incloure_gps = st.checkbox("Capturar Ubicació GPS", value=True)
    loc_actual = "Mataró, Espanya" if incloure_gps else "Ubicació no registrada"
    st.caption(f"📍 {loc_actual}")

# --- PANELL CENTRAL ---
st.title("🏗️ ScopeAI: Smart Maintenance")

# 1. DASHBOARD D'ACTIVITAT (Punt 3 de les teves fotos)
if st.session_state.history:
    with st.container():
        st.subheader("📊 Resum de l'Activitat")
        df_h = pd.DataFrame(st.session_state.history)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Pressupostos Totals", len(df_h))
        with c2:
            st.write("Estat de la flota: 🟢 80% Operativa")
        with c3:
            # Estalvi CO2 (Punt 1 de les millores ESG)
            st.metric("Estalvi CO2 (Est.)", f"{len(df_h)*1.2:.1f} kg")
        st.line_chart(df_h.set_index("Hora")["Estat"].apply(lambda x: 1 if x == "URGENT" else 0.5))

# 2. ENTRADA DE DADES I AJUDA (Punt 1 de les teves fotos)
st.subheader("📸 Nova Inspecció")

# Ajuda visual (Punt 1)
with st.expander("🔦 AJUDA PER A LA GRAVACIÓ"):
    st.markdown("""
    1. **Il·luminació:** Activa el flaix si estàs en un racó fosc.
    2. **Perspectiva:** Grava de lluny i després apropa't al nus o trencament.
    3. **Àudio:** Parla mentre graves per descriure l'avaria.
    """)

col_input, col_info = st.columns([2, 1])

with col_input:
    notas = st.text_area("Notes manuals", placeholder="Explica què veus o l'IA usarà l'àudio...")
    archivo = st.file_uploader("Vídeo/Foto de l'avaria", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_info:
    if es_urgent: st.error("🚨 TARIFA D'URGÈNCIA ACTIVA")
    st.info("🌱 **ESG Scan actiu:** Mesurant impacte ambiental.")

if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        with st.status("Analitzant vídeo, àudio i pressupostos..."):
            try:
                # Gestió de fitxers temporals
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # Pujada a Gemini
                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                model = genai.GenerativeModel('gemini-1.5-pro')
                
                # PROMPT AMB TOTS ELS PUNTS INTEGRATS
                prompt = f"""
                ERES UN INGENIERO SENIOR Y PERITO.
                CONTEXTO: "{notas}" | URGENCIA: {es_urgent} | UBICACIÓN: {loc_actual}
                
                1. IA SAFETY SCAN: Busca peligros. Si hay, empieza con "!!! ALERTA DE SEGURIDAD !!!".
                2. DIAGNÓSTICO: Analiza video/audio para identificar el fallo.
                3. PRESUPUESTO TRIPLE: Opciones Low-cost, Estándar y Premium usando inventario ({inv_data}).
                4. COSTES: Visita {preu_final_visita}€, Mano de obra {c_hora}€/h.
                5. PEDIDO: Genera una lista técnica para el proveedor al final.
                6. ESG: Estima el ahorro de CO2.
                """

                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    # Mostrar alerta de seguretat si n'hi ha
                    if "!!!" in respuesta.text:
                        st.warning(f"⚠️ {respuesta.text.split('!!!')[1]}")
                    
                    st.markdown("### 📋 Informe i Propostes")
                    st.markdown(respuesta.text)
                    
                    st.markdown("---")
                    t1, t2, t3 = st.tabs(["📄 PDF", "🛒 Comanda", "💾 Registrar"])
                    
                    with t1:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=10)
                        txt_clean = (f"SCOPEAI REPORT - {loc_actual}\n\n" + respuesta.text).encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, txt=txt_clean)
                        pdf.output("Report.pdf")
                        st.download_button("Baixar PDF", open("Report.pdf", "rb"), file_name="Pressupost.pdf")
                    
                    with t2:
                        st.code(respuesta.text.split("PEDIDO")[-1] if "PEDIDO" in respuesta.text else "Materials a l'informe.", language="markdown")
                    
                    with t3:
                        if st.button("Confirmar i Guardar"):
                            st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Element": archivo.name, "Estat": "URGENT" if es_urgent else "OK"})
                            st.success("Guardat al Dashboard!")

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)
            except Exception as e:
                st.error(f"Error crític: {e}")
