import streamlit as st
from utils.loaders import load_polity
from components.cards import render_polity_cards

def render_polity():
    st.title("🏛️ Polity and Policy")
    st.markdown(
        "Insumos, metodologías y mecanismos de actualización indispensables para la formulación, "
        "ejecución y evaluación de políticas públicas en el Perú."
    )
    
    subsecciones = load_polity()
    
    if not subsecciones:
        st.info("No se encontró información en data/polity.json.")
        return
        
    for idx, sub in enumerate(subsecciones):
        titulo_sub = sub.get("subseccion", f"Subsección {idx + 1}")
        tarjetas = sub.get("tarjetas", [])
        
        # El primer bloque expandido por defecto para mejor visualización
        with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
            render_polity_cards(tarjetas)
