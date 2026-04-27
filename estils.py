import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* 1. IMPORTACIÓ DE FONT PROFESSIONALS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* 2. CONFIGURACIÓ BASE (Neteja total) */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        .stApp {
            background-color: #F8FAFC !important; /* Gris ultra-clar tipus SaaS */
        }

        /* 3. SIDEBAR: NEGRE OLED INDUSTRIAL (Premium) */
        [data-testid="stSidebar"] {
            background-color: #09090B !important;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Forçar color de text a la sidebar */
        [data-testid="stSidebar"] * {
            color: #FAFAFA !important;
        }
        
        /* Inputs de la sidebar més elegants */
        [data-testid="stSidebar"] .stNumberInput input, 
        [data-testid="stSidebar"] .stSelectbox div {
            background-color: #18181B !important;
            border: 1px solid #27272A !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* 4. BOTÓ D'ACCIÓ: ESTIL APPLE / STRIPE */
        div.stButton > button {
            background-color: #18181B !important; /* Negre pur */
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 16px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            letter-spacing: -0.02em;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            width: 100% !important;
            margin-top: 20px;
        }

        div.stButton > button:hover {
            background-color: #27272A !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15) !important;
        }

        /* 5. TARGETA DE RESULTATS: "THE REPORT SHEET" */
        .premium-report {
            background-color: #FFFFFF !important;
            padding: 45px !important;
            border-radius: 24px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.05) !important;
            margin-top: 40px;
            color: #18181B !important;
        }

        .premium-report h2 {
            color: #18181B !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            letter-spacing: -0.05em !important;
            border-bottom: 2px solid #F1F5F9;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }

        /* 6. MÈTRIQUES (Dashboard nítid) */
        [data-testid="stMetric"] {
            background-color: white !important;
            border: 1px solid #F1F5F9 !important;
            padding: 20px !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        }

        /* 7. TEXT AREA I UPLOADER (Sense lila) */
        .stTextArea textarea {
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            padding: 15px !important;
        }
        
        .stFileUploader section {
            border-radius: 16px !important;
            border: 2px dashed #CBD5E1 !important;
            background-color: #FFFFFF !important;
        }

        /* Amagar el menú superior de Streamlit per més neteja */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="premium-report">
            <h2>{icona} {titol}</h2>
            <div style="font-size: 16px; line-height: 1.8; color: #3F3F46;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
