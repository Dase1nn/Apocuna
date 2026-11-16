import base64
import os

import streamlit as st
from utils.loaders import (
    load_polity,
    load_polity_alertas,
    load_fuentes,
    load_evaluaciones_politicas,
    load_revistas_gestion,
    fetch_ckan_datasets,
)
from components.cards import (
    escape,
    safe_url,
    _action_button,
    render_kpi_ribbon,
    render_polity_cards,
    render_polity_alertas_carousel,
    render_ckan_carousel,
    render_fuentes_grid,
)
from sections.fichas_tecnicas import render_ficha_tecnica_detalle

CEPLAN_PAGE_URL = (
    "https://www.gob.pe/institucion/ceplan/informes-publicaciones/"
    "7665898-base-de-datos-politicas-nacionales-de-los-sectores"
)
CEPLAN_XLSX_URL = (
    "https://cdn.www.gob.pe/uploads/document/file/9351001/"
    "7665898-base-de-datos-politicas-nacionales-de-los-sectores-al-15-10-2026.xlsx?v=1792092865"
)
_CEPLAN_PREVIEW_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "ceplan_previews",
    "bd_politicas_nacionales.png",
)


@st.cache_data(show_spinner=False)
def _load_ceplan_preview_data_uri(mtime: float) -> str:
    """Carga y codifica en base64 la captura de la base de datos CEPLAN."""
    _ = mtime
    with open(_CEPLAN_PREVIEW_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"

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


def _render_eval_cards_grid(items: list) -> None:
    """Renderiza una grilla de evaluaciones siguiendo las etiquetas apocunoso-style."""
    if not items:
        st.info("No se encontraron evaluaciones con estos criterios.")
        return

    cards_html = []
    for item in items:
        is_social = item.get("nivel_prioridad") == "programa_social"
        badge_left = "PROGRAMA SOCIAL" if is_social else "POLÍTICA PÚBLICA"
        tipo_eval = escape(item.get("tipo_evaluacion", "Evaluación"))
        anio = escape(item.get("anio", ""))
        badge_right = f"{tipo_eval.upper()} • {anio}" if anio else tipo_eval.upper()
        badge_right_cls = "badge-freq-permanente" if is_social else "badge-freq-anual"

        programa = escape(item.get("programa_o_ambito", ""))
        politica = escape(item.get("politica_publica", ""))
        titulo = escape(item.get("titulo", ""))
        hallazgo = escape(item.get("hallazgo_clave", ""))
        entidad = escape(item.get("entidad_evaluadora", ""))
        btn_html = _action_button(item.get("url"), "Ver evaluación ↗")

        cards_html.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta">'
            f'<span class="badge-tipo">{badge_left}</span>'
            f'<span class="{badge_right_cls}">{badge_right}</span>'
            f'</div>'
            f'<div class="inst">{programa}</div>'
            f'<h4>{titulo}</h4>'
            f'<div class="card-verified-meta" style="margin-bottom:0.45rem;">📌 Política vinculada: {politica}</div>'
            f'<p>{hallazgo}</p>'
            f'<div class="card-verified-meta">🏛️ {entidad}</div>'
            f'</div>'
            f'<div class="card-footer-action">{btn_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def _render_ceplan_y_evaluaciones() -> None:
    """Renderiza la Base de Datos CEPLAN (3/4 imagen + 1/4 leyenda) y evaluaciones peruanas."""
    st.header("📋 Políticas Nacionales CEPLAN y Evaluaciones de Programas Públicos")
    st.markdown(
        "Acceso directo al registro maestro de Políticas Nacionales del CEPLAN y compendio auditado "
        "de evaluaciones de impacto, diseño presupuestal (EDEP), implementación y seguimiento en el Perú."
    )

    preview_html = ""
    if os.path.exists(_CEPLAN_PREVIEW_PATH):
        mtime = os.path.getmtime(_CEPLAN_PREVIEW_PATH)
        uri = _load_ceplan_preview_data_uri(mtime)
        img_url = safe_url(uri)
        if img_url:
            preview_html = f'<img src="{img_url}" alt="Vista previa de la Base de Datos de Políticas Nacionales del CEPLAN en Excel" />'

    btn_ceplan = _action_button(CEPLAN_PAGE_URL, "Publicación CEPLAN ↗")
    btn_xlsx = _action_button(CEPLAN_XLSX_URL, "Descargar Excel ↗")

    spotlight_html = (
        '<div class="ceplan-spotlight-card">'
        '<div class="ceplan-spotlight-media">'
        f'{preview_html}'
        '<div class="ceplan-media-caption">'
        '<span>📊 Archivo oficial: <code>base-de-datos-politicas-nacionales-al-15-10-2026.xlsx</code></span>'
        '<span>Hojas: <strong>1. PN APROBADAS (51)</strong> · <strong>2. PN EN PROCESO (38)</strong></span>'
        '</div>'
        '</div>'
        '<div class="ceplan-spotlight-legend">'
        '<div>'
        '<div class="ceplan-legend-head">'
        '<span class="badge-tipo">BASE DE DATOS</span>'
        '<span class="badge-continua">SINAPLAN</span>'
        '</div>'
        '<h3 class="ceplan-legend-title">Políticas Nacionales de los Sectores (CEPLAN)</h3>'
        '</div>'
        '<div class="ceplan-stats-strip">'
        '<div class="ceplan-stat-box"><div class="ceplan-stat-num">51</div><div class="ceplan-stat-label">PN Aprobadas</div></div>'
        '<div class="ceplan-stat-box"><div class="ceplan-stat-num">38</div><div class="ceplan-stat-label">PN En Proceso</div></div>'
        '</div>'
        '<ul class="ceplan-legend-list">'
        '<li><strong>Hoja 1 (51 aprobadas):</strong> N°, Ministerio Rector, Nombre, Tipo (Multisectorial/Sectorial), D.S., Fecha y PDFs de la PN y norma.</li>'
        '<li><strong>Hoja 2 (38 en proceso):</strong> Cartera sectorial y multisectorial en actualización o formulación vigente.</li>'
        '</ul>'
        '<div class="ceplan-legend-actions">'
        f'{btn_ceplan}'
        f'{btn_xlsx}'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(spotlight_html, unsafe_allow_html=True)

    evals = load_evaluaciones_politicas()
    if not evals:
        return

    st.subheader("📊 Evaluaciones de Políticas y Programas Públicos en el Perú")
    st.caption(
        "Ordenadas por prioridad: primero programas sociales con su política nacional vinculada "
        "(Juntos, Pensión 65, Cuna Más, Qali Warma, Haku Wiñay, Beca 18, MIDIS) y luego evaluaciones generales y PpR."
    )

    c_prio, c_tipo, c_q = st.columns([1.2, 1.1, 1.5])
    with c_prio:
        prio_sel = st.selectbox(
            "Ámbito / Prioridad:",
            [
                "Todos (Programas Sociales primero)",
                "Solo Programas Sociales y PNDIS",
                "Solo Evaluaciones Generales y PpR",
            ],
            key="eval_prio_sel",
        )
    with c_tipo:
        tipo_sel = st.selectbox(
            "Tipo de evaluación:",
            ["Todos", "Impacto", "EDEP / Diseño y Presupuesto", "Seguimiento", "Implementación"],
            key="eval_tipo_sel",
        )
    with c_q:
        q_eval = st.text_input(
            "🔎 Filtrar evaluaciones:",
            placeholder="Ej: Juntos, Pensión 65, EDEP, Cuna Más, PpR...",
            key="eval_text_q",
        ).strip().lower()

    filtradas = evals
    if prio_sel == "Solo Programas Sociales y PNDIS":
        filtradas = [e for e in filtradas if e.get("nivel_prioridad") == "programa_social"]
    elif prio_sel == "Solo Evaluaciones Generales y PpR":
        filtradas = [e for e in filtradas if e.get("nivel_prioridad") == "politica_general"]

    if tipo_sel != "Todos":
        filtradas = [e for e in filtradas if e.get("tipo_evaluacion", "").lower() == tipo_sel.lower()]

    if q_eval:
        filtradas = [
            e for e in filtradas
            if q_eval in e.get("programa_o_ambito", "").lower()
            or q_eval in e.get("politica_publica", "").lower()
            or q_eval in e.get("titulo", "").lower()
            or q_eval in e.get("hallazgo_clave", "").lower()
            or q_eval in e.get("entidad_evaluadora", "").lower()
        ]

    sociales = [e for e in filtradas if e.get("nivel_prioridad") == "programa_social"]
    generales = [e for e in filtradas if e.get("nivel_prioridad") != "programa_social"]

    if not filtradas:
        st.info("No se encontraron evaluaciones que coincidan con los filtros aplicados.")
        return

    if sociales:
        st.markdown(
            f'<div class="eval-priority-banner">1. Prioridad: Programas Sociales y sus Políticas Públicas ({len(sociales)})</div>',
            unsafe_allow_html=True,
        )
        _render_eval_cards_grid(sociales)

    if generales:
        st.markdown(
            f'<div class="eval-priority-banner is-general">2. Evaluaciones Generales de Políticas Públicas, SINAPLAN y PpR ({len(generales)})</div>',
            unsafe_allow_html=True,
        )
        _render_eval_cards_grid(generales)


def _render_revistas_congresos_papers() -> None:
    """Renderiza revistas de gestión pública, memorias de congresos y papers recientes al final de Polity."""
    datos = load_revistas_gestion()
    revistas = datos.get("revistas", [])
    memorias = datos.get("memorias_congresos", [])
    papers = datos.get("papers_ensayos", [])

    if not (revistas or memorias or papers):
        return

    st.header("📚 Revistas, Memorias de Congresos y Papers en Gestión y Política Pública")
    st.markdown(
        "Selección curada para el análisis académico y comparado en **Perú y Latinoamérica**: "
        "revistas especializadas (*Saber Servir*, *CLAD*, *CIDE*, *INAP*, *U. de Chile*, *PUCP*, *Externado*), "
        "memorias de congresos internacionales y artículos recientes verificados."
    )

    tab_rev, tab_mem, tab_pap = st.tabs([
        f"📰 Revistas Especializadas ({len(revistas)})",
        f"🏛️ Memorias de Congresos ({len(memorias)})",
        f"📄 Papers y Ensayos Recientes ({len(papers)})",
    ])

    with tab_rev:
        cards_rev = []
        for r in revistas:
            btn = _action_button(r.get("url"), "Ir a la revista ↗")
            cards_rev.append(
                f'<div class="fuente-card">'
                f'<div>'
                f'<div class="card-header-meta">'
                f'<span class="badge-tipo">{escape(r.get("tipo", "REVISTA"))}</span>'
                f'<span class="badge-continua">{escape(r.get("frecuencia", "")).upper()}</span>'
                f'</div>'
                f'<div class="inst">{escape(r.get("institucion", ""))} • {escape(r.get("pais_alcance", ""))}</div>'
                f'<h4>{escape(r.get("titulo", ""))}</h4>'
                f'<p>{escape(r.get("descripcion", ""))}</p>'
                f'<div class="card-verified-meta">✓ {escape(r.get("acceso", "Acceso Abierto"))}</div>'
                f'</div>'
                f'<div class="card-footer-action">{btn}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="fuentes-grid">{"".join(cards_rev)}</div>', unsafe_allow_html=True)

    with tab_mem:
        cards_mem = []
        for m in memorias:
            btn = _action_button(m.get("url"), "Consultar memorias ↗")
            cards_mem.append(
                f'<div class="fuente-card">'
                f'<div>'
                f'<div class="card-header-meta">'
                f'<span class="badge-tipo">{escape(m.get("tipo", "MEMORIA CONGRESO"))}</span>'
                f'<span class="badge-freq-anual">{escape(m.get("alcance", "IBEROAMÉRICA")).upper()}</span>'
                f'</div>'
                f'<div class="inst">{escape(m.get("institucion", ""))}</div>'
                f'<h4>{escape(m.get("titulo", ""))}</h4>'
                f'<p>{escape(m.get("descripcion", ""))}</p>'
                f'</div>'
                f'<div class="card-footer-action">{btn}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="fuentes-grid">{"".join(cards_mem)}</div>', unsafe_allow_html=True)

    with tab_pap:
        cards_pap = []
        for p in papers:
            btn = _action_button(p.get("url"), "Leer artículo ↗")
            cards_pap.append(
                f'<div class="fuente-card">'
                f'<div>'
                f'<div class="card-header-meta">'
                f'<span class="badge-tipo">{escape(p.get("tipo", "PAPER"))}</span>'
                f'<span class="badge-freq-permanente">{escape(p.get("ambito", "")).upper()}</span>'
                f'</div>'
                f'<div class="inst">{escape(p.get("revista", ""))}</div>'
                f'<h4>{escape(p.get("titulo", ""))}</h4>'
                f'<p>{escape(p.get("resumen", ""))}</p>'
                f'<div class="card-verified-meta">📅 Publicado: {escape(p.get("anio", "2026"))}</div>'
                f'</div>'
                f'<div class="card-footer-action">{btn}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="fuentes-grid">{"".join(cards_pap)}</div>', unsafe_allow_html=True)


def render_polity():
    ficha_qp = st.query_params.get("ficha")
    if ficha_qp:
        render_ficha_tecnica_detalle(str(ficha_qp), origen="polity")
        return

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

    # BASE DE DATOS CEPLAN Y EVALUACIONES DE POLÍTICAS Y PROGRAMAS PÚBLICOS
    _render_ceplan_y_evaluaciones()

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

    st.markdown("---")

    # REVISTAS, MEMORIAS DE CONGRESOS Y PAPERS (Al final de Polity and Policy)
    _render_revistas_congresos_papers()
