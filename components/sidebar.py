import streamlit as st
from streamlit_option_menu import option_menu


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="padding: 0.2rem 0 0.8rem 0;">'
            '<h1 style="color: #EF4444; font-size: 1.45rem; font-weight: 800; '
            'letter-spacing: 2px; text-transform: uppercase; margin: 0 0 0.25rem 0;">'
            'APOCUNA HUB'
            '</h1>'
            '<div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase;">'
            'Evidencia & Política Pública'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        options_list = [
            "Inicio",
            "Polity and Policy",
            "Estudiantes (DEMO)",
            "Notas",
            "Eventos",
            "Sobre el sitio"
        ]
        
        default_idx = 0
        if "current_page" in st.session_state and st.session_state.current_page in options_list:
            default_idx = options_list.index(st.session_state.current_page)
            
        # Menú interactivo con iconos
        menu = option_menu(
            menu_title=None,
            options=options_list,
            icons=["house", "bank", "mortarboard", "journal-text", "calendar-event", "info-circle"],
            menu_icon="compass",
            default_index=default_idx,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#29B5E8", "font-size": "1.05rem"},
                "nav-link": {
                    "font-size": "0.92rem",
                    "text-align": "left",
                    "margin": "2px 0px",
                    "--hover-color": "rgba(41, 181, 232, 0.1)",
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
