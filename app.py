import streamlit as st

st.title("MetricBuild: Presupuestos de Ingeniería 🛠️")
st.write("Bienvenido. Sube tu vídeo para empezar el cálculo.")

# Un pequeño formulario de prueba
metros = st.number_input("¿Cuántos metros mide la instalación?", min_value=0.0)
if st.button("Calcular presupuesto"):
    # Aquí es donde Python hace su magia matemática
    resultado = metros * 25  # Ejemplo: 25€ por metro
    st.success(f"El presupuesto exacto es: {resultado} €")