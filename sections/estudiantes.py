import streamlit as st
from utils.loaders import load_estudiantes, load_cursos, load_becas
from components.cards import render_polity_cards, render_estudiantes_apuntes, render_cursos_grid, render_becas_grid

def render_estudiantes():
    st.title("🎓 Estudiantes (DEMO)")
    st.markdown(
        '<div class="banner-demo-top">🚀 <strong>Sección Activa:</strong> '
        'Las categorías de esta sección se actualizan de forma automatizada (becas, cursos, revistas y eventos). Espacio para la formación metodológica e investigación.</div>',
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
        elif sub.get("id") == "est_sub_1":
            with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
                # Show the cards
                render_polity_cards(sub.get("tarjetas", []))
                st.markdown("---")
                st.subheader("Últimas Alertas Académicas (Automatizado)")
                from utils.loaders import load_academico
                from components.cards import render_ckan_carousel # re-using or creating a specific carousel
                # Wait, I need a specific carousel for academico or just render them. 
                # Let's import render_academico_carousel from cards.py
                from components.cards import render_academico_carousel
                academico_data = load_academico()
                render_academico_carousel(academico_data)
        elif sub.get("id") == "est_sub_2":
            with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
                render_polity_cards(sub.get("tarjetas", []))
                st.markdown("---")
                st.subheader("Catálogo de Cursos (Automatizado)")
                cursos = load_cursos()
                if cursos:
                    col1, col2 = st.columns(2)
                    with col1:
                        filtro_modalidad = st.selectbox("Modalidad:", ["Todas"] + list(set(c.get("modalidad", "") for c in cursos if c.get("modalidad"))))
                    with col2:
                        filtro_costo = st.selectbox("Costo:", ["Todos"] + list(set(c.get("costo", "") for c in cursos if c.get("costo"))))
                    
                    cursos_filtrados = cursos
                    if filtro_modalidad != "Todas":
                        cursos_filtrados = [c for c in cursos_filtrados if c.get("modalidad") == filtro_modalidad]
                    if filtro_costo != "Todos":
                        cursos_filtrados = [c for c in cursos_filtrados if c.get("costo") == filtro_costo]
                        
                    render_cursos_grid(cursos_filtrados)
                else:
                    st.info("No se encontraron cursos.")
        elif sub.get("id") == "est_sub_4":
            with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
                render_polity_cards(sub.get("tarjetas", []))
                st.markdown("---")
                st.subheader("Becas y Oportunidades (Automatizado)")
                becas = load_becas()
                if becas:
                    render_becas_grid(becas)
                else:
                    st.info("No se encontraron becas.")
        else:
            with st.expander(f"📌 {titulo_sub}", expanded=(idx == 0)):
                render_polity_cards(sub.get("tarjetas", []))
