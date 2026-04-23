import streamlit as st

# Aquí pondrías tu Link de Pago de Stripe (Stripe Dashboard -> Payment Links)
STRIPE_LINK = "https://buy.stripe.com/tu_enlace_de_1_euro"

def mostrar_pago():
    st.warning("⚠️ Ya has agotado tu consulta gratuita de hoy.")
    st.info("Para realizar más análisis hoy, el coste es de **1€ por consulta**.")
    
    st.markdown(f"""
        <a href="{STRIPE_LINK}" target="_blank">
            <button style="background-color: #6772E5; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                Pagar 1€ con Stripe
            </button>
        </a>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.checkbox("✅ He realizado el pago correctamente"):
        st.success("Pago confirmado. Puedes proceder al análisis.")
        return True
    return False