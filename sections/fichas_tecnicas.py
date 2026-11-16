"""Vista dedicada de Fichas Técnicas Metodológicas para fuentes cuantitativas y herramientas FEN."""

import html
import urllib.parse
from typing import Any

import streamlit as st

from utils.loaders import load_fichas_tecnicas_index


def _safe_http_url(url: Any) -> str | None:
    """Valida que la URL use esquema http:// o https:// explícito."""
    if not isinstance(url, str):
        return None
    limpia = url.strip()
    if limpia.startswith(("https://", "http://")):
        return limpia
    return None


def _volver_al_catalogo(origen: str) -> None:
    """Limpia el parámetro de ficha y retorna al catálogo correspondiente."""
    if "ficha" in st.query_params:
        del st.query_params["ficha"]
    if origen == "fen":
        st.query_params["vista"] = "fen"
        st.session_state.current_page = "Monitoreo El Niño"
        st.session_state._last_qp_routed = "fen||"
    else:
        st.query_params["vista"] = "polity"
        st.session_state.current_page = "Políticas y Datos"
        st.session_state._last_qp_routed = "polity||"
    st.rerun()


def render_ficha_tecnica_detalle(ficha_id: str, origen: str = "polity") -> bool:
    """Renderiza la Ficha Técnica Metodológica completa de una fuente o herramienta."""
    index = load_fichas_tecnicas_index()
    ficha = index.get(ficha_id)

    volver_label = (
        "← Volver a Monitoreo El Niño"
        if origen == "fen"
        else "← Volver a Políticas y Datos"
    )
    if st.button(volver_label, key=f"btn_volver_ficha_top_{ficha_id}_{origen}"):
        _volver_al_catalogo(origen)

    if not ficha:
        st.warning(f"No se encontró la ficha técnica solicitada (`{ficha_id}`).")
        return False

    fid_canonico = str(ficha.get("id") or ficha_id)
    nombre_esc = html.escape(str(ficha.get("nombre") or "Fuente sin nombre"))
    ruta_origen = "MONITOREO EL NIÑO" if origen == "fen" else "POLÍTICAS Y DATOS"
    st.markdown(
        f'<div class="apocuna-breadcrumb">{ruta_origen} / FICHA TÉCNICA / <strong>{html.escape(fid_canonico.upper())}</strong></div>',
        unsafe_allow_html=True,
    )
    inst_esc = html.escape(str(ficha.get("institucion") or "Institución Oficial"))
    cat_esc = html.escape(str(ficha.get("categoria") or "FUENTE DE INVESTIGACIÓN"))
    tipo_esc = html.escape(str(ficha.get("tipo_insumo") or "Datos / Recurso"))
    freq_esc = html.escape(str(ficha.get("frecuencia") or "Periódica"))
    acceso_esc = html.escape(str(ficha.get("acceso") or "Acceso abierto"))
    resumen_esc = html.escape(str(ficha.get("resumen_ejecutivo") or ""))

    url_of = _safe_http_url(ficha.get("url_oficial"))
    btn_externo = (
        f'<a href="{html.escape(url_of, quote=True)}" target="_blank" rel="noopener noreferrer" '
        'class="btn-open">🌐 Acceder a la fuente oficial ↗</a>'
        if url_of
        else ""
    )

    st.markdown(
        f"""
        <div class="ficha-tecnica-hero">
          <div class="ficha-tecnica-hero-topbar"></div>
          <div class="ficha-tecnica-hero-inner">
            <div class="ficha-tecnica-badges">
              <span class="apocunoso-order-badge">FICHA TÉCNICA METODOLÓGICA</span>
              <span class="badge-portal">{cat_esc}</span>
              <span class="badge-freq badge-freq-mensual">{freq_esc}</span>
            </div>
            <div class="inst">{inst_esc}</div>
            <h1 class="ficha-tecnica-title">{nombre_esc}</h1>
            <p class="ficha-tecnica-resumen">{resumen_esc}</p>
            <div class="ficha-tecnica-meta-strip">
              <span><strong>📦 Tipo de insumo:</strong> {tipo_esc}</span>
              <span><strong>🔓 Condición de acceso:</strong> {acceso_esc}</span>
            </div>
            <div class="card-actions-row">
              {btn_externo}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    permalink = f"?vista={urllib.parse.quote(origen)}&ficha={urllib.parse.quote(fid_canonico)}"
    st.caption(f"Permalink directo de esta ficha técnica: `{permalink}`")

    # Bloque 01: Contenido, Módulos y Formatos
    contenido = ficha.get("contenido_variables") or {}
    cont_desc = html.escape(str(contenido.get("descripcion") or ""))
    modulos = contenido.get("modulos_principales") or []
    modulos_li = "".join(f"<li>{html.escape(str(m))}</li>" for m in modulos)
    formatos = contenido.get("formatos") or []
    formatos_chips = "".join(
        f'<span class="ficha-format-chip">{html.escape(str(fmt))}</span>' for fmt in formatos
    )

    # Bloque 02: Alcance, Cobertura y Llaves de Cruce
    alcance = ficha.get("alcance_cobertura") or {}
    unidad_esc = html.escape(str(alcance.get("unidad_analisis") or "Por confirmar"))
    geo_esc = html.escape(str(alcance.get("cobertura_geografica") or "Nacional"))
    temp_esc = html.escape(str(alcance.get("cobertura_temporal") or "Vigente"))
    llaves_esc = html.escape(str(alcance.get("llaves_cruce") or "UBIGEO / Identificador institucional"))

    # Bloque 03: Diferentes Usos
    usos = ficha.get("usos_aplicaciones") or []
    usos_li = "".join(f"<li>{html.escape(str(u))}</li>" for u in usos)

    # Bloque 04: Precauciones Metodológicas
    precauciones = ficha.get("precauciones_metodologicas") or []
    prec_li = "".join(f"<li>{html.escape(str(p))}</li>" for p in precauciones)

    st.markdown(
        f"""
        <div class="apocunoso-about-grid-2col">
          <article class="apocunoso-about-card about-card-blue">
            <div class="apocunoso-about-card-topbar"></div>
            <div class="apocunoso-about-card-inner">
              <div class="apocunoso-about-card-meta">
                <span class="apocunoso-order-badge">SECCIÓN 01</span>
                <span class="apocunoso-about-eyebrow">CONTENIDO · VARIABLES Y FORMATOS</span>
              </div>
              <h2 class="apocunoso-about-question">¿Qué contiene y en qué formatos?</h2>
              <div class="apocunoso-about-body">
                <p>{cont_desc}</p>
                <ul>{modulos_li}</ul>
                <div class="ficha-formats-row">{formatos_chips}</div>
              </div>
            </div>
          </article>

          <article class="apocunoso-about-card about-card-green">
            <div class="apocunoso-about-card-topbar"></div>
            <div class="apocunoso-about-card-inner">
              <div class="apocunoso-about-card-meta">
                <span class="apocunoso-order-badge">SECCIÓN 02</span>
                <span class="apocunoso-about-eyebrow">ALCANCE · COBERTURA Y CRUCES</span>
              </div>
              <h2 class="apocunoso-about-question">Alcance, cobertura y llaves de cruce</h2>
              <div class="apocunoso-about-body">
                <div class="ficha-scope-kv">
                  <div><strong>Unidad de análisis:</strong> {unidad_esc}</div>
                  <div><strong>Cobertura geográfica:</strong> {geo_esc}</div>
                  <div><strong>Serie temporal:</strong> {temp_esc}</div>
                  <div><strong>Llaves recomendadas de cruce:</strong> <code>{llaves_esc}</code></div>
                </div>
              </div>
            </div>
          </article>

          <article class="apocunoso-about-card about-card-gold">
            <div class="apocunoso-about-card-topbar"></div>
            <div class="apocunoso-about-card-inner">
              <div class="apocunoso-about-card-meta">
                <span class="apocunoso-order-badge">SECCIÓN 03</span>
                <span class="apocunoso-about-eyebrow">APLICACIONES EN INVESTIGACIÓN</span>
              </div>
              <h2 class="apocunoso-about-question">Usos recomendados en política pública</h2>
              <div class="apocunoso-about-body">
                <ul>{usos_li}</ul>
              </div>
            </div>
          </article>

          <article class="apocunoso-about-card about-card-pink">
            <div class="apocunoso-about-card-topbar"></div>
            <div class="apocunoso-about-card-inner">
              <div class="apocunoso-about-card-meta">
                <span class="apocunoso-order-badge">SECCIÓN 04</span>
                <span class="apocunoso-about-eyebrow">RIGOR METODOLÓGICO</span>
              </div>
              <h2 class="apocunoso-about-question">Precauciones y limitaciones</h2>
              <div class="apocunoso-about-body">
                <ul>{prec_li}</ul>
              </div>
            </div>
          </article>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bloque 05: Investigaciones de Referencia
    refs = ficha.get("investigaciones_referencia") or []
    refs_html = []
    for ref in refs:
        r_tit = html.escape(str(ref.get("titulo") or ""))
        r_aut = html.escape(str(ref.get("autores") or ""))
        r_anio = html.escape(str(ref.get("anio") or ""))
        r_uso = html.escape(str(ref.get("uso_especifico") or ""))
        r_url = _safe_http_url(ref.get("url"))
        r_link = (
            f'<a href="{html.escape(r_url, quote=True)}" target="_blank" rel="noopener noreferrer" '
            'class="btn-fen-secondary">Consultar estudio / repositorio ↗</a>'
            if r_url
            else ""
        )
        refs_html.append(
            f'<div class="ficha-ref-card">'
            f'<div class="ficha-ref-meta"><span>{r_aut}</span><span>{r_anio}</span></div>'
            f'<h4 class="ficha-ref-title">{r_tit}</h4>'
            f'<p class="ficha-ref-uso"><strong>Cómo emplea esta fuente:</strong> {r_uso}</p>'
            f'<div class="ficha-ref-action">{r_link}</div>'
            f'</div>'
        )

    st.markdown(
        f"""
        <section class="apocunoso-about-refs-card">
          <div class="apocunoso-about-intro-head">
            <span class="apocunoso-order-badge">05 · EVIDENCIA APLICADA</span>
            <span class="apocunoso-about-tag">INVESTIGACIONES Y REFERENCIAS DONDE SE HA UTILIZADO</span>
          </div>
          <h2 class="apocunoso-about-question">Estudios y reportes recomendados</h2>
          <div class="ficha-refs-grid">
            {"".join(refs_html)}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Volver al catálogo", key=f"btn_volver_ficha_bottom_{ficha_id}_{origen}"):
        _volver_al_catalogo(origen)

    return True
