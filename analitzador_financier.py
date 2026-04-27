import streamlit as st

def calcular_roi_reparacio(cost_reparacio):
    # Lògica: Una reparació preventiva sol estalviar 5 vegades el seu cost en danys majors
    estalvi_estimat = cost_reparacio * 5
    roi = ((estalvi_estimat - cost_reparacio) / cost_reparacio) * 100
    
    return {
        "estalvi": estalvi_estimat,
        "roi": roi,
        "urgencia": "ALTA" if roi > 300 else "MITJANA"
    }

def mostrar_targeta_financiera(cost):
    dades = calcular_roi_reparacio(cost)
    st.markdown(f"""
        <div style="background-color: #F0FDF4; padding: 20px; border-radius: 12px; border: 1px solid #BBF7D0; margin-top: 15px;">
            <h4 style="margin:0; color: #166534; font-size: 14px;">💰 ANÀLISI DE RENDIBILITAT</h4>
            <p style="margin: 5px 0; color: #14532D;">Estalvi preventiu estimat: <b>{dades['estalvi']} €</b></p>
            <div style="background-color: #166534; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; display: inline-block;">
                ROI: +{dades['roi']}%
            </div>
        </div>
    """, unsafe_allow_html=True)