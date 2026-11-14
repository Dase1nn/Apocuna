"""Subsección y tarjetas visuales de Normas Legales Oficiales (El Peruano - Polity & Policy)."""

import html
import urllib.parse
from typing import Any, Dict, List, Optional

import streamlit as st

from utils.loaders import (
    load_estado_pipeline,
    load_norma_comentada_md,
    load_normas_oficiales,
    load_politicas_nacionales,
)


GITHUB_ISSUES_NEW_URL = "https://github.com/Dase1nn/Apocuna/issues/new"


def validar_url_http(url: Any) -> Optional[str]:
    """Permite únicamente esquemas HTTP/HTTPS explícitos y seguros."""
    if not isinstance(url, str):
        return None
    limpia = url.strip()
    if limpia.startswith("https://") or limpia.startswith("http://"):
        return limpia
    return None


def construir_url_reporte_error(ficha: Dict[str, Any]) -> str:
    """Genera URL segura de reporte de error hacia GitHub Issues."""
    nid = str(ficha.get("id") or "sin-id")
    numero = str(ficha.get("numero_raw") or ficha.get("numero") or "")
    titulo = f"Error en ficha de norma: {numero} ({nid})"
    cuerpo = (
        f"Ficha ID: `{nid}`\n"
        f"Fecha de publicación: {ficha.get('fecha_publicacion', 'N/D')}\n"
        f"Fuente oficial: {validar_url_http(ficha.get('url_oficial')) or 'N/D'}\n\n"
        "Describe brevemente el error detectado:\n"
    )
    query = urllib.parse.urlencode({"title": titulo, "body": cuerpo})
    return f"{GITHUB_ISSUES_NEW_URL}?{query}"


def navegar_a_normas_comentadas(norma_id: Optional[str] = None) -> None:
    """Navega programáticamente a Polity and Policy manteniendo sincronizado el sidebar."""
    st.query_params["vista"] = "normas_comentadas"
    if norma_id:
        st.query_params["norma"] = norma_id
    elif "norma" in st.query_params:
        del st.query_params["norma"]

    st.session_state.current_page = "Polity and Policy"
    st.session_state._last_qp_routed = f"normas_comentadas|{norma_id or ''}"
    theme_key = f"apocuna_nav_{st.session_state.get('theme_mode', '💻 Auto')}"
    st.session_state.pop(theme_key, None)
    st.session_state.pop("_last_sidebar_menu", None)
    st.rerun()


def _etiqueta_estado(estado: Optional[str]) -> tuple[str, str]:
    """Devuelve texto visible y color semántico de insignia para el estado."""
    if estado == "revisado por persona":
        return "Revisado", "#10B981"
    if estado == "borrador IA":
        return "Borrador IA", "#F59E0B"
    return "Radar sin IA", "#0284C7"


def _clase_eje(eje: Optional[str]) -> str:
    """Normaliza la clase CSS semántica según el eje Polity/Policy."""
    eje_norm = (eje or "otro").strip().lower()
    if eje_norm in {"polity", "policy", "mixto", "otro"}:
        return f"norma-eje-{eje_norm}"
    return "norma-eje-otro"


def _nombres_politicas_ficha(
    ficha: Dict[str, Any], catalogo_map: Dict[str, str]
) -> List[str]:
    """Extrae etiquetas legibles de alineación con Políticas Nacionales."""
    etiquetas: List[str] = []
    for pol in ficha.get("politica_nacional") or []:
        if not isinstance(pol, dict):
            continue
        pid = pol.get("id")
        if not pid or pid == "ninguna":
            continue
        nombre = pol.get("nombre") or catalogo_map.get(pid) or pid
        etiquetas.append(f"{nombre} ({pol.get('tipo_alineacion', 'explícita')})")
    return etiquetas


def filtrar_normas(
    fichas: List[Dict[str, Any]],
    eje: str = "Todos",
    subtema: str = "Todos",
    politica_id: str = "Todas",
    entidad: str = "Todas",
    fecha: str = "Todas",
    incluir_baja_prioridad: bool = True,
) -> List[Dict[str, Any]]:
    """Aplica filtros declarativos sobre la lista de fichas oficiales."""
    salida: List[Dict[str, Any]] = []
    for f in fichas:
        if not incluir_baja_prioridad and f.get("prioridad") == "baja prioridad":
            continue
        if eje != "Todos" and (f.get("eje") or "") != eje:
            continue
        if subtema != "Todos" and (f.get("subtema") or "") != subtema:
            continue
        if entidad != "Todas" and (f.get("entidad") or "") != entidad:
            continue
        if fecha != "Todas" and (f.get("fecha_publicacion") or "") != fecha:
            continue
        if politica_id != "Todas":
            pids = {
                p.get("id")
                for p in (f.get("politica_nacional") or [])
                if isinstance(p, dict) and p.get("id") not in (None, "ninguna")
            }
            if politica_id == "__CON_ALINEACION__":
                if not pids:
                    continue
            elif politica_id not in pids:
                continue
        salida.append(f)
    return salida


def _render_banner_ia_html(ficha: Dict[str, Any]) -> str:
    """Renderiza advertencia visible obligatoria de contenido generado con IA."""
    modelo = html.escape(str(ficha.get("modelo") or "modelo IA"), quote=True)
    fecha_ia = html.escape(str(ficha.get("fecha_ia") or ficha.get("fecha_publicacion") or ""), quote=True)
    return (
        '<div class="norma-ia-disclaimer">'
        f'<strong style="color:#D97706;">Generado con IA ({modelo} — {fecha_ia}).</strong> '
        "Puede contener errores. No es texto oficial ni asesoría legal. Verifica en la fuente oficial."
        "</div>"
    )


def _render_enlaces_ficha_html(ficha: Dict[str, Any]) -> str:
    """Construye enlaces seguros `http(s)` hacia El Peruano y reporte de errores."""
    url_oficial = validar_url_http(ficha.get("url_oficial"))
    url_reporte = validar_url_http(construir_url_reporte_error(ficha))

    partes: List[str] = []
    if url_oficial:
        href_of = html.escape(url_oficial, quote=True)
        partes.append(
            f'<a href="{href_of}" target="_blank" rel="noopener noreferrer" class="norma-btn-primary">'
            "Ver norma oficial en El Peruano ↗</a>"
        )
    if url_reporte:
        href_rep = html.escape(url_reporte, quote=True)
        partes.append(
            f'<a href="{href_rep}" target="_blank" rel="noopener noreferrer" class="norma-btn-ghost">'
            "Reportar error en esta ficha ↗</a>"
        )
    return '<div style="display:flex;flex-wrap:wrap;gap:0.55rem;margin-top:0.85rem;">' + "".join(partes) + "</div>"


def construir_tarjeta_norma_html(
    ficha: Dict[str, Any],
    catalogo_map: Optional[Dict[str, str]] = None,
) -> str:
    """Construye una tarjeta visual Snowsight para una ficha de norma oficial."""
    catalogo_map = catalogo_map or {}
    nid = str(ficha.get("id") or "")
    nid_q = urllib.parse.quote(nid, safe="")
    permalink_rel = f"?vista=normas_comentadas&norma={nid_q}"

    label_est, color_est = _etiqueta_estado(ficha.get("estado"))
    eje_cls = _clase_eje(ficha.get("eje"))
    eje_txt = html.escape(str(ficha.get("eje") or "otro").upper())
    fecha_txt = html.escape(str(ficha.get("fecha_publicacion") or "Reciente"))
    entidad_txt = html.escape(str(ficha.get("entidad") or "ENTIDAD PÚBLICA"))
    tipo_txt = html.escape(str(ficha.get("tipo") or "NORMA"))
    num_txt = html.escape(str(ficha.get("numero_raw") or ficha.get("numero") or ""))
    subtema_txt = html.escape(str(ficha.get("subtema") or "General"))
    sumilla_txt = html.escape(str(ficha.get("sumilla") or ""))

    pols = _nombres_politicas_ficha(ficha, catalogo_map)
    if pols:
        pol_chip = f'<span class="norma-signal-chip is-aligned">✓ {html.escape(pols[0])}</span>'
    else:
        pol_chip = '<span class="norma-signal-chip">Sin alineación explícita</span>'

    n_citadas = len(ficha.get("normas_citadas") or [])
    citadas_chip = f'<span class="norma-signal-chip">📑 {n_citadas} cita(s)</span>'
    prio_chip = (
        '<span class="norma-signal-chip is-low-prio">Baja prioridad</span>'
        if ficha.get("prioridad") == "baja prioridad"
        else ""
    )

    url_of = validar_url_http(ficha.get("url_oficial"))
    btn_fuente = (
        f'<a href="{html.escape(url_of, quote=True)}" target="_blank" rel="noopener noreferrer" '
        'class="norma-btn-ghost">El Peruano ↗</a>'
        if url_of
        else ""
    )

    return (
        f'<div class="norma-visual-card {eje_cls}">'
        '<div class="norma-visual-top-bar"></div>'
        '<div class="norma-card-body">'
        '<div class="norma-card-toprow">'
        '<div class="norma-badge-group">'
        f'<span class="norma-estado-pill" style="background:{color_est};">{html.escape(label_est)}</span>'
        f'<span class="norma-eje-pill">{eje_txt}</span>'
        "</div>"
        f'<span class="card-date">{fecha_txt}</span>'
        "</div>"
        f'<div class="norma-entity-eyebrow"><span class="norma-entity-dot"></span>{entidad_txt}</div>'
        f'<h4 class="norma-card-title">{tipo_txt} {num_txt}</h4>'
        f'<span class="norma-subtema-chip">{subtema_txt}</span>'
        f'<p class="norma-sumilla">{sumilla_txt}</p>'
        f'<div class="norma-signals-row">{citadas_chip}{pol_chip}{prio_chip}</div>'
        "</div>"
        '<div class="norma-visual-footer">'
        f'<a href="{html.escape(permalink_rel, quote=True)}" target="_self" class="norma-btn-primary">Analizar ficha →</a>'
        f"{btn_fuente}"
        "</div>"
        "</div>"
    )


def render_normas_showcase_strip(fichas: List[Dict[str, Any]]) -> None:
    """Renderiza una cinta ejecutiva compacta con conteos por eje y estado."""
    if not fichas:
        return
    total = len(fichas)
    n_polity = sum(1 for f in fichas if (f.get("eje") or "").lower() == "polity")
    n_policy = sum(1 for f in fichas if (f.get("eje") or "").lower() == "policy")
    n_rev = sum(1 for f in fichas if f.get("estado") == "revisado por persona")
    ultima_fecha = max((str(f.get("fecha_publicacion") or "") for f in fichas), default="N/D")

    rev_pill = (
        f'<span class="normas-showcase-pill pill-revisado">✓ Revisadas: {n_rev}</span>'
        if n_rev
        else ""
    )
    st.markdown(
        f"""
        <div class="normas-showcase-strip">
          <span class="normas-showcase-pill">⚖️ Normas seleccionadas: {total}</span>
          <span class="normas-showcase-pill pill-polity">🏛️ Polity: {n_polity}</span>
          <span class="normas-showcase-pill pill-policy">📊 Policy: {n_policy}</span>
          {rev_pill}
          <span class="normas-showcase-pill" style="margin-left:auto;">📅 Edición: {html.escape(ultima_fecha)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_normas_visual_collection(
    fichas: List[Dict[str, Any]],
    catalogo_map: Optional[Dict[str, str]] = None,
    layout: str = "grid",
) -> None:
    """Renderiza una colección de tarjetas visuales en modo `carousel` o `grid`."""
    if not fichas:
        st.info("No hay normas disponibles en esta categoría.")
        return

    clase_contenedor = (
        "normas-visual-carousel" if layout == "carousel" else "normas-visual-grid"
    )
    tarjetas_html = "".join(
        construir_tarjeta_norma_html(f, catalogo_map=catalogo_map) for f in fichas
    )
    st.markdown(
        f'<div class="{clase_contenedor}">{tarjetas_html}</div>',
        unsafe_allow_html=True,
    )


def render_ficha_detalle(ficha: Dict[str, Any], catalogo_map: Dict[str, str]) -> None:
    """Renderiza el detalle completo de una norma seleccionada por ID o permalink."""
    nid = str(ficha.get("id") or "")
    label_estado, color_estado = _etiqueta_estado(ficha.get("estado"))
    eje_cls = _clase_eje(ficha.get("eje"))

    if st.button("← Volver al listado filtrado", key=f"btn_volver_{nid}"):
        if "norma" in st.query_params:
            del st.query_params["norma"]
        st.query_params["vista"] = "normas_comentadas"
        st.rerun()

    tipo_esc = html.escape(str(ficha.get("tipo") or "Norma Legal"))
    num_esc = html.escape(str(ficha.get("numero_raw") or ficha.get("numero") or ""))
    ent_esc = html.escape(str(ficha.get("entidad") or ""))
    fecha_esc = html.escape(str(ficha.get("fecha") or ficha.get("fecha_publicacion") or ""))
    sumilla_esc = html.escape(str(ficha.get("sumilla") or ""))
    eje_esc = html.escape(str(ficha.get("eje") or "otro").upper())
    sub_esc = html.escape(str(ficha.get("subtema") or ""))
    prio_esc = html.escape(str(ficha.get("prioridad") or "normal"))

    st.markdown(
        f"""
        <div class="norma-detail-hero {eje_cls}">
          <div class="norma-visual-top-bar"></div>
          <div class="norma-detail-hero-inner">
            <div class="norma-badge-group" style="margin-bottom:0.65rem;">
              <span class="norma-estado-pill" style="background:{color_estado};">{html.escape(label_estado)}</span>
              <span class="norma-eje-pill">Eje: {eje_esc}</span>
              <span class="norma-signal-chip">Prioridad: {prio_esc}</span>
            </div>
            <div class="norma-entity-eyebrow"><span class="norma-entity-dot"></span>{ent_esc}</div>
            <h3 style="margin:0.2rem 0 0.4rem 0;color:var(--text-title);">{tipo_esc} {num_esc}</h3>
            <p style="margin:0.15rem 0;color:var(--text-muted);font-size:0.88rem;">
              <strong>Publicado:</strong> {fecha_esc} · <strong>Subtema:</strong> {sub_esc}
            </p>
            <p style="margin-top:0.75rem;color:var(--text-body);line-height:1.55;">{sumilla_esc}</p>
            {_render_enlaces_ficha_html(ficha)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    permalink = f"?vista=normas_comentadas&norma={urllib.parse.quote(nid)}"
    st.caption(f"Permalink de esta ficha: `{permalink}`")

    md_humano = load_norma_comentada_md(nid)
    if md_humano is not None:
        st.success("Versión revisada por persona (`data/normas_comentadas/`).")
        st.markdown(md_humano)
    elif ficha.get("estado") == "borrador IA":
        st.markdown(_render_banner_ia_html(ficha), unsafe_allow_html=True)
        st.markdown("**Qué dispone:**")
        st.write(ficha.get("que_dispone") or "No especificado en el texto analizado.")

        repercusiones = ficha.get("repercusiones_esperadas") or []
        if repercusiones:
            st.markdown("**Repercusiones esperadas (condicional):**")
            for rep in repercusiones:
                efecto = rep.get("efecto") or ""
                art = rep.get("articulo") or ""
                cita = rep.get("cita") or ""
                st.markdown(f"- {efecto} *({art}: «{cita}»)*")

        preguntas = ficha.get("preguntas_a_verificar") or []
        if preguntas:
            st.markdown("**Preguntas a verificar:**")
            for preg in preguntas:
                st.markdown(f"- {preg}")
    else:
        st.info(
            "Esta ficha fue indexada en modo radar sin IA; los análisis generados con IA se "
            "incorporan en la ejecución automatizada cuando `NORMAS_IA_HABILITADA = True`."
        )

    politicas = [
        p
        for p in (ficha.get("politica_nacional") or [])
        if isinstance(p, dict) and p.get("id") not in (None, "ninguna")
    ]
    with st.expander("Alineación con Políticas Nacionales y evidencia textual", expanded=bool(politicas)):
        if not politicas:
            st.write("Ninguna alineación detectada en el texto.")
        else:
            for pol in politicas:
                nombre_pol = pol.get("nombre") or catalogo_map.get(pol["id"], pol["id"])
                evid = pol.get("evidencia") or {}
                st.markdown(
                    f"- **{nombre_pol}** (`{pol.get('tipo_alineacion', 'explícita')}`)"
                    f" — *{evid.get('articulo', 'Texto')}:* «{evid.get('cita', '')}»"
                )

    citadas = ficha.get("normas_citadas") or []
    with st.expander(f"Normas citadas detectadas ({len(citadas)})", expanded=False):
        if not citadas:
            st.write("Sin normas citadas extraídas.")
        else:
            for nc in citadas:
                st.markdown(
                    f"- **{nc.get('tipo') or ''} {nc.get('numero', '')}** "
                    f"({nc.get('relacion_detectada', 'mencionada')})"
                )

    st.caption(
        f"Trazabilidad · Motivo: {ficha.get('motivo_clasificacion', 'N/D')} | "
        f"SHA-256 del texto fuente: `{(ficha.get('hash_texto') or 'no verificado')[:24]}...`"
    )


def render_normas_comentadas_subsection() -> None:
    """Renderiza el radar diario y detalle de normas comentadas dentro de Polity & Policy."""
    st.header("⚖️ Normas comentadas y Radar diario (El Peruano)")
    st.markdown(
        "Seguimiento automatizado de normas legales filtradas por criterios **Polity / Policy** "
        "y alineación con Políticas Nacionales."
    )

    estado_pipe = load_estado_pipeline()
    estado_diario = (
        estado_pipe.get("fuentes", {}).get("normas_diario", {})
        if isinstance(estado_pipe, dict)
        else {}
    )
    if estado_diario.get("ultimo_estado") == "error":
        st.warning(
            f"Último intento del radar diario con incidencia ({estado_diario.get('ultimo_intento', '')}): "
            "no se publicaron nuevas fichas fallidas; se muestran los datos validados previos."
        )

    fichas = load_normas_oficiales()
    catalogo = load_politicas_nacionales()
    catalogo_map = {p["id"]: p["nombre"] for p in catalogo if isinstance(p, dict) and p.get("id")}

    if not fichas:
        st.info(
            "Aún no hay fichas publicadas en `data/generated/normas_oficiales/`. "
            "Ejecuta el workflow `normas_diario.yml` o `python scripts/actualizar_normas_diario.py`."
        )
        return

    norma_sel_id = st.query_params.get("norma")
    if norma_sel_id:
        objetivo = next((f for f in fichas if f.get("id") == norma_sel_id), None)
        if objetivo:
            render_ficha_detalle(objetivo, catalogo_map)
            return
        st.warning(f"No se encontró la ficha solicitada (`{norma_sel_id}`). Mostrando listado completo.")

    render_normas_showcase_strip(fichas)

    ejes_disp = ["Todos"] + sorted({str(f.get("eje")) for f in fichas if f.get("eje")})
    subs_disp = ["Todos"] + sorted({str(f.get("subtema")) for f in fichas if f.get("subtema")})
    ents_disp = ["Todas"] + sorted({str(f.get("entidad")) for f in fichas if f.get("entidad")})
    fechas_disp = ["Todas"] + sorted(
        {str(f.get("fecha_publicacion")) for f in fichas if f.get("fecha_publicacion")},
        reverse=True,
    )

    pids_presentes = sorted(
        {
            p.get("id")
            for f in fichas
            for p in (f.get("politica_nacional") or [])
            if isinstance(p, dict) and p.get("id") not in (None, "ninguna")
        }
    )
    pol_opciones = ["Todas", "__CON_ALINEACION__"] + pids_presentes

    def _fmt_pol(op_val: str) -> str:
        if op_val == "Todas":
            return "Todas las políticas"
        if op_val == "__CON_ALINEACION__":
            return "Solo con alineación detectada"
        return catalogo_map.get(op_val, op_val)

    c1, c2, c3 = st.columns(3)
    with c1:
        f_fecha = st.selectbox("Fecha de publicación", fechas_disp, key="normas_f_fecha")
        f_eje = st.selectbox("Eje (Polity / Policy)", ejes_disp, key="normas_f_eje")
    with c2:
        f_sub = st.selectbox("Subtema", subs_disp, key="normas_f_subtema")
        f_ent = st.selectbox("Entidad", ents_disp, key="normas_f_entidad")
    with c3:
        f_pol = st.selectbox(
            "Política Nacional",
            pol_opciones,
            format_func=_fmt_pol,
            key="normas_f_politica",
        )
        incluir_baja = st.checkbox(
            "Incluir transferencias de baja prioridad",
            value=True,
            key="normas_f_baja_prio",
        )

    filtradas = filtrar_normas(
        fichas,
        eje=f_eje,
        subtema=f_sub,
        politica_id=f_pol,
        entidad=f_ent,
        fecha=f_fecha,
        incluir_baja_prioridad=incluir_baja,
    )

    st.caption(f"Mostrando **{len(filtradas)}** de {len(fichas)} fichas publicadas.")
    render_normas_visual_collection(filtradas, catalogo_map=catalogo_map, layout="grid")
