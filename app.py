import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Apocuna Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado del tema si no existe
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = False

from components.sidebar import render_sidebar
from sections.home import render_home
from sections.polity import render_polity
from sections.estudiantes import render_estudiantes
from sections.notas import render_notas
from sections.eventos import render_eventos

def load_css():
    """Carga los estilos personalizados de Snowsight dinámicamente."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    
    if st.session_state.tema_oscuro:
        theme_vars = """
        :root {
            --primary-color: #29B5E8;
            --dark-color: #29B5E8;
            --bg-light: #0E1117;
            --text-color: #FAFAFA;
            --card-bg: #1E1E1E;
        }
        """
    else:
        theme_vars = """
        :root {
            --primary-color: #29B5E8;
            --dark-color: #11567F;
            --bg-light: #F8F9FA;
            --text-color: #333333;
            --card-bg: #FFFFFF;
        }
        """

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{theme_vars}\n{f.read()}</style>", unsafe_allow_html=True)

def main():
    # Renderizamos sidebar primero para que el toggle actualice el state
    render_sidebar()
    # Cargamos CSS inyectando las variables del tema
    load_css()
    
    # Inyectar banner APOCUNA HUB con comportamiento de encogimiento al scroll
    components.html(
        """
        <script>
        const doc = window.parent.document;
        let banner = doc.getElementById('apocuna-hub-banner');
        if (!banner) {
            banner = doc.createElement('div');
            banner.id = 'apocuna-hub-banner';
            banner.innerText = 'APOCUNA HUB';
            Object.assign(banner.style, {
                position: 'fixed',
                top: '0',
                left: doc.querySelector('[data-testid="stSidebar"]') ? doc.querySelector('[data-testid="stSidebar"]').offsetWidth + 'px' : '0',
                right: '0',
                backgroundColor: 'transparent',
                color: 'red',
                textAlign: 'center',
                fontWeight: '900',
                fontSize: '2.5rem',
                padding: '1rem',
                zIndex: '999999',
                transition: 'all 0.3s ease',
                pointerEvents: 'none'
            });
            doc.body.appendChild(banner);
            
            // Ajustar tamaño al hacer scroll en el contenedor principal
            const scrollArea = doc.querySelector('.stMain') || doc.documentElement;
            scrollArea.addEventListener('scroll', () => {
                if (scrollArea.scrollTop > 50) {
                    banner.style.fontSize = '1.2rem';
                    banner.style.padding = '0.5rem';
                    banner.style.backgroundColor = 'var(--background-color)';
                    banner.style.boxShadow = '0px 2px 10px rgba(0,0,0,0.1)';
                    banner.style.pointerEvents = 'auto';
                } else {
                    banner.style.fontSize = '2.5rem';
                    banner.style.padding = '1rem';
                    banner.style.backgroundColor = 'transparent';
                    banner.style.boxShadow = 'none';
                    banner.style.pointerEvents = 'none';
                }
            });
        }
        </script>
        """,
        height=0
    )
    
    current = st.session_state.get("current_page", "Inicio")
    
    # Enrutador
    if current == "Inicio":
        render_home()
    elif current == "Polity and Policy":
        render_polity()
    elif current == "Estudiantes (Próximamente)":
        render_estudiantes()
    elif current == "Notas":
        render_notas()
    elif current == "Eventos":
        render_eventos()

if __name__ == "__main__":
    main()
