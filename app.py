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

DARK_THEME_OVERRIDE_CSS = """
<style id="apocuna-theme-override-dark">
:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
    color-scheme: dark !important;
    --surface-bg: #151B26 !important;
    --surface-elevated: #1C2433 !important;
    --surface-hover: #1F293B !important;
    --surface-border: rgba(41, 181, 232, 0.22) !important;
    --surface-border-hover: rgba(56, 189, 248, 0.58) !important;
    --text-title: #F8FAFC !important;
    --text-body: #CBD5E1 !important;
    --text-muted: #94A3B8 !important;
    --text-accent: #38BDF8 !important;
    --shadow-card: 0 4px 16px rgba(0, 0, 0, 0.35), 0 1px 3px rgba(0, 0, 0, 0.22) !important;
    --shadow-card-hover: 0 12px 28px rgba(41, 181, 232, 0.2), 0 4px 12px rgba(0, 0, 0, 0.42) !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0E1117 !important;
    color: #F8FAFC !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #151B26 !important;
    color: #F8FAFC !important;
    border-right: 1px solid rgba(41, 181, 232, 0.16) !important;
}
[data-testid="stSidebar"] iframe[title="streamlit_option_menu.option_menu"] {
    background-color: #151B26 !important;
    color-scheme: dark !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: #1C2433 !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(41, 181, 232, 0.28) !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background-color: #1F293B !important;
    border-color: #38BDF8 !important;
    color: #38BDF8 !important;
}
[data-testid="stExpander"], [data-testid="stExpander"] details {
    background-color: #151B26 !important;
    border-color: rgba(41, 181, 232, 0.22) !important;
    color: #F8FAFC !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
    color: #F8FAFC !important;
}
header[data-testid="stHeader"] {
    background: rgba(14, 17, 23, 0.9) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] strong {
    color: #F8FAFC !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #E2E8F0 !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #94A3B8 !important;
}
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] {
    background-color: #1C2433 !important;
    color: #F8FAFC !important;
    border-color: rgba(41, 181, 232, 0.28) !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
}
div[data-baseweb="input"] input::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #94A3B8 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #38BDF8 !important;
}
[data-testid="stButtonGroup"] button {
    background-color: #1C2433 !important;
    color: #E2E8F0 !important;
    border-color: rgba(41, 181, 232, 0.28) !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
    background-color: rgba(41, 181, 232, 0.24) !important;
    color: #38BDF8 !important;
    border-color: #29B5E8 !important;
}
</style>
"""

LIGHT_THEME_OVERRIDE_CSS = """
<style id="apocuna-theme-override-light">
:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
    color-scheme: light !important;
    --surface-bg: #FFFFFF !important;
    --surface-elevated: #F8FAFC !important;
    --surface-hover: #F1F5F9 !important;
    --surface-border: rgba(15, 23, 42, 0.12) !important;
    --surface-border-hover: rgba(2, 132, 199, 0.5) !important;
    --text-title: #0F172A !important;
    --text-body: #334155 !important;
    --text-muted: #64748B !important;
    --text-accent: #0369A1 !important;
    --shadow-card: 0 2px 8px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    --shadow-card-hover: 0 10px 24px rgba(2, 132, 199, 0.14), 0 4px 8px rgba(15, 23, 42, 0.06) !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-right: 1px solid rgba(15, 23, 42, 0.1) !important;
}
[data-testid="stSidebar"] iframe[title="streamlit_option_menu.option_menu"] {
    background-color: #FFFFFF !important;
    color-scheme: light !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid rgba(15, 23, 42, 0.16) !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background-color: #F1F5F9 !important;
    border-color: #0284C7 !important;
    color: #0369A1 !important;
}
[data-testid="stExpander"], [data-testid="stExpander"] details {
    background-color: #FFFFFF !important;
    border-color: rgba(15, 23, 42, 0.12) !important;
    color: #0F172A !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
    color: #0F172A !important;
}
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.94) !important;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08) !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] strong {
    color: #0F172A !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #334155 !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #475569 !important;
}
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-color: rgba(15, 23, 42, 0.18) !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}
div[data-baseweb="input"] input::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #475569 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #0369A1 !important;
}
[data-testid="stButtonGroup"] button {
    background-color: #F1F5F9 !important;
    color: #334155 !important;
    border-color: rgba(15, 23, 42, 0.15) !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
    background-color: rgba(2, 132, 199, 0.15) !important;
    color: #0369A1 !important;
    border-color: #0284C7 !important;
}
</style>
"""


@st.cache_data(show_spinner=False)
def _get_cached_css(css_path: str, mtime: float) -> str:
    """Lee y cachea la hoja de estilos en memoria invalidando solo si cambia el archivo."""
    with open(css_path, "r", encoding="utf-8") as f:
        return f"<style>{f.read()}</style>"


def load_css():
    """Inyecta los estilos personalizados de Apocuna y el modo de tema seleccionado."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        mtime = os.path.getmtime(css_path)
        st.markdown(_get_cached_css(css_path, mtime), unsafe_allow_html=True)

    theme_mode = st.session_state.get("theme_mode", "💻 Auto")
    if theme_mode == "🌙 Oscuro":
        st.markdown(DARK_THEME_OVERRIDE_CSS, unsafe_allow_html=True)
    elif theme_mode == "☀️ Claro":
        st.markdown(LIGHT_THEME_OVERRIDE_CSS, unsafe_allow_html=True)


def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Inicio"
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "💻 Auto"

    render_sidebar()
    load_css()

    current = st.session_state.get("current_page", "Inicio")
    renderer = ROUTES.get(current, render_home)
    renderer()


if __name__ == "__main__":
    main()
