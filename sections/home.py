import streamlit as st
import json
import os
from components.cards import render_card_row

def render_home():
    st.title("Panel Principal")
    
    # Cargar contenido de JSON
    content_path = os.path.join(os.path.dirname(__file__), "..", "data", "content.json")
    try:
        with open(content_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error cargando contenido estático: {e}")
        data = {"home": {"featured_cards": []}}
        
    home_data = data.get("home", {})
    st.markdown(home_data.get("description", ""))
    
    # Renderizar tarjetas con scroll horizontal
    cards = home_data.get("featured_cards", [])
    if cards:
        render_card_row("Destacados y Categorías", cards)
