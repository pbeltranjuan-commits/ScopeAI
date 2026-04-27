import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* FORÇAR COLOR DE FONS */
        .stApp {
            background-color: #f1f5f9 !important;
        }

        /* FORÇAR SIDEBAR FOSCA */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }

        /* TÍTOL PRINCIPAL EN BLAU CORPORATIU */
        h1 {
            color: #1e3a8a !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }

        /* BOTÓ DE L'APP - EL FEM BLAU I GRAN */
        div.stButton > button:first-child {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            height: 50px !important;
            width: 100% !important;
            font-size: 18px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }

        /* CAIXA D'INFORMACIÓ TÈCNICA */
        .stTextArea textarea {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
        }

        /* TARGETA DE RESULTATS (La que veurem quan l'IA acabi) */
        .report-card {
            background-color: white !important;
            padding: 25px !important;
            border-radius: 15px !important;
            border-left: 8px solid #2563eb !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
            color: #1e293b !important;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="report-card">
            <h2 style="color:#1e3a8a; margin-top:0;">{icona} {titol}</h2>
            <div style="font-size: 16px; line-height: 1.6;">{contingut}</div>
        </div>
    """, unsafe_allow_html=True)
