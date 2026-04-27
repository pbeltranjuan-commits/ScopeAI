import streamlit as st

def aplicar_estils_personalitzats():
    st.markdown("""
        <style>
        /* Fons global més suau */
        .stApp {
            background-color: #f8fafc;
        }

        /* Sidebar: anem a lo segur, només el color de fons */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }
        
        /* Arreglar el color dels textos de la Sidebar per llegir-los bé */
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
            color: #f8fafc !important;
        }

        /* Targeta de resultats neta i sense errors de superposició */
        .report-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            color: #1e293b;
        }

        .report-card h3 {
            color: #2563eb !important;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def caixa_analisi(titol, icona, contingut):
    st.markdown(f"""
        <div class="report-card">
            <h3>{icona} {titol}</h3>
            <div style="white-space: pre-wrap;">{contingut}</div>
        </div>
    """, unsafe_allow_html=True)
