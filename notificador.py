import streamlit as st

def preparar_enviament_client(email_client, nom_pdf):
    # Aquí aniria la lògica de correu (SendGrid, Mailgun o Gmail)
    st.toast(f"📩 Informe preparat per enviar a: {email_client}", icon="📧")
    
def sidebar_notificacions():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📧 Notificacions")
    email = st.sidebar.text_input("Email del Client", placeholder="client@empresa.com")
    if st.sidebar.button("📧 Enviar Informe"):
        if email:
            st.sidebar.success(f"Enviat a {email}")
        else:
            st.sidebar.error("Introdueix un email")