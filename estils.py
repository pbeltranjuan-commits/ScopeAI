import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* FORÇAR FONS CLAR PREMIUM */
        .stApp {
            background: #F7F9FC !important;
        }

        /* SIDEBAR NEGRE OLED SENSE MARGES ESTRANYS */
        [data-testid="stSidebar"] {
            background-color: #09090B !important;
            color: #FAFAFA !important;
        }

        /* BOTÓ ESTIL APPLE/STRIPE */
        div.stButton > button {
            background-color: #18181B !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            width: 100% !important;
        }

        /* TARGETES DE RESULTATS BLANQUES AMB OMBRA SUAU */
        .premium-report {
            background: white !important;
            border-radius: 16px !important;
            padding: 35px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
            border: 1px solid #F1F5F9 !important;
            color: #18181B !important;
        }

        /* ELIMINAR EL COLOR VERMELL/LILA DELS TÍTOLS */
        h1, h2, h3 {
            color: #18181B !important;
            letter-spacing: -0.05em !important;
        }
        </style>
    """, unsafe_allow_html=True)
