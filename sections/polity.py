import streamlit as st
from utils.loaders import (
    load_polity,
    load_polity_alertas,
    load_fuentes,
    fetch_ckan_datasets
)
from components.cards import (
    render_kpi_ribbon,
    render_polity_cards,
    render_polity_alertas_carousel,
    render_ckan_carousel,
    render_fuentes_grid
)

BLOQUES_FUENTES = [
    ("Datos abiertos y microdatos", "📊 1. Datos abiertos y microdatos", True),
    ("Control gubernamental y conflictividad social", "⚖️ 2. Control gubernamental y conflictividad social", False),
    ("Think tanks y repositorios", "🧠 3. Think tanks y repositorios académicos", False),
    ("Organismos multilaterales", "🌍 4. Organismos multilaterales y cooperación", False),
    ("Documentos e informes específicos", "📑 5. Documentos e informes específicos", False),
]


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


def _matches_fuente(f: dict, bloque_sel: str, q_lower: str) -> bool:
    if bloque_sel != "Todos los bloques" and f.get("bloque", "").lower() != bloque_sel.lower():
        return False
    if not q_lower:
        return True
    blob = f"{f.get('nombre', '')} {f.get('institucion', '')} {f.get('descripcion_corta', '')}".lower()
    return q_lower in blob


def _render_catalogo_fuentes(fuentes: list):
    st.header("📊 Catálogo Auditado de Fuentes de Información")
    st.markdown("Bases de datos oficiales, plataformas de microdatos y repositorios organizados por bloques temáticos.")

    col_search, col_bloque = st.columns([2, 1])
    with col_search:
        query = st.text_input(
            "🔎 Filtrar fuentes por institución, nombre o temática:",
            placeholder="Ej: INEI, ENAHO, GRADE, CEPAL, Contraloría, MINSA...",
            key="polity_fuentes_search"
        )
    with col_bloque:
        opciones_bloque = ["Todos los bloques"] + [b[0] for b in BLOQUES_FUENTES]
        bloque_sel = st.selectbox("Bloque temático:", opciones_bloque, key="polity_fuentes_bloque")

    q_lower = query.lower().strip()
    if q_lower or bloque_sel != "Todos los bloques":
        filtradas = [f for f in fuentes if _matches_fuente(f, bloque_sel, q_lower)]
        st.caption(f"Mostrando **{len(filtradas)}** de **{len(fuentes)}** fuentes registradas.")
        render_fuentes_grid(filtradas)
        return

    for key_bloque, titulo_bloque, exp_default in BLOQUES_FUENTES:
        fuentes_bloque = [f for f in fuentes if f.get("bloque", "").lower() == key_bloque.lower()]
        with st.expander(f"{titulo_bloque} ({len(fuentes_bloque)})", expanded=exp_default):
            render_fuentes_grid(fuentes_bloque)


def render_polity():
    st.title("🏛️ Polity and Policy: Insumos, Fuentes y Datos Abiertos")
    st.markdown(
        '<p class="hero-subtitle">Metodologías, repositorios auditados y mecanismos de vigilancia institucional para la formulación, '
        'ejecución y evaluación de políticas públicas en el Perú.</p>',
        unsafe_allow_html=True
    )

    subsecciones = load_polity()
    alertas = load_polity_alertas()
    fuentes = load_fuentes()
    total_tarjetas = sum(len(s.get("tarjetas", [])) for s in subsecciones)

    render_kpi_ribbon([
        {"icon": "🏛️", "value": str(len(subsecciones)), "label": "Ejes Estratégicos", "sub": "Normativa, Datos, Coyuntura y Evidencia"},
        {"icon": "🗂️", "value": str(total_tarjetas), "label": "Insumos Técnicos", "sub": "Incluye Boletines de Normas Legales"},
        {"icon": "🗄️", "value": str(len(fuentes)), "label": "Fuentes Auditadas", "sub": "5 bloques temáticos verificados"},
        {"icon": "📢", "value": str(len(alertas)), "label": "Alertas Institucionales", "sub": "Contraloría, Defensoría, IEP, GRADE, CEPAL"},
    ])

    if alertas:
        st.subheader("📢 Últimas Alertas Institucionales (Automatizado)")
        render_polity_alertas_carousel(alertas)
        st.markdown("---")

    if subsecciones:
        st.header("🧭 Ejes Estratégicos de Polity & Policy")
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

    st.markdown("---")

    # PORTALES NACIONALES DE DATOS ABIERTOS Y SALUD (Trasladado desde Inicio)
    st.header("🔄 Portales Nacionales de Datos Abiertos y Salud")
    st.markdown("Acceso directo a los catálogos nacionales de datos abiertos (PCM, GOB.PE, MINSA REUNIS y CDC Perú).")
    portales_ckan = [f for f in fuentes if f.get("id") in ("f_001", "f_002", "f_003", "f_004")]
    ckan_datasets = fetch_ckan_datasets()
    render_ckan_carousel(ckan_datasets, portales_directos=portales_ckan)

    st.markdown("---")

    # CATÁLOGO AUDITADO DE FUENTES DE INFORMACIÓN (Trasladado desde Inicio)
    _render_catalogo_fuentes(fuentes)
