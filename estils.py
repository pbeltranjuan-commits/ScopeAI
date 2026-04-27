import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* 1. TIPOGRAFIA DE LUXE (Inter, la més usada en SaaS Premium) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* 2. FONS PRINCIPAL LLUMINÓS I NET */
        .stApp {
            background-color: #F7F9FC !important; /* Gris-blau extremadament suau */
        }

        /* 3. SIDEBAR: NEGRE OLED (Contrast Premium) */
        [data-testid="stSidebar"] {
            background-color: #09090B !important; /* Negre pur / OLED */
            border-right: none !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #A1A1AA !important; /* Text secundari gris elegant */
        }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] strong {
            color: #FAFAFA !important; /* Text principal blanc pur */
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }

        /* 4. TARGETES METRIQUES (Estil Flotant) */
        div[data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            color: #18181B !important;
            letter-spacing: -1px;
        }
        
        .stMetric {
            background-color: #FFFFFF !important;
            padding: 24px !important;
            border-radius: 16px !important;
            border: 1px solid #F4F4F5 !important;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.04) !important;
            transition: transform 0.2s ease;
        }
        
        .stMetric:hover {
            transform: translateY(-2px);
        }

        /* 5. INPUTS I ZONES DE TEXT (Arrodonits i nets) */
        .stTextArea textarea, .stTextInput input, .stNumberInput input {
            background-color: #FFFFFF !important;
            border: 1px solid #E4E4E7 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            color: #18181B !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important;
        }
        
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #18181B !important;
            box-shadow: 0 0 0 1px #18181B !important;
        }

        /* 6. EL BOTÓ D'ACCIÓ PRINCIPAL (Negre absolut, botó Apple) */
        div.stButton > button {
            background-color: #18181B !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            width: 100%;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 14px 0 rgba(0,0,0,0.1) !important;
        }

        div.stButton > button:hover {
            background-color: #27272A !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
            transform: scale(1.01);
        }

        /* 7. LA CAIXA D'INFORME FINAL (Paper d'alta qualitat) */
        .premium-report {
            background-color: #FFFFFF;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05);
            border: 1px solid #F4F4F5;
            margin-top: 2rem;
        }
        
        .premium-report h2 {
            color: #18181B;
            font-weight: 700;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #F4F4F5;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .premium-report p, .premium-report li {
            color: #52525B;
            font-size: 16px;
            line-height: 1.8;
        }

        /* 8. FILE UPLOADER NET */
        .stFileUploader section {
            background-color: #FFFFFF !important;
            border: 2px dashed #E4E4E7 !important;
            border-radius: 16px !important;
            padding: 24px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="premium-report">
            <h2><span>{icona}</span> {titol}</h2>
            <div class="report-content">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
