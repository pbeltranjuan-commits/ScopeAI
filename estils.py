import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* FONTS I FONS GENERAL */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Roboto', sans-serif;
        }

        /* SIDEBAR PROFESSIONAL */
        [data-testid="stSidebar"] {
            background-color: #1e293b !important;
            border-right: 1px solid #334155;
        }
        
        /* TEXTOS DE LA SIDEBAR (Arreglar el lila que no es llegeix) */
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }

        /* TITOLS */
        h1, h2, h3 {
            color: #38bdf8 !important;
            font-weight: 700 !important;
        }

        /* BOTONS PROFESSIONALS */
        div.stButton > button {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        div.stButton > button:hover {
            background: #0ea5e9 !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
            transform: translateY(-1px);
        }

        /* CAIXES DE TEXT I INPUTS */
        input, textarea, .stNumberInput div {
            background-color: #1e293b !important;
            color: white !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
        }

        /* TARGETA DE RESULTATS (L'informe que surt) */
        .report-card {
            background-color: #1e293b;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #38bdf8;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="report-card">
            <h2 style="margin-top:0; color:#38bdf8;">{icona} {titol}</h2>
            <div style="color:#f1f5f9; font-size:16px; line-height:1.6;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
