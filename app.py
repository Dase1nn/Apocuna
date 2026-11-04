import os
import streamlit as st

# Configuración de página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Apocuna Hub | Evidencia y Políticas Públicas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto"
)

from components.sidebar import render_sidebar
from sections.home import render_home
from sections.polity import render_polity
from sections.fen import render_fen
from sections.estudiantes import render_estudiantes
from sections.notas import render_notas
from sections.eventos import render_eventos
from sections.sobre_el_sitio import render_sobre_el_sitio

ROUTES = {
    "Inicio": render_home,
    "Polity and Policy": render_polity,
    "🌊 Fenómeno El Niño (FEN)": render_fen,
    "Fenómeno El Niño (FEN)": render_fen,
    "Estudiantes (DEMO)": render_estudiantes,
    "Estudiantes": render_estudiantes,
    "Notas": render_notas,
    "Eventos": render_eventos,
    "Sobre el sitio": render_sobre_el_sitio,
}


@st.cache_data(show_spinner=False)
def _get_cached_css(css_path: str, mtime: float) -> str:
    """Lee y cachea la hoja de estilos en memoria invalidando solo si cambia el archivo."""
    with open(css_path, "r", encoding="utf-8") as f:
        return f"<style>{f.read()}</style>"


def load_css():
    """Inyecta los estilos personalizados de Apocuna sin lecturas redundantes de disco."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        mtime = os.path.getmtime(css_path)
        st.markdown(_get_cached_css(css_path, mtime), unsafe_allow_html=True)


def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Inicio"

    render_sidebar()
    load_css()

    current = st.session_state.get("current_page", "Inicio")
    renderer = ROUTES.get(current, render_home)
    renderer()


if __name__ == "__main__":
    main()
