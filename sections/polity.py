import streamlit as st
from utils.loaders import load_polity, load_polity_alertas
from components.cards import render_kpi_ribbon, render_polity_cards, render_polity_alertas_carousel


def _filter_tarjetas(tarjetas: list, freq_filter: str, query: str) -> list:
    q = query.lower().strip()
    res = tarjetas
    if freq_filter != "Todas":
        res = [t for t in res if freq_filter.lower() in t.get("frecuencia", "").lower()]
    if q:
        res = [
            t for t in res
            if q in t.get("titulo", "").lower()
            or q in t.get("descripcion", "").lower()
            or q in t.get("fuente", "").lower()
        ]
    return res


def render_polity():
    st.title("🏛️ Polity and Policy: Insumos Estratégicos")
    st.markdown(
        '<p class="hero-subtitle">Metodologías, repositorios y mecanismos de vigilancia institucional para la formulación, '
        'ejecución y evaluación de políticas públicas en el Perú.</p>',
        unsafe_allow_html=True
    )

    subsecciones = load_polity()
    alertas = load_polity_alertas()
    total_tarjetas = sum(len(s.get("tarjetas", [])) for s in subsecciones)

    render_kpi_ribbon([
        {"icon": "🏛️", "value": str(len(subsecciones)), "label": "Ejes Estratégicos", "sub": "Normativa, Datos, Coyuntura y Evidencia"},
        {"icon": "🗂️", "value": str(total_tarjetas), "label": "Insumos Técnicos", "sub": "Fuentes primarias verificadas"},
        {"icon": "📢", "value": str(len(alertas)), "label": "Alertas Institucionales", "sub": "Contraloría, Defensoría, IEP, GRADE, CEPAL"},
    ])

    if alertas:
        st.subheader("📢 Últimas Alertas Institucionales (Automatizado)")
        render_polity_alertas_carousel(alertas)
        st.markdown("---")

    if not subsecciones:
        st.info("No se encontró información en data/polity.json.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        busqueda = st.text_input(
            "🔎 Buscar insumo por institución o palabra clave:",
            placeholder="Ej: ENAHO, El Peruano, Conflictos, INCORE, BID...",
            key="polity_search"
        )
    with col2:
        freq_sel = st.selectbox(
            "Frecuencia de actualización:",
            ["Todas", "Diaria", "Semanal", "Mensual", "Permanente"],
            key="polity_freq"
        )

    for idx, sub in enumerate(subsecciones):
        titulo_sub = sub.get("subseccion", f"Subsección {idx + 1}")
        tarjetas_filtradas = _filter_tarjetas(sub.get("tarjetas", []), freq_sel, busqueda)
        is_expanded = (idx == 0) or bool(busqueda) or (freq_sel != "Todas")
        with st.expander(f"📌 {titulo_sub} ({len(tarjetas_filtradas)})", expanded=is_expanded):
            render_polity_cards(tarjetas_filtradas)
