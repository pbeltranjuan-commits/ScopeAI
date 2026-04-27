import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile

# --- 1. IMPORTACIONS DE TOTS ELS TEUS BLOCS DE NOTES ---
from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago
from ingenieria import obtener_manual_formulas
from estils import aplicar_estils_personalitzats, caixa_analisi
from prompts import obtener_prompt_ingenieria
from generador_pdf import crear_pdf_professional
from base_dades import guardar_inspeccio_gsheets # El bloc per a milers d'usuaris

# --- 2. CONFIGURACIÓ I DISSENY ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Enterprise", layout="wide", page_icon="🏗️")

# Apliquem el nou disseny que es llegeix bé
aplicar_estils_personalitzats()

# --- 3. LOGIN I SESSIÓ ---
gestionar_sesion()

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🏗️ ScopeAI Enterprise")

# --- 4. SIDEBAR (Control Tècnic) ---
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
    inv_data = pd.read_excel(ex).to_string() if ex else "Sense inventari local."
    
    c_visita = st.number_input("Preu Visita (€)", value=60.0)
    c_hora = st.number_input("Preu Hora (€)", value=45.0)
    
    st.markdown("---")
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita
    
    # Ubicació simulada (es pot connectar a GPS real)
    loc_actual = "📍 Carrer de la Riera, Mataró"

# --- 5. INTERFÍCIE D'INSPECCIÓ ---
st.subheader("📸 Nova Inspecció d'Enginyeria")

col_a, col_b = st.columns([2,1])
with col_a:
    notas = st.text_area("Descripció tècnica de l'avaria", placeholder="Explica què veus o quina prova has fet...")
    archivo = st.file_uploader("Pujar evidència (Foto o Vídeo)", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

with col_b:
    st.info(f"📍 Ubicació: {loc_actual}")
    if es_urgent: st.error("🔥 TARIFA D'URGÈNCIA ACTIVADA")

# --- 6. EXECUCIÓ I GENERACIÓ DE RESULTATS ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI I GENERAR INFORME"):
        # Verificació de quota/pagament
        if not verificar_cuota():
            if not mostrar_pago():
                st.warning("🔒 Cal confirmar el pagament per continuar.")
                st.stop()

        with st.status("🛠️ Analitzant evidències i calculant pressupost..."):
            try:
                # Gestió de fitxer temporal
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                # Pujada a Gemini
                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # 🧠 CRIDA AL MOTOR DE PROMPTS
                prompt = obtener_prompt_ingenieria(loc_actual, es_urgent, notas, inv_data, p_final_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                res = model.generate_content([prompt, file_uploaded])
                
                if res.text:
                    st.markdown("---")
                    # Mostrem el resultat amb el disseny de targeta professional
                    caixa_analisi("Diagnòstic Oficial ScopeAI", "🔍", res.text)
                    
                    # 📄 GENERACIÓ DEL PDF DE LUXE
                    pdf_bytes = crear_pdf_professional(res.text, st.session_state.user)
                    
                    st.download_button(
                        label="📥 Baixar Informe Tècnic Professional (PDF)",
                        data=pdf_bytes,
                        file_name=f"Informe_{st.session_state.user}_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )

                    # 📊 GUARDAR A LA BASE DE DADES (HISTÒRIC)
                    # Aquí guardem la dada perquè no es perdi mai
                    guardar_inspeccio_gsheets(st.session_state.user, "Inspecció General", 150.0)

                    # Registre d'ús
                    registrar_uso_gratis()
                    st.success("Inspecció finalitzada i guardada a l'històric.")

                # Neteja
                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error en el procés: {e}")

# --- 7. APARTAT D'ESTADÍSTIQUES (Opcional) ---
st.markdown("---")
if st.checkbox("📊 Mostrar historial d'activitat de l'empresa"):
    from analitica import mostrar_dashboard
    mostrar_dashboard()
