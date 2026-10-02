import streamlit as st
from utils.loaders import load_estudiantes
from components.cards import render_polity_cards, render_estudiantes_apuntes

def render_estudiantes():
    st.title("🎓 Estudiantes (Próximamente)")
    st.markdown(
        '<div class="banner-demo-top">🚧 <strong>Próximamente – versión demo:</strong> '
        'Espacio dedicado a la formación metodológica, investigación académica y archivo de apuntes para estudiantes de Ciencia Política, Gestión Pública y Economía.</div>',
        unsafe_allow_html=True
    )
    
    subsecciones = load_estudiantes()
    if not subsecciones:
        st.info("No se encontró información en data/estudiantes.json.")
        return
        
    for idx, sub in enumerate(subsecciones):
        titulo_sub = sub.get("subseccion", f"Subsección {idx + 1}")
        
        # Si es la subsección 5 de apuntes, renderizar con formato especializado de apuntes
        if "apuntes" in sub:
            with st.expander(f"📚 {titulo_sub}", expanded=True):
                st.markdown("Guías teóricas y normativas sobre los 11 sistemas administrativos del Estado peruano:")
                render_estudiantes_apuntes(sub.get("apuntes", []))
        else:
            with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
                render_polity_cards(sub.get("tarjetas", []))
