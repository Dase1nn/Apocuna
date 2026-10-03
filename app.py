import streamlit as st
import os

# Configuración de página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Apocuna Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto"
)

# No explicit theme state needed

from components.sidebar import render_sidebar
from sections.home import render_home
from sections.polity import render_polity
from sections.estudiantes import render_estudiantes
from sections.notas import render_notas
from sections.eventos import render_eventos
from sections.sobre_el_sitio import render_sobre_el_sitio

def load_css():
    """Carga los estilos personalizados de Snowsight dinámicamente."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # Renderizamos sidebar primero para que el toggle actualice el state
    render_sidebar()
    # Cargamos CSS inyectando las variables del tema
    load_css()

    
    current = st.session_state.get("current_page", "Inicio")
    
    # Enrutador
    if current == "Inicio":
        render_home()
    elif current == "Polity and Policy":
        render_polity()
    elif current in ["Estudiantes (DEMO)", "Estudiantes"]:
        render_estudiantes()
    elif current == "Notas":
        render_notas()
    elif current == "Eventos":
        render_eventos()
    elif current == "Sobre el sitio":
        render_sobre_el_sitio()

if __name__ == "__main__":
    main()
