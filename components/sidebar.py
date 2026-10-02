import streamlit as st
from streamlit_option_menu import option_menu


def render_sidebar():
    with st.sidebar:
        st.title("Navegación")
        
        # Toggle claro/oscuro
        modo_oscuro = st.toggle("🌙 Modo Oscuro / Claro", value=st.session_state.tema_oscuro)
        st.session_state.tema_oscuro = modo_oscuro
        
        st.markdown("---")
        
        # Menú interactivo con iconos
        menu = option_menu(
            menu_title="APOCUNA HUB",
            options=[
                "Inicio",
                "Polity and Policy",
                "Estudiantes (Próximamente)",
                "Notas",
                "Eventos"
            ],
            icons=["house", "bank", "mortarboard", "journal-text", "calendar-event"],
            menu_icon="compass",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "var(--primary-color)", "font-size": "1.1rem"},
                "nav-link": {
                    "font-size": "0.95rem",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "rgba(41, 181, 232, 0.1)",
                },
                "nav-link-selected": {"background-color": "rgba(41, 181, 232, 0.2)", "color": "var(--dark-color)", "font-weight": "600"},
            }
        )
        st.session_state.current_page = menu
