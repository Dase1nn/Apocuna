import streamlit as st
from streamlit_option_menu import option_menu
from utils.loaders import load_dashboard_kpis

OPTIONS_LIST = [
    "Inicio",
    "Polity and Policy",
    "Fenómeno El Niño (FEN)",
    "Estudiantes (DEMO)",
    "Notas",
    "Eventos",
    "Sobre el sitio"
]

THEME_OPTIONS = ["💻 Auto", "🌙 Oscuro", "☀️ Claro"]


def _resolve_option_menu_styles(theme_mode: str) -> dict:
    """Calibra el contenedor y los enlaces de option_menu para Auto, Oscuro y Claro."""
    container = {
        "padding": "0!important",
        "background-color": "transparent",
        "border-radius": "0px",
    }
    nav_link = {
        "font-size": "0.91rem",
        "text-align": "left",
        "margin": "3px 0px",
        "padding": "0.55rem 0.85rem",
        "border-radius": "8px",
        "--hover-color": "rgba(41, 181, 232, 0.14)",
    }
    nav_selected = {
        "background-color": "rgba(41, 181, 232, 0.18)",
        "color": "#29B5E8",
        "font-weight": "600",
        "border-left": "3px solid #29B5E8",
    }

    if theme_mode == "🌙 Oscuro":
        container["background-color"] = "#151B26"
        container["--secondary-background-color"] = "#151B26"
        container["--text-color"] = "#E2E8F0"
        nav_link["color"] = "#E2E8F0"
        nav_link["background-color"] = "transparent"
        nav_selected["background-color"] = "rgba(41, 181, 232, 0.22)"
        nav_selected["color"] = "#38BDF8"
    elif theme_mode == "☀️ Claro":
        container["background-color"] = "#FFFFFF"
        container["--secondary-background-color"] = "#FFFFFF"
        container["--text-color"] = "#1E293B"
        nav_link["color"] = "#1E293B"
        nav_link["background-color"] = "transparent"
        nav_selected["color"] = "#0284C7"
        nav_selected["background-color"] = "rgba(2, 132, 199, 0.14)"

    return {
        "container": container,
        "icon": {"color": "#29B5E8", "font-size": "1.02rem"},
        "nav-link": nav_link,
        "nav-link-selected": nav_selected,
    }


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand-box">'
            '<div class="sidebar-brand-badge">PERÚ • PUBLIC POLICY HUB</div>'
            '<h1 class="sidebar-brand-title">APOCUNA HUB</h1>'
            '<div class="sidebar-brand-subtitle">Evidencia, Datos & Gobernanza</div>'
            '</div>',
            unsafe_allow_html=True
        )

        current_theme = st.session_state.get("theme_mode", "💻 Auto")
        if current_theme not in THEME_OPTIONS:
            current_theme = "💻 Auto"

        st.markdown('<div class="sidebar-theme-label">🎨 MODO DE APARIENCIA</div>', unsafe_allow_html=True)
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
        if current == "Estudiantes":
            current = "Estudiantes (DEMO)"
        elif current == "🌊 Fenómeno El Niño (FEN)":
            current = "Fenómeno El Niño (FEN)"
        default_idx = OPTIONS_LIST.index(current) if current in OPTIONS_LIST else 0

        menu = option_menu(
            menu_title=None,
            options=OPTIONS_LIST,
            icons=[
                "house",
                "bank",
                "tsunami",
                "mortarboard",
                "journal-text",
                "calendar-event",
                "info-circle"
            ],
            menu_icon="compass",
            default_index=default_idx,
            key=f"apocuna_nav_{selected_theme}",
            styles=_resolve_option_menu_styles(selected_theme),
        )
        st.session_state.current_page = menu

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
