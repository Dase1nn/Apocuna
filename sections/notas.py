import streamlit as st
from utils.loaders import load_notas
from components.cards import render_nota_horizontal

def render_notas():
    st.title("📝 Notas, Ensayos e Investigación")
    
    notas = load_notas()
    if not notas:
        st.info("No se encontraron notas en data/notas/.")
        return
        
    selected_id = st.session_state.get("selected_note_id")
    
    # Vista detallada de la nota
    if selected_id:
        nota_seleccionada = next((n for n in notas if n.get("id") == selected_id), None)
        
        if nota_seleccionada:
            if st.button("← Volver a la lista de notas", key="btn_back_to_list"):
                st.session_state["selected_note_id"] = None
                st.rerun()
                
            meta = nota_seleccionada.get("meta", {})
            st.header(meta.get("titulo", "Sin título"))
            st.caption(
                f"✍️ Autor: **{meta.get('autor', 'Apocuna Hub')}** | "
                f"📅 Fecha: **{meta.get('fecha', 'Reciente')}** | "
                f"🏷️ Tipo: **{meta.get('tipo', 'ENSAYO')}**"
            )
            st.markdown("---")
            # Renderizar el cuerpo en Markdown
            st.markdown(nota_seleccionada.get("body", ""))
            
            st.markdown("---")
            if st.button("← Volver a la lista de notas", key="btn_back_to_list_bottom"):
                st.session_state["selected_note_id"] = None
                st.rerun()
            return
        else:
            st.session_state["selected_note_id"] = None
            
    # Vista de lista de notas
    st.markdown("Análisis empírico, reflexiones de gobernanza y documentos de trabajo.")
    
    for idx, nota in enumerate(notas):
        render_nota_horizontal(nota)
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📖 Leer nota completa", key=f"btn_read_{nota.get('id')}_{idx}"):
                st.session_state["selected_note_id"] = nota.get("id")
                st.rerun()
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
