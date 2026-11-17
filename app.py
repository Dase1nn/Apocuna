import importlib
import os
import streamlit as st

# Configuración de página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Apocuna Hub | Evidencia y Políticas Públicas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto"
)

import utils.loaders as _loaders_mod
if getattr(_loaders_mod, "LOADERS_VERSION", None) != "2026-11-16-sec":
    importlib.reload(_loaders_mod)

from components.sidebar import render_sidebar
from sections.home import render_home
from sections.rastrea_la_norma import render_rastrea_la_norma
from sections.polity import render_polity
from sections.fen import render_fen
from sections.biblioteca import render_biblioteca
from sections.estudiantes import render_estudiantes
from sections.sobre_el_sitio import render_sobre_el_sitio
from sections.busqueda_global import render_busqueda_global

from utils.loaders import load_dashboard_kpis, sanitize_slug_param

ROUTES = {
    "Inicio": render_home,
    "Rastrea la Norma": render_rastrea_la_norma,
    "Políticas y Datos": render_polity,
    "Polity and Policy": render_polity,
    "Monitoreo El Niño": render_fen,
    "🌊 Fenómeno El Niño (FEN)": render_fen,
    "Fenómeno El Niño (FEN)": render_fen,
    "Biblioteca y Revistas": render_biblioteca,
    "Notas": render_biblioteca,
    "Eventos": render_biblioteca,
    "Escuela y Becas": render_estudiantes,
    "Estudiantes (DEMO)": render_estudiantes,
    "Estudiantes": render_estudiantes,
    "Sobre Apocuna": render_sobre_el_sitio,
    "Sobre el sitio": render_sobre_el_sitio,
}

_DARK_RULES_BODY = """
:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
    color-scheme: dark !important;
    --surface-bg: #181D1A !important;
    --surface-elevated: #202723 !important;
    --surface-hover: #262F2A !important;
    --surface-border: #4A5750 !important;
    --surface-border-hover: #F0BB38 !important;
    --text-title: #FAF7E9 !important;
    --text-body: #DCE0DB !important;
    --text-muted: #A3B0A8 !important;
    --text-accent: #5AB0E6 !important;
    --shadow-card: 3px 3px 0px #080A09 !important;
    --shadow-card-hover: 5px 5px 0px #F0BB38 !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #121614 !important;
    color: #FAF7E9 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #181D1A !important;
    color: #FAF7E9 !important;
    border-right: 2px solid #4A5750 !important;
}
[data-testid="stSidebar"] iframe[title="streamlit_option_menu.option_menu"] {
    background-color: #181D1A !important;
    color-scheme: dark !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"],
div[data-testid="stButton"] > button {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #4A5750 !important;
    border-left: 5px solid #F0BB38 !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"]:hover,
div[data-testid="stButton"] > button:hover {
    background-color: #262F2A !important;
    border-color: #F0BB38 !important;
    color: #F0BB38 !important;
}
.btn-open,
.norma-btn-primary {
    background: #2775AA !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #FAF7E9 !important;
    box-shadow: 2px 2px 0px #080A09 !important;
}
.btn-open:hover,
.norma-btn-primary:hover {
    background: #F0BB38 !important;
    color: #171B18 !important;
    border-color: #171B18 !important;
    box-shadow: 3px 3px 0px #080A09 !important;
}
.norma-eje-policy .norma-btn-primary {
    background: #1B8668 !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #FAF7E9 !important;
}
.norma-btn-ghost,
.btn-fen-secondary,
.btn-ficha-tecnica {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #4A5750 !important;
    border-left: 4px solid #F0BB38 !important;
}
.norma-btn-ghost:hover,
.btn-fen-secondary:hover,
.btn-ficha-tecnica:hover {
    background-color: #262F2A !important;
    border-color: #F0BB38 !important;
    color: #F0BB38 !important;
}
.ficha-tecnica-hero,
.ficha-ref-card {
    background-color: #181D1A !important;
    border-color: #4A5750 !important;
    color: #FAF7E9 !important;
}
.ficha-format-chip,
.badge-tipo {
    background-color: #262F2A !important;
    color: #FAF7E9 !important;
    border-color: #4A5750 !important;
}
.legend-item-row {
    background-color: #202723 !important;
    color: #DCE0DB !important;
    border-color: #4A5750 !important;
}
.badge-freq-anual {
    background-color: rgba(240, 187, 56, 0.18) !important;
    color: #F0BB38 !important;
    border-color: #F0BB38 !important;
}
.badge-freq-permanente {
    background-color: rgba(163, 176, 168, 0.16) !important;
    color: #DCE0DB !important;
    border-color: #A3B0A8 !important;
}
[data-testid="stExpander"],
[data-testid="stExpander"] details {
    background-color: #181D1A !important;
    border: 1.5px solid #4A5750 !important;
    color: #FAF7E9 !important;
    border-radius: 0px !important;
}
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] details > summary:focus,
[data-testid="stExpander"] details > summary:active {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    border-radius: 0px !important;
}
[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpander"] details[open] > summary:hover,
[data-testid="stExpander"] details[open] > summary:focus {
    background-color: #262F2A !important;
    color: #FAF7E9 !important;
    border-bottom: 1.5px solid #4A5750 !important;
}
[data-testid="stExpander"] details > summary *,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    background-color: transparent !important;
    color: #FAF7E9 !important;
    fill: #FAF7E9 !important;
}
header[data-testid="stHeader"] {
    background: #121614 !important;
    border-bottom: 2px solid #4A5750 !important;
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
    color: #FAF7E9 !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p {
    color: #DCE0DB !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #A3B0A8 !important;
}
code, [data-testid="stMarkdownContainer"] code, .flow-step-desc code {
    background-color: #262F2A !important;
    color: #F0BB38 !important;
    border: 1px solid #4A5750 !important;
    padding: 0.1rem 0.3rem !important;
    border-radius: 0px !important;
}
/* Inputs y Selectboxes en Modo Oscuro */
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] .react-aria-ComboBox > div[role="group"],
[data-testid="stMultiSelect"] .react-aria-ComboBox > div[role="group"] {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    border-color: #4A5750 !important;
    border-radius: 0px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
[data-testid="stSelectbox"] input[role="combobox"],
[data-testid="stSelectbox"] button,
[data-testid="stMultiSelect"] input[role="combobox"],
[data-testid="stMultiSelect"] button {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    -webkit-text-fill-color: #FAF7E9 !important;
    caret-color: #FAF7E9 !important;
}
div[data-baseweb="select"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stMultiSelect"] svg {
    fill: #FAF7E9 !important;
    color: #FAF7E9 !important;
}
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="base-input"] input::placeholder,
[data-testid="stSelectbox"] input::placeholder {
    color: #A3B0A8 !important;
    -webkit-text-fill-color: #A3B0A8 !important;
    opacity: 1 !important;
}
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"],
.react-aria-Popover,
.react-aria-ListBox,
.react-aria-ListBoxItem,
div[role="listbox"],
div[role="option"] {
    background-color: #202723 !important;
    color: #FAF7E9 !important;
    border-radius: 0px !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"],
.react-aria-ListBoxItem[data-focused],
.react-aria-ListBoxItem[data-selected],
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background-color: #262F2A !important;
    color: #F0BB38 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #A3B0A8 !important;
    background-color: transparent !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #F0BB38 !important;
    border-bottom: 3px solid #F0BB38 !important;
}
[data-testid="stButtonGroup"] button {
    background-color: #202723 !important;
    color: #DCE0DB !important;
    border: 1.5px solid #4A5750 !important;
    border-radius: 0px !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
    background-color: #F0BB38 !important;
    color: #171B18 !important;
    border-color: #FAF7E9 !important;
    font-weight: 800 !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"] *,
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] * {
    color: #171B18 !important;
}
.flow-step-card,
.flow-telemetry-chip {
    background-color: #181D1A !important;
    border-color: #4A5750 !important;
    color: #FAF7E9 !important;
}
.sidebar-logo-frame,
.apocunoso-hero-logo {
    box-shadow: 3px 3px 0px #F0BB38 !important;
}
"""

_LIGHT_RULES_BODY = """
:root, html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
    color-scheme: light !important;
    --surface-bg: #FAF7E9 !important;
    --surface-elevated: #F2EFE0 !important;
    --surface-hover: #EAE5D1 !important;
    --surface-border: #171B18 !important;
    --surface-border-hover: #2775AA !important;
    --text-title: #171B18 !important;
    --text-body: #252B27 !important;
    --text-muted: #4E5752 !important;
    --text-accent: #1E5D88 !important;
    --shadow-card: 3px 3px 0px #171B18 !important;
    --shadow-card-hover: 5px 5px 0px #171B18 !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #F2EFE0 !important;
    color: #171B18 !important;
    border-right: 2px solid #171B18 !important;
}
[data-testid="stSidebar"] iframe[title="streamlit_option_menu.option_menu"] {
    background-color: #F2EFE0 !important;
    color-scheme: light !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"],
div[data-testid="stButton"] > button {
    background-color: #F2EFE0 !important;
    color: #171B18 !important;
    border: 1.5px solid #171B18 !important;
    border-left: 5px solid #1B8668 !important;
    border-radius: 0px !important;
}
[data-testid="stBaseButton-secondary"]:hover,
div[data-testid="stButton"] > button:hover {
    background-color: #EAE5D1 !important;
    border-color: #2775AA !important;
    color: #1E5D88 !important;
}
.btn-open,
.norma-btn-primary {
    background: #171B18 !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #171B18 !important;
    box-shadow: 2px 2px 0px #2775AA !important;
}
.btn-open:hover,
.norma-btn-primary:hover {
    background: #2775AA !important;
    color: #FAF7E9 !important;
    border-color: #171B18 !important;
    box-shadow: 3px 3px 0px #171B18 !important;
}
.norma-eje-policy .norma-btn-primary {
    background: #1B8668 !important;
    color: #FAF7E9 !important;
    border: 1.5px solid #171B18 !important;
}
.norma-btn-ghost,
.btn-fen-secondary,
.btn-ficha-tecnica {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
    border: 1.5px solid #171B18 !important;
    border-left: 4px solid #1B8668 !important;
}
.norma-btn-ghost:hover,
.btn-fen-secondary:hover,
.btn-ficha-tecnica:hover {
    background-color: #EAE5D1 !important;
    border-color: #1B8668 !important;
    color: #171B18 !important;
}
.ficha-tecnica-hero,
.ficha-ref-card {
    background-color: #FAF7E9 !important;
    border-color: #171B18 !important;
    color: #171B18 !important;
}
.ficha-format-chip,
.badge-tipo {
    background-color: #EAE5D1 !important;
    color: #171B18 !important;
    border-color: #171B18 !important;
}
.legend-item-row {
    background-color: #F2EFE0 !important;
    color: #252B27 !important;
    border-color: #171B18 !important;
}
.badge-freq-anual {
    background-color: rgba(240, 187, 56, 0.24) !important;
    color: #171B18 !important;
    border-color: #171B18 !important;
}
.badge-freq-permanente {
    background-color: rgba(78, 87, 82, 0.12) !important;
    color: #252B27 !important;
    border-color: #4E5752 !important;
}
[data-testid="stExpander"],
[data-testid="stExpander"] details {
    background-color: #FAF7E9 !important;
    border: 1.5px solid #171B18 !important;
    color: #171B18 !important;
    border-radius: 0px !important;
}
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] details > summary:focus,
[data-testid="stExpander"] details > summary:active {
    background-color: #F2EFE0 !important;
    color: #171B18 !important;
    border-radius: 0px !important;
}
[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpander"] details[open] > summary:hover,
[data-testid="stExpander"] details[open] > summary:focus {
    background-color: #EAE5D1 !important;
    color: #171B18 !important;
    border-bottom: 1.5px solid #171B18 !important;
}
[data-testid="stExpander"] details > summary *,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    background-color: transparent !important;
    color: #171B18 !important;
    fill: #171B18 !important;
}
header[data-testid="stHeader"] {
    background: #FAF7E9 !important;
    border-bottom: 2px solid #171B18 !important;
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
    color: #171B18 !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p {
    color: #252B27 !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #4E5752 !important;
}
code, [data-testid="stMarkdownContainer"] code, .flow-step-desc code {
    background-color: #EAE5D1 !important;
    color: #171B18 !important;
    border: 1px solid #171B18 !important;
    padding: 0.1rem 0.3rem !important;
    border-radius: 0px !important;
}
/* Inputs y Selectboxes en Modo Claro (incluso si el navegador está en Dark Mode) */
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] .react-aria-ComboBox > div[role="group"],
[data-testid="stMultiSelect"] .react-aria-ComboBox > div[role="group"] {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
    border: 1.5px solid #171B18 !important;
    border-radius: 0px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
[data-testid="stSelectbox"] input[role="combobox"],
[data-testid="stSelectbox"] button,
[data-testid="stMultiSelect"] input[role="combobox"],
[data-testid="stMultiSelect"] button {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
    -webkit-text-fill-color: #171B18 !important;
    caret-color: #171B18 !important;
}
div[data-baseweb="select"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stMultiSelect"] svg {
    fill: #171B18 !important;
    color: #171B18 !important;
}
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="base-input"] input::placeholder,
[data-testid="stSelectbox"] input::placeholder {
    color: #4E5752 !important;
    -webkit-text-fill-color: #4E5752 !important;
    opacity: 1 !important;
}
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"],
.react-aria-Popover,
.react-aria-ListBox,
.react-aria-ListBoxItem,
div[role="listbox"],
div[role="option"] {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
    border-radius: 0px !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"],
.react-aria-ListBoxItem[data-focused],
.react-aria-ListBoxItem[data-selected],
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background-color: #EAE5D1 !important;
    color: #1E5D88 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #4E5752 !important;
    background-color: transparent !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #171B18 !important;
    border-bottom: 3px solid #1B8668 !important;
}
[data-testid="stButtonGroup"] button {
    background-color: #FAF7E9 !important;
    color: #171B18 !important;
    border: 1.5px solid #171B18 !important;
    border-radius: 0px !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
    background-color: #171B18 !important;
    color: #FAF7E9 !important;
    border-color: #171B18 !important;
    font-weight: 800 !important;
}
[data-testid="stButtonGroup"] button[aria-checked="true"] *,
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] * {
    color: #FAF7E9 !important;
}
.flow-step-card,
.flow-telemetry-chip {
    background-color: #FAF7E9 !important;
    border-color: #171B18 !important;
    color: #171B18 !important;
}
"""

DARK_THEME_OVERRIDE_CSS = f'<style id="apocuna-theme-override-dark">{_DARK_RULES_BODY}</style>'
LIGHT_THEME_OVERRIDE_CSS = f'<style id="apocuna-theme-override-light">{_LIGHT_RULES_BODY}</style>'
AUTO_THEME_OVERRIDE_CSS = (
    '<style id="apocuna-theme-override-auto">'
    f'@media (prefers-color-scheme: light) {{ {_LIGHT_RULES_BODY} }}'
    f'@media (prefers-color-scheme: dark) {{ {_DARK_RULES_BODY} }}'
    '</style>'
)


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

    theme_mode = st.session_state.get("theme_mode", "☀️ Claro")
    if theme_mode == "🌙 Oscuro":
        st.markdown(DARK_THEME_OVERRIDE_CSS, unsafe_allow_html=True)
    elif theme_mode == "☀️ Claro":
        st.markdown(LIGHT_THEME_OVERRIDE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(AUTO_THEME_OVERRIDE_CSS, unsafe_allow_html=True)


def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Inicio"
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "☀️ Claro"

    qp = st.query_params
    vista_qp = sanitize_slug_param(qp.get("vista"), max_len=40)
    norma_qp = sanitize_slug_param(qp.get("norma"), max_len=140)
    ficha_qp = sanitize_slug_param(qp.get("ficha"), max_len=80)
    qp_sig = f"{vista_qp}|{norma_qp}|{ficha_qp}"
    if qp_sig != "||" and st.session_state.get("_last_qp_routed") != qp_sig:
        target_page = None
        if norma_qp or vista_qp in ("normas_comentadas", "rastrea_norma"):
            target_page = "Rastrea la Norma"
        elif vista_qp == "fen":
            target_page = "Monitoreo El Niño"
        elif vista_qp == "polity" or ficha_qp:
            target_page = "Políticas y Datos"
        elif vista_qp == "biblioteca":
            target_page = "Biblioteca y Revistas"
        elif vista_qp == "escuela":
            target_page = "Escuela y Becas"

        if target_page:
            st.session_state.current_page = target_page
            st.session_state._last_qp_routed = qp_sig
            theme_key = f"apocuna_nav_{st.session_state.get('theme_mode', '☀️ Claro')}"
            st.session_state.pop(theme_key, None)
            st.session_state.pop("_last_sidebar_menu", None)

    render_sidebar()
    load_css()

    # Barra de búsqueda general en la parte superior del sitio
    st.markdown('<div class="apocuna-top-search-anchor"></div>', unsafe_allow_html=True)
    col_search_top, col_search_btn = st.columns([6.5, 1.0])
    with col_search_top:
        global_q = st.text_input(
            "Buscador general",
            placeholder="🔎 Buscar en todo Apocuna: normas de El Peruano, noticias, microdatos, fichas técnicas, FEN, cursos...",
            key="global_search_query",
            label_visibility="collapsed",
        )
    with col_search_btn:
        if st.session_state.get("global_search_query", "").strip():
            if st.button("✕ Limpiar", key="btn_top_clear_search", use_container_width=True):
                st.session_state["global_search_query"] = ""
                st.rerun()

    if global_q and global_q.strip():
        render_busqueda_global(global_q)
        return

    current = st.session_state.get("current_page", "Inicio")
    renderer = ROUTES.get(current, render_home)
    renderer()


if __name__ == "__main__":
    main()
