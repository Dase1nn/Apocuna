import streamlit as st
from utils.loaders import load_eventos, load_eventos_alertas
from components.cards import render_kpi_ribbon, render_eventos_grid, render_eventos_alertas_carousel


def _matches_evento(e: dict, tipo_expected: str | None, b_lower: str) -> bool:
    if tipo_expected and e.get("tipo") != tipo_expected:
        return False
    if not b_lower:
        return True
    blob = f"{e.get('titulo', '')} {e.get('tematica', '')} {e.get('descripcion', '')}".lower()
    return b_lower in blob


def _filter_eventos(eventos: list, tipo_filtro: str, busqueda: str) -> list:
    tipo_map = {"Revistas": "revista", "Congresos": "congreso"}
    tipo_expected = tipo_map.get(tipo_filtro)
    b_lower = busqueda.lower().strip()
    return [e for e in eventos if _matches_evento(e, tipo_expected, b_lower)]


def render_eventos():
    st.title("📅 Calendario de Eventos y Publicaciones Indexadas")
    st.markdown(
        '<p class="hero-subtitle">Revistas académicas arbitradas y congresos especializados para la difusión y deliberación en políticas públicas y gobernanza.</p>',
        unsafe_allow_html=True
    )

    eventos = load_eventos()
    alertas = load_eventos_alertas()
    revistas_count = sum(1 for e in eventos if e.get("tipo") == "revista")
    congresos_count = sum(1 for e in eventos if e.get("tipo") == "congreso")

    render_kpi_ribbon([
        {"icon": "📚", "value": str(revistas_count), "label": "Revistas Indexadas", "sub": "Recepción continua de manuscritos"},
        {"icon": "🏛️", "value": str(congresos_count), "label": "Congresos y Coloquios", "sub": "Nacionales e internacionales"},
        {"icon": "📢", "value": str(len(alertas)), "label": "Novedades en Radar", "sub": "Seguimiento automatizado"},
    ])

    if alertas:
        st.subheader("📢 Últimas Novedades y Convocatorias (Automatizado)")
        render_eventos_alertas_carousel(alertas)
        st.markdown("---")

    if not eventos:
        st.info("No se encontraron registros en data/eventos.json.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        tipo_filtro = st.selectbox("Filtrar por categoría:", ["Todos", "Revistas", "Congresos"])
    with col2:
        busqueda = st.text_input(
            "🔎 Buscar por temática, revista o congreso:",
            placeholder="Ej: Gobernanza, Escolar, CLAD, FLACSO, ALACIP, Educación..."
        )

    eventos_filtrados = _filter_eventos(eventos, tipo_filtro, busqueda)
    st.caption(f"Mostrando **{len(eventos_filtrados)}** de **{len(eventos)}** convocatorias académicas registradas.")
    render_eventos_grid(eventos_filtrados)
