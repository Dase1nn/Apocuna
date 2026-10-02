import streamlit as st

def render_card_row(title: str, cards_data: list):
    """
    Renderiza una fila de tarjetas con scroll horizontal (estilo Snowsight).
    """
    st.subheader(title)
    
    # Construcción HTML para las tarjetas con overflow-x
    cards_html = ""
    for card in cards_data:
        cards_html += f"""<div class="card">
<h3>{card.get('title', '')}</h3>
<p>{card.get('description', '')}</p>
</div>"""

    
    container_html = f"""<div class="card-container">
{cards_html}
</div>"""

    
    st.markdown(container_html, unsafe_allow_html=True)
