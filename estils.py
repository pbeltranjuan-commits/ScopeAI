import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* 1. FONTS I FONS GENERAL (Claredat total) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        .stApp {
            background-color: #F8FAFC !important; /* Gris molt clar, gairebé blanc */
            color: #1E293B !important; /* Text gris fosc, no negre pur */
            font-family: 'Inter', sans-serif !important;
        }

        /* 2. SIDEBAR PROFESSIONAL (Blau Marí Corporatiu) */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important; /* Blau molt fosc elegant */
            border-right: 1px solid #E2E8F0;
        }
        
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] label {
            color: #F8FAFC !important; /* Text blanc a la sidebar */
            font-weight: 500;
        }

        /* 3. TÍTOLS */
        h1, h2, h3 {
            color: #0F172A !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }

        /* 4. BOTONS D'ACCIO (Estil SaaS modern) */
        div.stButton > button {
            background-color: #2563EB !important; /* Blau elèctric professional */
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            transition: background 0.2s ease;
            width: 100%;
        }

        div.stButton > button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }

        /* 5. TARGETA DE RESULTATS (L'Informe) */
        .report-card {
            background-color: #FFFFFF !important;
            padding: 30px !important;
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            margin-top: 20px;
        }

        /* 6. INPUTS (Més nets) */
        .stTextArea textarea, .stNumberInput input {
            background-color: white !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            color: #1E293B !important;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="report-card">
            <h3 style="margin-top:0; color:#2563EB;">{icona} {titol}</h3>
            <div style="color:#334155; font-size:16px; line-height:1.6;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
