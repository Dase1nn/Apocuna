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
    
    # Inyectar banner APOCUNA HUB refinado y no invasivo
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
                left: '0',
                right: '0',
                backgroundColor: 'rgba(14, 17, 23, 0.75)',
                backdropFilter: 'blur(8px)',
                WebkitBackdropFilter: 'blur(8px)',
                color: '#EF4444',
                textAlign: 'center',
                fontWeight: '800',
                fontSize: '1.2rem',
                letterSpacing: '3px',
                padding: '0.6rem 1rem',
                zIndex: '999990',
                borderBottom: '1px solid rgba(255, 255, 255, 0.07)',
                transition: 'all 0.25s ease',
                pointerEvents: 'none'
            });
            doc.body.appendChild(banner);
            
            function updateBannerLayout() {
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (sidebar && sidebar.offsetWidth > 50) {
                    banner.style.left = sidebar.offsetWidth + 'px';
                } else {
                    banner.style.left = '0';
                }
            }
            updateBannerLayout();
            window.parent.addEventListener('resize', updateBannerLayout);
            
            const observer = new MutationObserver(updateBannerLayout);
            const sidebarEl = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebarEl) {
                observer.observe(sidebarEl, { attributes: true, attributeFilter: ['aria-expanded', 'style'] });
            }
            
            const scrollArea = doc.querySelector('.stMain') || doc.documentElement;
            scrollArea.addEventListener('scroll', () => {
                updateBannerLayout();
                if (scrollArea.scrollTop > 30) {
                    banner.style.fontSize = '1.05rem';
                    banner.style.padding = '0.45rem 1rem';
                    banner.style.backgroundColor = 'rgba(14, 17, 23, 0.92)';
                    banner.style.boxShadow = '0px 4px 16px rgba(0,0,0,0.35)';
                } else {
                    banner.style.fontSize = '1.2rem';
                    banner.style.padding = '0.6rem 1rem';
                    banner.style.backgroundColor = 'rgba(14, 17, 23, 0.75)';
                    banner.style.boxShadow = 'none';
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
