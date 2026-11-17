"""Sección unificada: Biblioteca, Notas y Revistas."""

import importlib
import streamlit as st

from components.cards import (
    _action_button,
    escape,
    render_academico_carousel,
    render_eventos_alertas_carousel,
    render_eventos_grid,
    render_kpi_ribbon,
    render_nota_horizontal,
    render_nota_reader,
)
import utils.loaders as _loaders_mod
if not hasattr(_loaders_mod, "load_revistas_gestion"):
    importlib.reload(_loaders_mod)

from utils.loaders import (
    load_academico,
    load_eventos,
    load_eventos_alertas,
    load_notas,
    load_revistas_gestion,
    sanitize_slug_param,
)


def _render_nota_detail(nota: dict) -> None:
    render_nota_reader(nota, "← Volver a Notas y Ensayos", key_prefix="bib")


def _render_tab_notas(notas: list) -> None:
    if not notas:
        st.info("No se encontraron notas registradas.")
        return

    for idx, nota in enumerate(notas):
        render_nota_horizontal(nota)
        if st.button("📖 Leer artículo completo →", key=f"btn_bib_read_{nota.get('id')}_{idx}"):
            st.session_state["selected_note_id"] = nota.get("id")
            st.rerun()
        st.markdown("<div class='note-item-spacer'></div>", unsafe_allow_html=True)


def _render_tab_revistas_y_papers(rev_data: dict, academico: list) -> None:
    revistas = rev_data.get("revistas", [])
    papers = rev_data.get("papers_ensayos", [])

    if academico:
        st.subheader("🔬 Radar Académico (OpenAlex)")
        render_academico_carousel(academico)
        st.markdown("---")

    if revistas:
        st.markdown('<div id="revistas-lista"></div>', unsafe_allow_html=True)
        st.subheader(f"📰 Revistas de Gestión y Política Pública ({len(revistas)})")
        c1, c2 = st.columns([2, 1])
        with c1:
            q_rev = st.text_input(
                "🔎 Buscar revista o país:",
                placeholder="Ej: Saber Servir, CLAD, CIDE, PUCP, Educación...",
                key="bib_rev_search",
            ).strip().lower()
        with c2:
            alcance_opts = ["Todos", "Perú", "Latinoamérica / Internacional"]
            alcance_sel = st.selectbox("Alcance:", alcance_opts, key="bib_rev_alcance")

        filtradas = []
        for r in revistas:
            pais = r.get("pais_alcance", "")
            if alcance_sel == "Perú" and "perú" not in pais.lower():
                continue
            if alcance_sel == "Latinoamérica / Internacional" and pais.lower() == "perú":
                continue
            if q_rev:
                blob = f"{r.get('titulo', '')} {r.get('institucion', '')} {pais} {r.get('descripcion', '')}".lower()
                if q_rev not in blob:
                    continue
            filtradas.append(r)

        if filtradas:
            cards_rev = []
            for r in filtradas:
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
        else:
            st.info("No hay revistas que coincidan con ese filtro.")

    if papers:
        st.markdown("---")
        st.subheader(f"📄 Papers y Ensayos Destacados ({len(papers)})")
        cards_pap = []
        for p in papers:
            btn = _action_button(p.get("url"), "Leer artículo ↗")
            cards_pap.append(
                f'<div class="fuente-card">'
                f'<div>'
                f'<div class="card-header-meta">'
                f'<span class="badge-tipo">{escape(p.get("tipo", "PAPER"))}</span>'
                f'<span class="badge-freq badge-domain-blue">{escape(p.get("ambito", "")).upper()}</span>'
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


def _render_tab_congresos_y_memorias(rev_data: dict, eventos: list, alertas: list) -> None:
    memorias = rev_data.get("memorias_congresos", [])

    if alertas:
        st.subheader("📢 Novedades y Convocatorias")
        render_eventos_alertas_carousel(alertas)
        st.markdown("---")

    if memorias:
        st.subheader(f"🏛️ Memorias de Congresos ({len(memorias)})")
        cards_mem = []
        for m in memorias:
            btn = _action_button(m.get("url"), "Consultar memorias ↗")
            cards_mem.append(
                f'<div class="fuente-card">'
                f'<div>'
                f'<div class="card-header-meta">'
                f'<span class="badge-tipo">{escape(m.get("tipo", "MEMORIA CONGRESO"))}</span>'
                f'<span class="badge-freq badge-freq-anual">{escape(m.get("alcance", "IBEROAMÉRICA")).upper()}</span>'
                f'</div>'
                f'<div class="inst">{escape(m.get("institucion", ""))}</div>'
                f'<h4>{escape(m.get("titulo", ""))}</h4>'
                f'<p>{escape(m.get("descripcion", ""))}</p>'
                f'</div>'
                f'<div class="card-footer-action">{btn}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="fuentes-grid">{"".join(cards_mem)}</div>', unsafe_allow_html=True)
        st.markdown("---")

    st.subheader(f"📅 Congresos y Coloquios ({len(eventos)})")
    if eventos:
        render_eventos_grid(eventos)
    else:
        st.info("No hay congresos registrados por el momento.")


def render_biblioteca() -> None:
    """Renderiza el módulo consolidado Biblioteca y Revistas."""
    notas = load_notas()
    selected_id = st.session_state.get("selected_note_id")
    if selected_id:
        nota_sel = next((n for n in notas if n.get("id") == selected_id), None)
        if nota_sel:
            _render_nota_detail(nota_sel)
            return
        st.session_state["selected_note_id"] = None

    rev_data = load_revistas_gestion()
    academico = load_academico()
    eventos = load_eventos()
    alertas = load_eventos_alertas()

    revistas_count = len(rev_data.get("revistas", []))
    papers_count = len(rev_data.get("papers_ensayos", []))
    memorias_count = len(rev_data.get("memorias_congresos", []))

    st.title("📚 Biblioteca, Notas y Revistas")
    st.markdown(
        '<p class="hero-subtitle">Ensayos propios, revistas especializadas en gestión pública, papers recientes y memorias de congresos.</p>',
        unsafe_allow_html=True,
    )

    render_kpi_ribbon([
        {
            "icon": "📝",
            "value": str(len(notas)),
            "label": "Notas y Ensayos",
            "sub": "Investigación aplicada",
            "href": "?vista=biblioteca&tab=notas",
        },
        {
            "icon": "📰",
            "value": str(revistas_count),
            "label": "Revistas",
            "sub": "Perú y Latinoamérica",
            "href": "?vista=biblioteca&tab=revistas#revistas-lista",
        },
        {
            "icon": "📄",
            "value": str(papers_count + len(academico)),
            "label": "Papers",
            "sub": "Curados y OpenAlex",
            "href": "?vista=biblioteca&tab=revistas",
        },
        {
            "icon": "🏛️",
            "value": str(memorias_count + len(eventos)),
            "label": "Congresos",
            "sub": "Actas y convocatorias",
            "href": "?vista=biblioteca&tab=congresos",
        },
    ])

    tab_opts = [
        f"📰 Revistas y Papers ({revistas_count + papers_count})",
        f"📝 Notas y Ensayos ({len(notas)})",
        f"🏛️ Congresos y Memorias ({memorias_count + len(eventos)})",
    ]
    tab_qp_map = {"revistas": tab_opts[0], "notas": tab_opts[1], "congresos": tab_opts[2]}
    tab_qp = sanitize_slug_param(st.query_params.get("tab"), max_len=30)
    if tab_qp in tab_qp_map and st.session_state.get("_last_tab_qp_bib") != tab_qp:
        st.session_state["bib_active_tab"] = tab_qp_map[tab_qp]
        st.session_state._last_tab_qp_bib = tab_qp

    active_tab = st.segmented_control(
        "Sección de Biblioteca y Revistas",
        options=tab_opts,
        default=st.session_state.get("bib_active_tab", tab_opts[0]),
        selection_mode="single",
        label_visibility="collapsed",
        key="bib_active_tab",
        width="stretch",
    )
    if not active_tab:
        active_tab = tab_opts[0]

    st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    if active_tab == tab_opts[0]:
        _render_tab_revistas_y_papers(rev_data, academico)
    elif active_tab == tab_opts[1]:
        _render_tab_notas(notas)
    else:
        _render_tab_congresos_y_memorias(rev_data, eventos, alertas)
