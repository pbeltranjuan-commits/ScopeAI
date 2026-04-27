import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* 1. NETEJA TOTAL I TIPOGRAFIA INTER */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .stApp {
            background-color: #F8FAFC !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* 2. SIDEBAR NEGRE OLED (PROFESSIONAL) */
        [data-testid="stSidebar"] {
            background-color: #09090B !important;
            border-right: 1px solid #E2E8F0;
        }
        
        [data-testid="stSidebar"] * {
            color: #FAFAFA !important;
        }

        /* 3. TARGETES DE DADES 'FLOATING WHITE' */
        .stMetric {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            border: 1px solid #F1F5F9 !important;
        }

        /* 4. EL BOTÓ 'PREMIUM' (NEGRE I ARRODONIT) */
        div.stButton > button {
            background-color: #18181B !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.2s ease;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        }

        div.stButton > button:hover {
            background-color: #27272A !important;
            transform: translateY(-1px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
        }

        /* 5. INFORME FINAL (ESTIL DOCUMENT PERICIAL) */
        .premium-report {
            background-color: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.05) !important;
            margin-top: 30px;
        }

        .premium-report h2 {
            color: #18181B !important;
            border-bottom: 2px solid #F1F5F9;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-weight: 700;
        }

        /* 6. INPUTS NETS */
        .stTextArea textarea {
            border-radius: 10px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="premium-report">
            <h2>{icona} {titol}</h2>
            <div style="color: #3F3F46; line-height: 1.7; font-size: 16px;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
