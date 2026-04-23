import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
import time
import os
import tempfile

# --- IMPORTACIONS DELS TEUS MÒDULS ---
try:
    from usuarios import gestionar_sesion, verificar_cuota, registrar_uso_gratis
    from pagos import mostrar_pago
    from ingenieria import obtener_manual_formulas
except ImportError as e:
    st.error(f"Falten fitxers al GitHub: {e}")
    st.stop()

# 1. CONFIGURACIÓ DE L'API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="ScopeAI Ultimate", layout="wide", page_icon="💎")

# --- LOGIN OBLIGATORI ---
gestionar_sesion()

st.title("🏗️ ScopeAI Enterprise")

# Inicialitzar historial
if 'history' not in st.session_state: 
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panell de Control")
    st.write(f"👤 Usuari: **{st.session_state.get('user', 'Usuari')}**")
    
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
    
    es_urgent = st.toggle("🚨 Urgència 24h", value=False)
    p_final_visita = c_visita * 1.5 if es_urgent else c_visita

# --- DASHBOARD ---
if st.session_state.history:
    st.markdown("### 📊 Resum d'Activitat")
    df_h = pd.DataFrame(st.session_state.history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressupostos", len(df_h))
    c2.metric("Estalvi CO2", f"{len(df_h)*1.2:.1f} kg")
    c3.metric("Estat Flota", "🟢 Operativa")
    st.markdown("---")

# --- NOVA INSPECCIÓ ---
st.subheader("📸 Nova Inspecció")
notas = st.text_area("Información técnica", placeholder="Escriu o descriu l'avaria...")
archivo = st.file_uploader("Subir vídeo o foto", type=['mp4', 'mov', 'jpg', 'png', 'jpeg'])

if archivo:
    st.success(f"Arxiu detectat: {archivo.name}")
    
    if st.button("🚀 EJECUTAR ANÀLISI COMPLETA"):
        # VERIFICACIÓ DE QUOTA
        tiene_gratis = verificar_cuota()
        pago_ok = False
        
        if not tiene_gratis:
            pago_ok = mostrar_pago()
        
        if tiene_gratis or pago_ok:
            with st.status("Processant anàlisi d'enginyeria..."):
                try:
                    # Guardar fitxer temporal
                    suffix = os.path.splitext(archivo.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                        tfile.write(archivo.read())
                        temp_path = tfile.name

                    # Pujar a Gemini
                    file_uploaded = genai.upload_file(path=temp_path)
                    while file_uploaded.state.name == "PROCESSING":
                        time.sleep(2)
                        file_uploaded = genai.get_file(file_uploaded.name)

                    # Carregar fórmules d'enginyeria
                    manual_formulas = obtener_manual_formulas()

                    model = genai.GenerativeModel(model_name=model_triat)
                    prompt = f"""
                    ERES INGENIERO SENIOR Y PERITO.
                    USA ESTAS FÓRMULAS PARA TUS CÁLCULOS:
                    {manual_formulas}

                    DATOS: Ubicación: {loc_actual} | Urgencia: {es_urgent} | Notas: {notas}
                    INVENTARIO: {inv_data}
                    COSTES: Visita {p_final_visita}€, Mano obra {c_hora}€/h.

                    TAREA: 
                    1. Diagnóstico técnico.
                    2. IA Safety Scan (!!! ALERTA !!!).
                    3. Búsqueda externa con enlaces si no hay stock.
                    4. Presupuesto detallado con IVA 21%.
                    5. Responde en CATALÀ.
                    """

                    respuesta = model.generate_content([prompt, file_uploaded])
                    
                    if respuesta.text:
                        st.markdown("---")
                        st.markdown(respuesta.text)
                        
                        # --- GENERACIÓ DE PDF (REVISADA) ---
                        try:
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", 'B', 16)
                            pdf.cell(0, 10, "Informe Tecnico ScopeAI", ln=True, align='C')
                            pdf.set_font("Arial", size=10)
                            pdf.ln(10)
                            
                            # Netegem el text per evitar errors de caràcters especials al PDF
                            clean_text = respuesta.text.encode('latin-1', 'replace').decode('latin-1')
                            pdf.multi_cell(0, 5, txt=clean_text)
                            
                            pdf_output = "informe_generado.pdf"
                            pdf.output(pdf_output)
                            
                            with open(pdf_output, "rb") as f:
                                st.download_button(
                                    label="📥 Baixar Informe en PDF",
                                    data=f,
                                    file_name=f"Informe_{st.session_state.user}.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as pdf_err:
                            st.error(f"No s'ha pogut generar el PDF: {pdf_err}")

                        # REGISTRE D'ÚS
                        if tiene_gratis:
                            registrar_uso_gratis()
                            st.toast("Crèdit gratuït utilitzat", icon="⏳")
                        
                        st.session_state.history.append({"Hora": time.strftime("%H:%M"), "Estat": "OK"})

                    # Neteja de fitxers
                    os.unlink(temp_path)
                    genai.delete_file(file_uploaded.name)

                except Exception as e:
                    st.error(f"Error en l'anàlisi: {e}")
        else:
            st.warning("🔒 Cal confirmar el pagament per continuar.")
