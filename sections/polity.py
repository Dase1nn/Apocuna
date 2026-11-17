import base64
import os

import streamlit as st

from components.cards import (
    _action_button,
    escape,
    render_ckan_carousel,
    render_fuentes_grid,
    render_kpi_ribbon,
    render_polity_alertas_carousel,
    safe_url,
)
from sections.fichas_tecnicas import render_ficha_tecnica_detalle
from utils.loaders import (
    fetch_ckan_datasets,
    load_evaluaciones_politicas,
    load_fuentes,
    load_informes_sectoriales,
    load_polity_alertas,
    sanitize_slug_param,
)

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

BLOQUES_FUENTES = [
    ("Datos abiertos y microdatos", "📊 Datos Abiertos y Microdatos", True),
    ("Control gubernamental y conflictividad social", "⚖️ Control y Conflictividad", False),
    ("Think tanks y repositorios", "🧠 Think Tanks Nacionales", False),
    ("Organismos multilaterales", "🌍 Multilaterales", False),
]


@st.cache_data(show_spinner=False)
def _load_ceplan_preview_data_uri(mtime: float) -> str:
    """Carga y codifica en base64 la captura de la base de datos CEPLAN."""
    _ = mtime
    with open(_CEPLAN_PREVIEW_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _filter_fuentes(fuentes: list, bloque_sel: str, q_raw: str) -> list:
    q = q_raw.strip().lower()
    res = fuentes
    if bloque_sel != "Todos":
        res = [f for f in res if (f.get("bloque") or "").lower() == bloque_sel.lower()]
    if q:
        res = [
            f for f in res
            if q in (f.get("nombre") or "").lower()
            or q in (f.get("institucion") or "").lower()
            or q in (f.get("descripcion_corta") or "").lower()
            or q in (f.get("bloque") or "").lower()
        ]
    return res


def _render_tab_datos_y_microdatos(fuentes: list) -> None:
    st.subheader("🗄️ Catálogo Unificado de Fuentes y Microdatos")
    st.caption("Repositorios oficiales verificados. Las fuentes cuantitativas incluyen Ficha Técnica metodológica.")

    c1, c2 = st.columns([2, 1.2])
    with c1:
        q_fuente = st.text_input(
            "🔎 Buscar fuente o institución:",
            placeholder="Ej: ENAHO, INCORE, MINSA, Defensoría, GRADE, CEPAL...",
            key="datos_fuentes_search",
        )
    with c2:
        bloques_ops = ["Todos"] + [b[0] for b in BLOQUES_FUENTES]
        bloque_sel = st.selectbox("Categoría:", bloques_ops, key="datos_fuentes_bloque")

    if q_fuente or bloque_sel != "Todos":
        filtradas = _filter_fuentes(fuentes, bloque_sel, q_fuente)
        st.caption(f"Mostrando **{len(filtradas)}** de **{len(fuentes)}** fuentes verificadas.")
        render_fuentes_grid(filtradas)
    else:
        for key_bloque, titulo_bloque, exp_default in BLOQUES_FUENTES:
            fuentes_bloque = [f for f in fuentes if f.get("bloque", "").lower() == key_bloque.lower()]
            with st.expander(f"{titulo_bloque} ({len(fuentes_bloque)})", expanded=exp_default):
                render_fuentes_grid(fuentes_bloque)

    st.markdown("---")
    with st.expander("🔄 Portales Nacionales CKAN (PCM / MINSA REUNIS / CDC)", expanded=False):
        portales_ckan = [f for f in fuentes if f.get("id") in ("f_001", "f_002", "f_003", "f_004")]
        ckan_datasets = fetch_ckan_datasets()
        render_ckan_carousel(ckan_datasets, portales_directos=portales_ckan)


def _render_eval_cards_grid(items: list) -> None:
    """Renderiza la grilla de evaluaciones en estética apocunoso-style."""
    if not items:
        st.info("No se encontraron evaluaciones con esos filtros.")
        return

    cards_html = []
    for item in items:
        is_social = item.get("nivel_prioridad") == "programa_social"
        badge_left = "PROGRAMA SOCIAL" if is_social else "POLÍTICA PÚBLICA"
        tipo_raw = str(item.get("tipo_evaluacion", "Evaluación"))
        tipo_short = "EDEP" if "edep" in tipo_raw.lower() else tipo_raw
        anio = escape(item.get("anio", ""))
        badge_right = f"{escape(tipo_short).upper()} • {anio}" if anio else escape(tipo_short).upper()

        t_low = tipo_short.lower()
        if "impacto" in t_low:
            badge_right_cls = "badge-freq badge-domain-blue"
        elif "seguimiento" in t_low:
            badge_right_cls = "badge-freq badge-domain-green"
        elif "edep" in t_low:
            badge_right_cls = "badge-freq badge-domain-gold"
        else:
            badge_right_cls = "badge-freq badge-domain-pink"

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
            f'<div class="card-verified-meta" style="margin-bottom:0.4rem;">📌 {politica}</div>'
            f'<p>{hallazgo}</p>'
            f'<div class="card-verified-meta">🏛️ {entidad}</div>'
            f'</div>'
            f'<div class="card-footer-action">{btn_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def _render_tab_ceplan_y_evaluaciones(evals: list) -> None:
    st.subheader("📋 Base de Datos CEPLAN (Políticas Nacionales)")
    st.caption("Registro maestro del SINAPLAN (51 Políticas Nacionales aprobadas y 38 en proceso).")

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
        '<li><strong>Hoja 1 (51 aprobadas):</strong> N°, Ministerio Rector, Tipo, D.S., Fecha y PDFs oficiales.</li>'
        '<li><strong>Hoja 2 (38 en proceso):</strong> Cartera en actualización o formulación vigente.</li>'
        '</ul>'
        '<div class="ceplan-legend-actions">'
        f'{btn_ceplan}'
        f'{btn_xlsx}'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(spotlight_html, unsafe_allow_html=True)

    if not evals:
        return

    st.markdown('<div id="evaluaciones"></div>', unsafe_allow_html=True)
    st.subheader("📊 Evaluaciones de Políticas y Programas Públicos")
    st.caption("Prioridad por programas sociales (Juntos, Pensión 65, Cuna Más, Qali Warma, Haku Wiñay, Beca 18) y evaluaciones PpR.")

    c_prio, c_tipo, c_q = st.columns([1.2, 1.1, 1.5])
    with c_prio:
        prio_sel = st.selectbox(
            "Ámbito:",
            [
                "Todos (Sociales primero)",
                "Solo Programas Sociales",
                "Solo Generales y PpR",
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
    if prio_sel == "Solo Programas Sociales":
        filtradas = [e for e in filtradas if e.get("nivel_prioridad") == "programa_social"]
    elif prio_sel == "Solo Generales y PpR":
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
        st.info("No se encontraron evaluaciones con esos criterios.")
        return

    if sociales:
        st.markdown(
            f'<div class="eval-priority-banner">1. Programas Sociales y Política Vinculada ({len(sociales)})</div>',
            unsafe_allow_html=True,
        )
        _render_eval_cards_grid(sociales)

    if generales:
        st.markdown(
            f'<div class="eval-priority-banner is-general">2. Evaluaciones Generales, SINAPLAN y PpR ({len(generales)})</div>',
            unsafe_allow_html=True,
        )
        _render_eval_cards_grid(generales)


def _render_tab_alertas_e_informes(alertas: list, informes: list) -> None:
    if alertas:
        st.subheader("📢 Alertas Institucionales Recientes")
        render_polity_alertas_carousel(alertas)
        st.markdown("---")

    st.subheader(f"📑 Informes Sectoriales Recientes ({len(informes)})")
    st.caption("Publicaciones puntuales del INEI, UNICEF, PNUD y Contraloría General.")
    if informes:
        render_fuentes_grid(informes)
    else:
        st.info("No hay informes sectoriales registrados.")


def render_polity():
    ficha_qp = sanitize_slug_param(st.query_params.get("ficha"), max_len=80)
    if ficha_qp:
        render_ficha_tecnica_detalle(ficha_qp, origen="polity")
        return

    st.title("🏛️ Políticas y Datos Abiertos")
    st.markdown(
        '<p class="hero-subtitle">Microdatos con ficha técnica, Políticas Nacionales (CEPLAN), evaluaciones públicas y vigilancia institucional.</p>',
        unsafe_allow_html=True,
    )

    fuentes = load_fuentes()
    evals = load_evaluaciones_politicas()
    alertas = load_polity_alertas()
    informes = load_informes_sectoriales()

    render_kpi_ribbon([
        {
            "icon": "🗄️",
            "value": str(len(fuentes)),
            "label": "Fuentes Maestras",
            "sub": "Microdatos, control y think tanks",
            "href": "?vista=polity&tab=datos",
        },
        {
            "icon": "📋",
            "value": "51 / 38",
            "label": "Políticas CEPLAN",
            "sub": "Aprobadas y en proceso",
            "href": "?vista=polity&tab=ceplan",
        },
        {
            "icon": "📊",
            "value": str(len(evals)),
            "label": "Evaluaciones",
            "sub": "Programas sociales y PpR",
            "href": "?vista=polity&tab=ceplan#evaluaciones",
        },
        {
            "icon": "📢",
            "value": str(len(alertas) + len(informes)),
            "label": "Alertas e Informes",
            "sub": "Coyuntura y control",
            "href": "?vista=polity&tab=alertas",
        },
    ])

    tab_opts = [
        f"📊 Datos y Microdatos ({len(fuentes)})",
        f"📋 CEPLAN y Evaluaciones ({len(evals)})",
        f"📢 Alertas e Informes ({len(alertas) + len(informes)})",
    ]
    tab_qp_map = {"datos": tab_opts[0], "ceplan": tab_opts[1], "alertas": tab_opts[2]}
    tab_qp = sanitize_slug_param(st.query_params.get("tab"), max_len=30)
    if tab_qp in tab_qp_map and st.session_state.get("_last_tab_qp_polity") != tab_qp:
        st.session_state["polity_active_tab"] = tab_qp_map[tab_qp]
        st.session_state._last_tab_qp_polity = tab_qp

    active_tab = st.segmented_control(
        "Sección de Políticas y Datos",
        options=tab_opts,
        default=st.session_state.get("polity_active_tab", tab_opts[0]),
        selection_mode="single",
        label_visibility="collapsed",
        key="polity_active_tab",
        width="stretch",
    )
    if not active_tab:
        active_tab = tab_opts[0]

    st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    if active_tab == tab_opts[0]:
        _render_tab_datos_y_microdatos(fuentes)
    elif active_tab == tab_opts[1]:
        _render_tab_ceplan_y_evaluaciones(evals)
    else:
        _render_tab_alertas_e_informes(alertas, informes)
