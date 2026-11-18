import streamlit as st
from streamlit_option_menu import option_menu
from utils.loaders import load_dashboard_kpis
from components.apocunoso_branding import build_sidebar_brand_html

OPTIONS_LIST = [
    "Inicio",
    "Rastrea la Norma",
    "Políticas y Datos",
    "Monitoreo El Niño",
    "Biblioteca y Revistas",
    "Escuela y Becas",
    "Sobre Apocuna",
]

LEGACY_PAGE_ALIASES = {
    "Polity and Policy": "Políticas y Datos",
    "🌊 Fenómeno El Niño (FEN)": "Monitoreo El Niño",
    "Fenómeno El Niño (FEN)": "Monitoreo El Niño",
    "Notas": "Biblioteca y Revistas",
    "Eventos": "Biblioteca y Revistas",
    "Estudiantes": "Escuela y Becas",
    "Estudiantes (DEMO)": "Escuela y Becas",
    "Sobre el sitio": "Sobre Apocuna",
}

THEME_OPTIONS = ["💻 Auto", "🌙 Oscuro", "☀️ Claro"]


def _resolve_option_menu_styles(theme_mode: str) -> dict:
    """Calibra el contenedor y los enlaces de option_menu bajo el sistema `apocunoso-style` (0px radio, bordes nítidos)."""
    container = {
        "padding": "0!important",
        "background-color": "#F2EFE0",
        "border-radius": "0px",
    }
    nav_link = {
        "font-size": "0.88rem",
        "font-weight": "600",
        "text-align": "left",
        "margin": "3px 0px",
        "padding": "0.62rem 0.85rem",
        "border-radius": "0px",
        "color": "#171B18",
        "background-color": "transparent",
        "--hover-color": "#E6E1CE",
    }
    nav_selected = {
        "background-color": "#FAF7E9",
        "color": "#171B18",
        "font-weight": "800",
        "border-left": "5px solid #1B8668",
        "border-top": "1.5px solid #171B18",
        "border-right": "1.5px solid #171B18",
        "border-bottom": "1.5px solid #171B18",
    }
    icon_style = {"color": "#2775AA", "font-size": "1.02rem"}

    if theme_mode == "🌙 Oscuro":
        container["background-color"] = "#181D1A"
        container["--secondary-background-color"] = "#181D1A"
        container["--text-color"] = "#FAF7E9"
        nav_link["color"] = "#DCE0DB"
        nav_link["background-color"] = "transparent"
        nav_link["--hover-color"] = "#262F2A"
        nav_selected["background-color"] = "#202723"
        nav_selected["color"] = "#FAF7E9"
        nav_selected["border-left"] = "5px solid #F0BB38"
        nav_selected["border-top"] = "1.5px solid #4A5750"
        nav_selected["border-right"] = "1.5px solid #4A5750"
        nav_selected["border-bottom"] = "1.5px solid #4A5750"
        icon_style["color"] = "#F0BB38"
    elif theme_mode == "💻 Auto":
        container["color-scheme"] = "light dark"
        container["background-color"] = "light-dark(#F2EFE0, #181D1A)"
        container["--secondary-background-color"] = "light-dark(#F2EFE0, #181D1A)"
        container["--text-color"] = "light-dark(#171B18, #FAF7E9)"
        nav_link["color-scheme"] = "light dark"
        nav_link["color"] = "light-dark(#171B18, #DCE0DB)"
        nav_link["background-color"] = "transparent"
        nav_link["--hover-color"] = "light-dark(#E6E1CE, #262F2A)"
        nav_selected["color-scheme"] = "light dark"
        nav_selected["background-color"] = "light-dark(#FAF7E9, #202723)"
        nav_selected["color"] = "light-dark(#171B18, #FAF7E9)"
        nav_selected["border-left"] = "5px solid light-dark(#1B8668, #F0BB38)"
        nav_selected["border-top"] = "1.5px solid light-dark(#171B18, #4A5750)"
        nav_selected["border-right"] = "1.5px solid light-dark(#171B18, #4A5750)"
        nav_selected["border-bottom"] = "1.5px solid light-dark(#171B18, #4A5750)"
        icon_style["color-scheme"] = "light dark"
        icon_style["color"] = "light-dark(#2775AA, #F0BB38)"

    return {
        "container": container,
        "icon": icon_style,
        "nav-link": nav_link,
        "nav-link-selected": nav_selected,
    }


def render_sidebar():
    with st.sidebar:
        st.markdown(
            build_sidebar_brand_html(),
            unsafe_allow_html=True
        )

        current_theme = st.session_state.get("theme_mode", "💻 Auto")
        if current_theme not in THEME_OPTIONS:
            current_theme = "💻 Auto"

        st.markdown('<div class="sidebar-theme-label">🎨 MODO DE APARIENCIA (APOCUNOSO)</div>', unsafe_allow_html=True)
        selected_theme = st.segmented_control(
            "Modo de apariencia",
            options=THEME_OPTIONS,
            default=current_theme,
            selection_mode="single",
            label_visibility="collapsed",
            key="sidebar_theme_segmented",
            width="stretch",
        )
        if not selected_theme:
            selected_theme = current_theme
        st.session_state.theme_mode = selected_theme

        st.markdown("---")

        current = st.session_state.get("current_page", "Inicio")
        current = LEGACY_PAGE_ALIASES.get(current, current)
        st.session_state.current_page = current
        default_idx = OPTIONS_LIST.index(current) if current in OPTIONS_LIST else 0

        menu = option_menu(
            menu_title=None,
            options=OPTIONS_LIST,
            icons=[
                "house",
                "binoculars",
                "bank",
                "tsunami",
                "journal-bookmark",
                "mortarboard",
                "info-circle",
            ],
            menu_icon="compass",
            default_index=default_idx,
            key=f"apocuna_nav_{selected_theme}",
            styles=_resolve_option_menu_styles(selected_theme),
        )
        prev_menu = st.session_state.get("_last_sidebar_menu")
        if prev_menu is None:
            st.session_state._last_sidebar_menu = menu
            st.session_state.current_page = menu
        elif menu != prev_menu:
            st.session_state._last_sidebar_menu = menu
            st.session_state.current_page = menu
            for qp_k in ("vista", "norma", "ficha"):
                if qp_k in st.query_params:
                    del st.query_params[qp_k]

        kpis = load_dashboard_kpis()
        st.markdown(
            f"""
            <div class="sidebar-telemetry-card">
                <div class="sidebar-telemetry-header">
                    <span class="status-dot-live"></span>
                    <span>RADAR AUTOMATIZADO</span>
                </div>
                <div class="sidebar-telemetry-grid">
                    <div><strong>{kpis['fuentes_total']}</strong><span>Fuentes</span></div>
                    <div><strong>{kpis['noticias_total']}</strong><span>Noticias</span></div>
                    <div><strong>{kpis['oportunidades_total']}</strong><span>Recursos</span></div>
                </div>
                <div class="sidebar-telemetry-sync">Últ. sync: {kpis['last_sync']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
