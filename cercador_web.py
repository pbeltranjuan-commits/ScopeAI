import streamlit as st
import random

def cercar_preus_reals(peça_clau):
    """
    Simula una cerca en temps real a bases de dades de subministraments 
    industrials (RS, ManoMano, Amazon Business).
    """
    # En una versió Pro, aquí connectaríem amb l'API de Google o Tavily
    # Per ara, creem un cercador intel·ligent que l'IA farà servir
    
    bases_de_dades = ["RS Components", "ManoMano", "Amazon Business", "Bauhaus Professional"]
    
    # Simulem la cerca de mercat
    preu_estimat = random.uniform(15.0, 450.0)
    font = random.choice(bases_de_dades)
    
    resultat = {
        "peça": peça_clau,
        "preu_mercat": round(preu_estimat, 2),
        "font": font,
        "disponibilitat": "En estoc (Enviament 24h)"
    }
    
    return resultat

def mostrar_targeta_preu(dades):
    """Renderitza una caixa visual premium amb la dada trobada"""
    st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 5px solid #18181B; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <p style="margin:0; font-size: 12px; color: #6B7280; text-transform: uppercase;">Font: {dades['font']}</p>
            <h4 style="margin:5px 0; color: #111827;">{dades['peça']}</h4>
            <p style="margin:0; font-weight: 700; color: #18181B; font-size: 18px;">{dades['preu_mercat']} € <span style="font-size: 12px; font-weight: 400; color: #10B981;">{dades['disponibilitat']}</span></p>
        </div>
    """, unsafe_allow_html=True)