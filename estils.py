import streamlit as st

def aplicar_estils_personalitzats():
    # Injecció forçada: això "mata" qualsevol disseny previ de Streamlit
    st.markdown("""
        <style>
        /* 1. ELIMINAR EL COLOR LILA/BLAU PER DEFECTE */
        :root {
            --primary-color: #18181B;
        }

        /* 2. FONS DE PÀGINA NET (Estil Apple) */
        .stApp {
            background-color: #F8FAFC !important;
        }

        /* 3. SIDEBAR NEGRE OLED (Aquest és el canvi més gran) */
        [data-testid="stSidebar"] {
            background-color: #09090B !important;
            border-right: 1px solid #E2E8F0 !important;
            min-width: 300px !important;
        }
        
        /* Forçar text blanc a la sidebar */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: #FAFAFA !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* 4. TARGETES BLANQUES (Mètriques) */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            padding: 20px !important;
        }

        /* 5. BOTÓ NEGRE MINIMALISTA */
        div.stButton > button {
            background-color: #18181B !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid #18181B !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button:hover {
            background-color: #3F3F46 !important;
            border-color: #3F3F46 !important;
            transform: translateY(-1px);
        }

        /* 6. CAIXA D'INFORME (Efecte Full de Paper) */
        .premium-card {
            background: white !important;
            padding: 35px !important;
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.03) !important;
            margin-top: 25px;
            color: #18181B !important;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="premium-card">
            <h2 style="color: #18181B; margin-top: 0; font-weight: 700;">{icona} {titol}</h2>
            <hr style="border: 0; border-top: 1px solid #F1F5F9; margin: 15px 0;">
            <div style="font-size: 16px; line-height: 1.7; color: #4B5563;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)
