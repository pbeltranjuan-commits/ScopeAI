import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import os
import tempfile

# --- 1. IMPORTACIONS DE TOTS ELS TEUS MÒDULS ---
from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
from pagos import mostrar_pago
from ingenieria import obtener_manual_formulas
from estils import aplicar_estils_personalitzats, caixa_analisi
from prompts import obtener_prompt_ingenieria
from generador_pdf import crear_pdf_professional

# Blocs modulars visuals
from dashboard import mostrar_dashboard_premium
from cercador_web import cercar_preus_reals, mostrar_targeta_preu
from analitzador_financier import mostrar_targeta_financiera
from notificador import sidebar_notificacions

# --- NOU: PERSISTÈNCIA SQL ---
from base_dades import guardar_inspeccio_sql, carregar_historial_sql

# --- 2. CONFIGURACIÓ DE L'API I PÀGINA ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")

# Activem el disseny Premium
aplicar_estils_personalitzats()

# LOGIN OBLIGATORI
gestionar_sesion()

st.title("🏗️ ScopeAI Enterprise")

# --- 3. PERSISTÈNCIA DE DADES (Recuperem de SQL) ---
user_actual = st.session_state.get('user', 'pol123')
if 'history' not in st.session_state:
    # Ara l'historial ve de Supabase, no es perd mai!
    st.session_state.history = carregar_historial_sql(user_actual)

# --- 4. CONFIGURACIÓ SIDEBAR (Recuperat 100%) ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{user_actual}**")
    
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

    # BLOC NOTIFICACIONS
    sidebar_notificacions()

# --- 5. DASHBOARD (Carregat des de SQL) ---
if st.session_state.history:
    mostrar_dashboard_premium(st.session_state.history)
    st.markdown("---")

# --- 6. ENTRADA DE DADES (Recuperat Completa) ---
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
    
    if notas:
        st.markdown("🔍 **Cerca de mercat:**")
        dades_mercat = cercar_preus_reals(notas[:15])
        mostrar_targeta_preu(dades_mercat)

# --- 7. LÒGICA DE L'ANÀLISI (Recuperada línia a línia) ---
if archivo:
    if st.button("🚀 EXECUTAR ANÀLISI COMPLETA"):
        pot_anar_gratis = verificar_cuota()
        
        if not pot_anar_gratis:
            if not mostrar_pago():
                st.warning("🔒 Operació bloquejada. Superat el límit diari.")
                st.stop()

        with st.status(f"🔍 Analitzant amb {model_triat}..."):
            try:
                # Gestió de fitxer temporal per a Gemini
                suffix = os.path.splitext(archivo.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(archivo.read())
                    temp_path = tfile.name

                file_uploaded = genai.upload_file(path=temp_path)
                while file_uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    file_uploaded = genai.get_file(file_uploaded.name)

                # Generar prompt amb mòdul d'enginyeria
                prompt = obtener_prompt_ingenieria(loc_actual, es_urgent, notas, inv_data, p_final_visita, c_hora)
                
                model = genai.GenerativeModel(model_name=model_triat)
                respuesta = model.generate_content([prompt, file_uploaded])
                
                if respuesta.text:
                    st.markdown("---")
                    caixa_analisi("Diagnòstic Oficial ScopeAI", "🔍", respuesta.text)
                    
                    # ROI Financer
                    mostrar_targeta_financiera(150.0)

                    # --- GUARDAR A SQL (Sustitueix el guardat local i Sheets) ---
                    tipus_detectat = "Mecànica" if "motor" in notas.lower() else "Elèctrica"
                    guardar_inspeccio_sql(user_actual, tipus_detectat, 150.0)
                    
                    # Recarreguem de SQL per actualitzar Dashboard immediatament
                    st.session_state.history = carregar_historial_sql(user_actual)

                    # Generació de PDF
                    pdf_bytes = crear_pdf_professional(respuesta.text, user_actual)
                    
                    st.download_button(
                        label="📥 Baixar Informe PDF Professional",
                        data=pdf_bytes,
                        file_name=f"Informe_{user_actual}.pdf",
                        mime="application/pdf"
                    )

                    if pot_anar_gratis:
                        registrar_uso_gratis()
                        st.success("Anàlisi finalitzada i desada a la base de dades SQL.")
                        time.sleep(1)
                        st.rerun()

                os.unlink(temp_path)
                genai.delete_file(file_uploaded.name)

            except Exception as e:
                st.error(f"Error crític: {str(e)}")
