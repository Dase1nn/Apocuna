import streamlit as st
from utils.loaders import load_notas
from components.cards import render_nota_horizontal


def _render_nota_detail(nota: dict):
    if st.button("← Volver al índice de notas y ensayos", key="btn_back_to_list"):
        st.session_state["selected_note_id"] = None
        st.rerun()

    meta = nota.get("meta", {})
    st.markdown(
        f"""
        <div class="snow-card article-reader-header">
            <div class="note-meta">{meta.get('tipo', 'ENSAYO')} • ⏱️ {meta.get('lectura_min', 3)} min de lectura ({meta.get('palabras', 0)} palabras)</div>
            <h1 class="hero-intro-title">{meta.get('titulo', 'Sin título')}</h1>
            <div class="note-author-date">✍️ Autor: <strong>{meta.get('autor', 'Apocuna Hub')}</strong> &nbsp;|&nbsp; 📅 Publicación: <strong>{meta.get('fecha', 'Reciente')}</strong></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="article-reader-body">', unsafe_allow_html=True)
    st.markdown(nota.get("body", ""))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    if st.button("← Volver al índice de notas y ensayos", key="btn_back_to_list_bottom"):
        st.session_state["selected_note_id"] = None
        st.rerun()


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
