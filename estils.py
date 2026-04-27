import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* Font global */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }

        /* Fons de la pàgina */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        }

        /* Sidebar estil "Dark Glass" */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b;
        }
        
        [data-testid="stSidebar"] section {
            background-color: transparent !important;
        }

        /* Botó principal (Cridaner i Modern) */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
            filter: brightness(1.1);
        }

        /* Targetes de resultats (Estil Notion) */
        .report-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin: 20px 0;
            line-height: 1.6;
        }

        .report-card h3 {
            color: #1e293b;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Mètriques (Dashboard) */
        [data-testid="stMetricValue"] {
            font-weight: 800;
            color: #2563eb;
        }
        
        [data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #64748b;
        }

        /* Estil per als inputs i file uploader */
        section[data-testid="stFileUploadDropzone"] {
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            background: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    """Crea un bloc visualment separat per als resultats de la IA"""
    st.markdown(f"""
        <div class="report-card">
            <h3>{icona} {titol}</h3>
            <div style="color: #334155;">
                {contingut}
            </div>
        </div>
    """, unsafe_allow_html=True)