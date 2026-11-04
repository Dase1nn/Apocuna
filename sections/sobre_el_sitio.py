import streamlit as st
from utils.loaders import load_sobre_el_sitio_html


def render_sobre_el_sitio():
    html_body = load_sobre_el_sitio_html()
    if html_body:
        st.markdown(f'<div class="snow-card about-reader-card">{html_body}</div>', unsafe_allow_html=True)
    else:
        st.warning("No se encontró el contenido de la sección 'Sobre el sitio'.")
