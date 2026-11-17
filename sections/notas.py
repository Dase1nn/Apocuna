import streamlit as st
from utils.loaders import load_notas
from components.cards import render_nota_horizontal, render_nota_reader


def _render_nota_detail(nota: dict):
    render_nota_reader(nota, "← Volver al índice de notas y ensayos", key_prefix="notas")


def render_notas():
    st.title("📝 Notas, Ensayos e Investigación Aplicada")

    notas = load_notas()
    if not notas:
        st.info("No se encontraron notas en data/notas/.")
        return

    selected_id = st.session_state.get("selected_note_id")
    if selected_id:
        nota_sel = next((n for n in notas if n.get("id") == selected_id), None)
        if nota_sel:
            _render_nota_detail(nota_sel)
            return
        st.session_state["selected_note_id"] = None

    st.markdown(
        '<p class="hero-subtitle">Análisis empírico, reflexiones sobre gobernanza subnacional y documentos de trabajo.</p>',
        unsafe_allow_html=True
    )

    for idx, nota in enumerate(notas):
        render_nota_horizontal(nota)
        if st.button("📖 Leer artículo completo →", key=f"btn_read_{nota.get('id')}_{idx}"):
            st.session_state["selected_note_id"] = nota.get("id")
            st.rerun()
        st.markdown("<div class='note-item-spacer'></div>", unsafe_allow_html=True)
