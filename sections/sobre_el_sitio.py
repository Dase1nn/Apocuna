import streamlit as st
import os
import markdown

def render_sobre_el_sitio():
    # El archivo markdown en data/
    md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sobre_el_sitio.md")
    
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        html_body = markdown.markdown(raw_content)
        st.markdown(f'<div class="snow-card">{html_body}</div>', unsafe_allow_html=True)
    else:
        st.warning("No se encontró el contenido de la sección 'Sobre el sitio'.")
