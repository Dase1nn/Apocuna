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
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#29B5E8", "font-size": "1.02rem"},
                "nav-link": {
                    "font-size": "0.91rem",
                    "text-align": "left",
                    "margin": "3px 0px",
                    "padding": "0.55rem 0.85rem",
                    "border-radius": "8px",
                    "--hover-color": "rgba(41, 181, 232, 0.12)",
                },
                "nav-link-selected": {
                    "background-color": "rgba(41, 181, 232, 0.18)",
                    "color": "#29B5E8",
                    "font-weight": "600",
                    "border-left": "3px solid #29B5E8"
                },
            }
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
