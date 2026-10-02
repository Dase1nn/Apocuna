import streamlit as st
from utils.loaders import load_eventos
from components.cards import render_eventos_grid

def render_eventos():
    st.title("📅 Calendario de Eventos y Publicaciones")
    st.markdown("Revistas indexadas y congresos especializados para la difusión y deliberación en políticas públicas y gobernanza.")
    
    eventos = load_eventos()
    if not eventos:
        st.info("No se encontraron registros en data/eventos.json.")
        return
        
    # Filtros interactivos
    col1, col2 = st.columns([1, 2])
    with col1:
        tipo_filtro = st.selectbox(
            "Filtrar por tipo:",
            ["Todos", "Revistas", "Congresos"]
        )
    with col2:
        busqueda = st.text_input(
            "Buscar por temática o título:",
            placeholder="Ej: Gobernanza, Escolar, Descentralización, Educación..."
        )
        
    # Aplicar filtros
    eventos_filtrados = eventos
    
    if tipo_filtro == "Revistas":
        eventos_filtrados = [e for e in eventos_filtrados if e.get("tipo") == "revista"]
    elif tipo_filtro == "Congresos":
        eventos_filtrados = [e for e in eventos_filtrados if e.get("tipo") == "congreso"]
        
    if busqueda:
        b_lower = busqueda.lower().strip()
        eventos_filtrados = [
            e for e in eventos_filtrados 
            if b_lower in e.get("titulo", "").lower() 
            or b_lower in e.get("tematica", "").lower() 
            or b_lower in e.get("descripcion", "").lower()
        ]
        
    st.caption(f"Mostrando **{len(eventos_filtrados)}** de **{len(eventos)}** convocatorias registradas.")
    st.markdown("---")
    
    render_eventos_grid(eventos_filtrados)
