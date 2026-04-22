import streamlit as st
import google.generativeai as genai

# 1. Configurar la conexión con la IA (usando el "Secret")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("ScopeAI: El Ojo del Ingeniero 🏗️")

# 2. Botón para subir el vídeo/foto
archivo = st.file_uploader("Sube el vídeo de la instalación", type=['mp4', 'mov', 'jpg', 'png'])

if archivo is not None:
    st.info("Analizando el archivo con Inteligencia Artificial...")
    
    # Mostrar el archivo
    if 'mp4' in archivo.name or 'mov' in archivo.name:
        st.video(archivo)
    else:
        st.image(archivo)

    # 3. La pregunta mágica (el "Prompt")
    if st.button("Calcular Mediciones"):
        # Convertimos el archivo para que Gemini lo entienda
        bytes_data = archivo.getvalue()
        
        # Le pedimos a la IA que analice
        response = model.generate_content([
            "Eres un experto en ingeniería. Mira este archivo y dime: 1. Qué materiales ves. 2. Una estimación de metros lineales. 3. Un presupuesto aproximado.",
            {"mime_type": archivo.type, "data": bytes_data}
        ])
        
        st.subheader("Resultado del Análisis:")
        st.write(response.text)
