"""Sección dedicada: Rastrea la Norma (Beta v1-rastro-norma)."""

import html
import streamlit as st

import config
from components.cards import render_normas_carousel
from sections.normas_comentadas import (
    render_ficha_detalle,
    render_normas_comentadas_subsection,
    render_normas_showcase_strip,
    render_normas_visual_collection,
)
from utils.loaders import (
    load_estado_pipeline,
    load_normas,
    load_normas_oficiales,
    load_politicas_nacionales,
)


def construir_diagrama_flujo_normas_html(
    ia_habilitada: bool,
    modelo_ia: str,
    ultimo_estado: str,
    ultimo_intento: str,
    total_fichas: int,
) -> str:
    """Construye el HTML + SVG animado del diagrama '¿Cómo seguimos la norma?'."""
    estado_ia_txt = (
        f"IA activa · {html.escape(modelo_ia)}"
        if ia_habilitada
        else "Modo radar determinístico"
    )
    estado_sync_txt = html.escape(ultimo_intento or "Sincronización diaria 11:15 y 23:15 UTC")
    estado_badge_txt = html.escape(ultimo_estado or "listo")

    html_crudo = f"""
<div class="flow-pipeline-shell">
<div class="flow-shell-top">
<div>
<h2 class="flow-shell-title">¿Cómo seguimos la norma?</h2>
<p class="flow-shell-sub">Flujo automatizado y verificable desde la publicación oficial en <strong>El Peruano</strong> hasta la ficha analítica en Apocuna.</p>
</div>
</div>
<div class="flow-track-wrapper">
<svg class="flow-connector-svg" viewBox="0 0 1000 28" preserveAspectRatio="none" aria-hidden="true">
<line class="flow-connector-base" x1="100" y1="14" x2="900" y2="14" />
<line class="flow-connector-dash" x1="100" y1="14" x2="900" y2="14" />
<circle class="flow-node-anchor" cx="100" cy="14" r="5" />
<circle class="flow-node-anchor" cx="300" cy="14" r="5" />
<circle class="flow-node-anchor" cx="500" cy="14" r="5" />
<circle class="flow-node-anchor" cx="700" cy="14" r="5" />
<circle class="flow-node-anchor" cx="900" cy="14" r="5" />
<circle class="flow-packet-dot" cx="100" cy="14" r="5.5">
<animate attributeName="cx" values="100;300;500;700;900" keyTimes="0;0.25;0.5;0.75;1" dur="7.5s" repeatCount="indefinite" />
</circle>
</svg>
<div class="flow-steps-grid">
<div class="flow-step-card" style="--step-index:0;">
<div class="flow-step-head">
<span class="flow-step-num">PASO 01</span>
<span class="flow-step-icon">🏛️</span>
</div>
<h3 class="flow-step-title">Recolección oficial</h3>
<p class="flow-step-desc">Consulta respetuosa del cuadernillo diario de Normas Legales en <code>busquedas.elperuano.pe</code> (2 pasadas al día).</p>
<span class="flow-step-tag">robots.txt + Crawl-delay</span>
</div>
<div class="flow-step-card" style="--step-index:1;">
<div class="flow-step-head">
<span class="flow-step-num">PASO 02</span>
<span class="flow-step-icon">🧭</span>
</div>
<h3 class="flow-step-title">Filtro y Clasificación</h3>
<p class="flow-step-desc">Reglas determinísticas excluyen trámites/viajes y asignan eje <strong>Polity</strong> o <strong>Policy</strong> + Política Nacional.</p>
<span class="flow-step-tag">Sin personas · Catálogo CEPLAN</span>
</div>
<div class="flow-step-card" style="--step-index:2;">
<div class="flow-step-head">
<span class="flow-step-num">PASO 03</span>
<span class="flow-step-icon">🔐</span>
</div>
<h3 class="flow-step-title">Trazabilidad SHA-256</h3>
<p class="flow-step-desc">Extrae artículos clave y normas citadas en memoria con hash SHA-256 verificable, sin almacenar textos completos ni PDFs.</p>
<span class="flow-step-tag">Trazabilidad jurídica</span>
</div>
<div class="flow-step-card" style="--step-index:3;">
<div class="flow-step-head">
<span class="flow-step-num">PASO 04</span>
<span class="flow-step-icon">✨</span>
</div>
<h3 class="flow-step-title">Borrador IA + Verificador</h3>
<p class="flow-step-desc">Gemini sintetiza <em>qué dispone</em>, <em>repercusiones</em> y preguntas; un verificador estricto valida cada cita contra el texto oficial.</p>
<span class="flow-step-tag">{estado_ia_txt}</span>
</div>
<div class="flow-step-card" style="--step-index:4;">
<div class="flow-step-head">
<span class="flow-step-num">PASO 05</span>
<span class="flow-step-icon">⚖️</span>
</div>
<h3 class="flow-step-title">Publicación y Revisión</h3>
<p class="flow-step-desc">Indexa las fichas con enlace al boletín original y permite reemplazo curado por revisión humana verificada.</p>
<span class="flow-step-tag">Rama data · {total_fichas} fichas</span>
</div>
</div>
</div>
<div class="flow-telemetry-bar">
<span class="flow-telemetry-chip">⚙️ {estado_ia_txt}</span>
<span class="flow-telemetry-chip">📡 Estado radar: {estado_badge_txt}</span>
<span class="flow-telemetry-chip">🕒 Último ciclo: {estado_sync_txt}</span>
</div>
</div>
""".strip()
    return html_crudo


def render_rastrea_la_norma() -> None:
    """Renderiza la sección principal 'Rastrea la Norma' con los filtros arriba."""
    st.markdown(
        """
        <div class="rastrea-hero-header">
          <div>
            <h1 style="margin:0;color:var(--text-title);">🔍 Rastrea la Norma</h1>
            <p style="margin:0.25rem 0 0 0;color:var(--text-muted);font-size:0.95rem;">
              Seguimiento diario de normas de <strong>El Peruano</strong> por ejes <strong>Polity &amp; Policy</strong>.
            </p>
          </div>
          <span class="rastrea-beta-pill">
            <span class="rastrea-beta-dot"></span>
            Radar Activo
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fichas_oficiales = load_normas_oficiales()
    catalogo = load_politicas_nacionales()
    catalogo_map = {p["id"]: p["nombre"] for p in catalogo if isinstance(p, dict) and p.get("id")}

    norma_sel_id = st.query_params.get("norma")
    if norma_sel_id:
        objetivo = next((f for f in fichas_oficiales if f.get("id") == norma_sel_id), None)
        if objetivo:
            render_ficha_detalle(objetivo, catalogo_map)
            return
        st.warning(f"No se encontró la ficha solicitada (`{norma_sel_id}`). Mostrando vista completa.")

    estado_pipe = load_estado_pipeline()
    estado_diario = (
        estado_pipe.get("fuentes", {}).get("normas_diario", {})
        if isinstance(estado_pipe, dict)
        else {}
    )

    with st.expander("⚙️ Cómo funciona la verificación normativa (5 pasos)", expanded=False):
        flujo_html = construir_diagrama_flujo_normas_html(
            ia_habilitada=bool(getattr(config, "NORMAS_IA_HABILITADA", False)),
            modelo_ia=str(getattr(config, "GEMINI_MODELO_NORMAS", "gemini-3.5-flash-lite")),
            ultimo_estado=str(estado_diario.get("ultimo_estado") or "activo"),
            ultimo_intento=str(estado_diario.get("ultimo_intento") or "2 pasadas diarias (11:15 y 23:15 UTC)"),
            total_fichas=len(fichas_oficiales),
        )
        st.markdown(flujo_html, unsafe_allow_html=True)

    normas_prensa = load_normas()
    normas_filtradas = [n for n in normas_prensa if n.get("grupo") == "Noticias sobre normas legales"] or normas_prensa

    tab_diario, tab_prensa = st.tabs([
        f"🏛️ Normas de El Peruano ({len(fichas_oficiales)})",
        f"📰 Monitoreo en Prensa ({len(normas_filtradas)})",
    ])

    with tab_diario:
        if fichas_oficiales:
            render_normas_showcase_strip(fichas_oficiales)
        render_normas_comentadas_subsection(
            show_header=False,
            show_showcase=False,
            skip_detail_check=True,
        )

    with tab_prensa:
        st.caption("Decretos, proyectos de ley y resoluciones sectoriales reportados en prensa.")
        render_normas_carousel(normas_filtradas)
