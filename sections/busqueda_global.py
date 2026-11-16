"""Buscador global unificado de Apocuna Hub (consulta datos curados y feeds actualizados en vivo)."""

import html
import unicodedata
import urllib.parse
from typing import Any

import streamlit as st

from utils.loaders import (
    load_academico,
    load_becas,
    load_cursos,
    load_estudiantes,
    load_evaluaciones_politicas,
    load_eventos,
    load_eventos_alertas,
    load_fichas_tecnicas,
    load_fuentes,
    load_normas,
    load_normas_oficiales,
    load_notas,
    load_noticias,
    load_polity,
    load_polity_alertas,
    load_revistas_gestion,
    resolve_ficha_id,
)


def _normalize_text(val: Any) -> str:
    """Normaliza texto a minúsculas sin tildes para búsqueda tolerante."""
    if not val:
        return ""
    raw = str(val)
    nfkd = unicodedata.normalize("NFKD", raw)
    no_accents = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return no_accents.lower().strip()


def _safe_http_url(url: Any) -> str | None:
    if not isinstance(url, str):
        return None
    limpia = url.strip()
    if limpia.startswith(("https://", "http://")):
        return limpia
    return None


def _matches_tokens(tokens: list[str], *fields: Any) -> bool:
    blob = _normalize_text(" ".join(str(f or "") for f in fields))
    return all(tok in blob for tok in tokens)


def buscar_en_todo_el_sitio(query: str) -> list[dict]:
    """Busca en todas las fuentes actualizadas automáticamente y catálogos curados del sitio."""
    tokens = [t for t in _normalize_text(query).split() if t]
    if not tokens:
        return []

    resultados: list[dict] = []

    # 1. Normas Oficiales de El Peruano (actualizadas diariamente en data/generated/normas_oficiales/)
    for f in load_normas_oficiales():
        titulo_norma = f"{f.get('tipo', '')} {f.get('numero_raw') or f.get('numero') or ''}".strip()
        sumilla = f.get("sumilla") or ""
        entidad = f.get("entidad") or ""
        subtema = f.get("subtema") or ""
        que_dispone = f.get("que_dispone") or ""
        if _matches_tokens(tokens, titulo_norma, sumilla, entidad, subtema, que_dispone, f.get("eje")):
            nid = str(f.get("id") or "")
            resultados.append({
                "grupo": "Normas Legales",
                "tipo_badge": "NORMA LEGAL",
                "estado_badge": str(f.get("fecha_publicacion") or "Reciente"),
                "institucion": entidad or "El Peruano",
                "titulo": titulo_norma or "Norma Oficial",
                "descripcion": sumilla or que_dispone,
                "url_externa": f.get("url_oficial"),
                "label_externa": "El Peruano ↗",
                "url_interna": f"?vista=normas_comentadas&norma={urllib.parse.quote(nid, safe='')}" if nid else None,
                "label_interna": "Analizar ficha →",
                "fecha_sort": str(f.get("fecha_publicacion") or ""),
            })

    # 2. Radar regulatorio general (data/generated/normas.json)
    for n in load_normas():
        if _matches_tokens(tokens, n.get("titulo"), n.get("entidad"), n.get("tipo_norma"), n.get("grupo")):
            resultados.append({
                "grupo": "Normas Legales",
                "tipo_badge": str(n.get("tipo_norma") or "NORMA").upper(),
                "estado_badge": str(n.get("fecha_iso") or "")[:10] or "Reciente",
                "institucion": n.get("entidad") or "Normativa",
                "titulo": n.get("titulo") or "",
                "descripcion": f"Seguimiento regulatorio ({n.get('grupo', 'General')}).",
                "url_externa": n.get("url"),
                "label_externa": "Consultar ↗",
                "fecha_sort": str(n.get("fecha_iso") or "")[:10],
            })

    # 3. Noticias y Alertas Automatizadas (noticias.json, polity_alertas.json, eventos_alertas.json, academico.json)
    feeds = [
        (load_noticias(), "Noticias y Alertas", "NOTICIA", "resumen"),
        (load_polity_alertas(), "Noticias y Alertas", "ALERTA POLITY", None),
        (load_eventos_alertas(), "Noticias y Alertas", "CONVOCATORIA", None),
        (load_academico(), "Noticias y Alertas", "PAPER / OPENALEX", "autores"),
    ]
    for lista, grupo, badge, desc_key in feeds:
        for item in lista:
            extra = item.get(desc_key, "") if desc_key else ""
            if _matches_tokens(tokens, item.get("titulo"), item.get("fuente"), extra, item.get("categoria")):
                resultados.append({
                    "grupo": grupo,
                    "tipo_badge": badge,
                    "estado_badge": str(item.get("fecha_iso") or "")[:10] or "Reciente",
                    "institucion": item.get("fuente") or "Radar Automatizado",
                    "titulo": item.get("titulo") or "",
                    "descripcion": extra or "Reporte capturado por el radar automatizado de Apocuna.",
                    "url_externa": item.get("url"),
                    "label_externa": "Leer fuente ↗",
                    "fecha_sort": str(item.get("fecha_iso") or "")[:10],
                })

    # 4. Fichas Técnicas Metodológicas y Catálogo Polity & Fuentes
    seen_ficha_ids: set[str] = set()
    for ft in load_fichas_tecnicas():
        modulos = " ".join((ft.get("contenido_variables") or {}).get("modulos_principales") or [])
        usos = " ".join(ft.get("usos_aplicaciones") or [])
        llaves = (ft.get("alcance_cobertura") or {}).get("llaves_cruce") or ""
        if _matches_tokens(tokens, ft.get("nombre"), ft.get("institucion"), ft.get("resumen_ejecutivo"), modulos, usos, llaves):
            fid = str(ft.get("id") or "")
            seen_ficha_ids.add(fid)
            vista = "fen" if fid.startswith(("senamhi_", "windy_", "enfen_", "noaa_", "dhn_", "copernicus_", "sunass_", "ana_", "cenepred_", "indeci_", "igp_", "anin_")) else "polity"
            resultados.append({
                "grupo": "Fuentes y Fichas Técnicas",
                "tipo_badge": "FICHA TÉCNICA",
                "estado_badge": str(ft.get("frecuencia") or "Vigente").upper(),
                "institucion": ft.get("institucion") or "",
                "titulo": ft.get("nombre") or "",
                "descripcion": ft.get("resumen_ejecutivo") or "",
                "url_externa": ft.get("url_oficial"),
                "label_externa": "Portal oficial ↗",
                "url_interna": f"?vista={vista}&ficha={urllib.parse.quote(fid, safe='')}",
                "label_interna": "📄 Ficha técnica →",
                "fecha_sort": "",
            })

    for sub in load_polity():
        for t in sub.get("tarjetas", []):
            if _matches_tokens(tokens, t.get("titulo"), t.get("descripcion"), t.get("fuente"), sub.get("subseccion")):
                fid = resolve_ficha_id(t)
                if fid and fid in seen_ficha_ids:
                    continue
                resultados.append({
                    "grupo": "Fuentes y Fichas Técnicas",
                    "tipo_badge": "INSUMO POLITY",
                    "estado_badge": str(t.get("frecuencia") or "Permanente").upper(),
                    "institucion": t.get("fuente") or "",
                    "titulo": t.get("titulo") or "",
                    "descripcion": t.get("descripcion") or "",
                    "url_externa": t.get("url"),
                    "label_externa": "Abrir recurso ↗",
                    "url_interna": f"?vista=polity&ficha={urllib.parse.quote(fid, safe='')}" if fid else None,
                    "label_interna": "📄 Ficha técnica →",
                    "fecha_sort": "",
                })

    for f in load_fuentes():
        if _matches_tokens(tokens, f.get("nombre"), f.get("institucion"), f.get("descripcion_corta"), f.get("bloque")):
            fid = resolve_ficha_id(f)
            if fid and fid in seen_ficha_ids:
                continue
            resultados.append({
                "grupo": "Fuentes y Fichas Técnicas",
                "tipo_badge": str(f.get("tipo") or "FUENTE").upper(),
                "estado_badge": "✓ AUDITADA",
                "institucion": f.get("institucion") or "",
                "titulo": f.get("nombre") or "",
                "descripcion": f.get("descripcion_corta") or "",
                "url_externa": f.get("url"),
                "label_externa": "Explorar fuente ↗",
                "url_interna": f"?vista=polity&ficha={urllib.parse.quote(fid, safe='')}" if fid else None,
                "label_interna": "📄 Ficha técnica →",
                "fecha_sort": "",
            })

    # 5. Fenómeno El Niño (FEN) — Herramientas y radar en vivo
    try:
        from sections.fen import FEN_IMPACT_CARDS, MASTER_FEN_TOOLS
        for tool in MASTER_FEN_TOOLS:
            if _matches_tokens(tokens, tool.get("nombre"), tool.get("institucion"), tool.get("categoria"), tool.get("utilidad")):
                fid = resolve_ficha_id(tool)
                resultados.append({
                    "grupo": "FEN / Clima",
                    "tipo_badge": str(tool.get("categoria") or "FEN").upper(),
                    "estado_badge": str(tool.get("frecuencia") or "Tiempo real").upper(),
                    "institucion": tool.get("institucion") or "",
                    "titulo": tool.get("nombre") or "",
                    "descripcion": tool.get("utilidad") or "",
                    "url_externa": tool.get("url"),
                    "label_externa": "Abrir herramienta ↗",
                    "url_interna": f"?vista=fen&ficha={urllib.parse.quote(fid, safe='')}" if fid else None,
                    "label_interna": "📄 Ficha técnica →",
                    "fecha_sort": "",
                })
        for imp in FEN_IMPACT_CARDS:
            if _matches_tokens(tokens, imp.get("titulo"), imp.get("institucion"), imp.get("descripcion"), imp.get("eje")):
                fid = resolve_ficha_id(imp)
                resultados.append({
                    "grupo": "FEN / Clima",
                    "tipo_badge": "IMPACTO FEN",
                    "estado_badge": "DATOS ABIERTOS",
                    "institucion": imp.get("institucion") or "",
                    "titulo": imp.get("titulo") or "",
                    "descripcion": imp.get("descripcion") or "",
                    "url_externa": imp.get("url"),
                    "label_externa": "Consultar plataforma ↗",
                    "url_interna": f"?vista=fen&ficha={urllib.parse.quote(fid, safe='')}" if fid else None,
                    "label_interna": "📄 Ficha técnica →",
                    "fecha_sort": "",
                })
    except Exception:
        pass

    # 6. Estudiantes, Cursos, Becas, Eventos y Notas
    for c in load_cursos():
        if _matches_tokens(tokens, c.get("nombre"), c.get("proveedor"), c.get("tema"), c.get("descripcion_corta")):
            resultados.append({
                "grupo": "Estudiantes y Eventos",
                "tipo_badge": str(c.get("modalidad") or "CURSO").upper(),
                "estado_badge": str(c.get("costo") or "ABIERTO").upper(),
                "institucion": c.get("proveedor") or "",
                "titulo": c.get("nombre") or "",
                "descripcion": c.get("descripcion_corta") or c.get("tema") or "",
                "url_externa": c.get("url"),
                "label_externa": "Ir al curso ↗",
                "fecha_sort": "",
            })

    for b in load_becas():
        if _matches_tokens(tokens, b.get("nombre"), b.get("institucion"), b.get("tipo")):
            resultados.append({
                "grupo": "Estudiantes y Eventos",
                "tipo_badge": str(b.get("tipo") or "BECA").upper(),
                "estado_badge": "PORTAL OFICIAL",
                "institucion": b.get("institucion") or "",
                "titulo": b.get("nombre") or "",
                "descripcion": "Convocatorias y oportunidades de financiamiento académico.",
                "url_externa": b.get("url"),
                "label_externa": "Portal de becas ↗",
                "fecha_sort": "",
            })

    for sub in load_estudiantes():
        for ap in sub.get("apuntes", []):
            if _matches_tokens(tokens, ap.get("titulo"), ap.get("sistema"), ap.get("curso"), ap.get("resumen"), ap.get("normativa")):
                resultados.append({
                    "grupo": "Estudiantes y Eventos",
                    "tipo_badge": "SISTEMA ADM.",
                    "estado_badge": str(ap.get("normativa") or "LOPE"),
                    "institucion": f"{ap.get('sistema', '')} • {ap.get('curso', '')}",
                    "titulo": ap.get("titulo") or "",
                    "descripcion": ap.get("resumen") or "",
                    "url_externa": ap.get("url"),
                    "label_externa": "Marco Normativo ↗",
                    "fecha_sort": "",
                })

    for ev in load_eventos():
        if _matches_tokens(tokens, ev.get("titulo"), ev.get("tematica"), ev.get("descripcion"), ev.get("tipo")):
            resultados.append({
                "grupo": "Estudiantes y Eventos",
                "tipo_badge": str(ev.get("tipo") or "EVENTO").upper(),
                "estado_badge": str(ev.get("fecha_limite") or "Vigente"),
                "institucion": ev.get("tematica") or "",
                "titulo": ev.get("titulo") or "",
                "descripcion": ev.get("descripcion") or "",
                "url_externa": ev.get("enlace"),
                "label_externa": "Sitio oficial ↗",
                "fecha_sort": "",
            })

    # 8. CEPLAN Políticas Nacionales + Evaluaciones de Programas Públicos
    ceplan_desc = (
        "Base de datos consolidada del CEPLAN (51 Políticas Nacionales aprobadas y 38 en proceso, "
        "Decretos Supremos, ministerios rectores, estado SINAPLAN y enlaces PDF)."
    )
    if _matches_tokens(tokens, "Base de Datos Políticas Nacionales CEPLAN SINAPLAN", ceplan_desc, "ministerios sectores decreto supremo"):
        resultados.append({
            "grupo": "Polity & Policy / Fuentes",
            "tipo_badge": "BASE DE DATOS",
            "estado_badge": "OFICIAL CEPLAN",
            "institucion": "CEPLAN — SINAPLAN",
            "titulo": "Base de Datos: Políticas Nacionales de los Sectores (51 aprobadas / 38 en proceso)",
            "descripcion": ceplan_desc,
            "url_externa": "https://www.gob.pe/institucion/ceplan/informes-publicaciones/7665898-base-de-datos-politicas-nacionales-de-los-sectores",
            "label_externa": "Publicación CEPLAN ↗",
            "fecha_sort": "2026-10-15",
        })

    for ev in load_evaluaciones_politicas():
        if _matches_tokens(
            tokens,
            ev.get("titulo"),
            ev.get("programa_o_ambito"),
            ev.get("politica_publica"),
            ev.get("tipo_evaluacion"),
            ev.get("entidad_evaluadora"),
            ev.get("hallazgo_clave"),
        ):
            is_soc = ev.get("nivel_prioridad") == "programa_social"
            resultados.append({
                "grupo": "Evaluaciones y Literatura Pública",
                "tipo_badge": "PROGRAMA SOCIAL" if is_soc else "POLÍTICA PÚBLICA",
                "estado_badge": f"{ev.get('tipo_evaluacion', 'EVALUACIÓN').upper()} • {ev.get('anio', '')}".strip(" •"),
                "institucion": f"{ev.get('programa_o_ambito', '')} ({ev.get('entidad_evaluadora', '')})",
                "titulo": ev.get("titulo") or "",
                "descripcion": ev.get("hallazgo_clave") or "",
                "url_externa": ev.get("url"),
                "label_externa": "Ver evaluación ↗",
                "fecha_sort": str(ev.get("anio") or ""),
            })

    # 9. Revistas, Memorias de Congresos y Papers de Gestión Pública
    rev_data = load_revistas_gestion()
    for rev in rev_data.get("revistas", []):
        if _matches_tokens(tokens, rev.get("titulo"), rev.get("institucion"), rev.get("pais_alcance"), rev.get("descripcion")):
            resultados.append({
                "grupo": "Evaluaciones y Literatura Pública",
                "tipo_badge": str(rev.get("tipo") or "REVISTA").upper(),
                "estado_badge": str(rev.get("frecuencia") or "Abierto").upper(),
                "institucion": f"{rev.get('institucion', '')} • {rev.get('pais_alcance', '')}",
                "titulo": rev.get("titulo") or "",
                "descripcion": rev.get("descripcion") or "",
                "url_externa": rev.get("url"),
                "label_externa": "Ir a la revista ↗",
                "fecha_sort": "",
            })
    for mem in rev_data.get("memorias_congresos", []):
        if _matches_tokens(tokens, mem.get("titulo"), mem.get("institucion"), mem.get("alcance"), mem.get("descripcion")):
            resultados.append({
                "grupo": "Evaluaciones y Literatura Pública",
                "tipo_badge": str(mem.get("tipo") or "MEMORIA CONGRESO").upper(),
                "estado_badge": str(mem.get("alcance") or "IBEROAMÉRICA").upper(),
                "institucion": mem.get("institucion") or "",
                "titulo": mem.get("titulo") or "",
                "descripcion": mem.get("descripcion") or "",
                "url_externa": mem.get("url"),
                "label_externa": "Consultar memorias ↗",
                "fecha_sort": "",
            })
    for pap in rev_data.get("papers_ensayos", []):
        if _matches_tokens(tokens, pap.get("titulo"), pap.get("revista"), pap.get("ambito"), pap.get("resumen")):
            resultados.append({
                "grupo": "Evaluaciones y Literatura Pública",
                "tipo_badge": str(pap.get("tipo") or "PAPER").upper(),
                "estado_badge": str(pap.get("ambito") or pap.get("anio") or "").upper(),
                "institucion": pap.get("revista") or "",
                "titulo": pap.get("titulo") or "",
                "descripcion": pap.get("resumen") or "",
                "url_externa": pap.get("url"),
                "label_externa": "Leer artículo ↗",
                "fecha_sort": str(pap.get("anio") or ""),
            })

    for nota in load_notas():
        meta = nota.get("meta") or {}
        if _matches_tokens(tokens, meta.get("titulo"), meta.get("autor"), meta.get("extracto"), nota.get("body")):
            resultados.append({
                "grupo": "Notas y Ensayos",
                "tipo_badge": str(meta.get("tipo") or "NOTA").upper(),
                "estado_badge": str(meta.get("fecha") or "Publicada"),
                "institucion": meta.get("autor") or "Apocuna Hub",
                "titulo": meta.get("titulo") or "",
                "descripcion": meta.get("extracto") or "",
                "nota_id": nota.get("id"),
                "fecha_sort": str(meta.get("fecha") or ""),
            })

    return resultados


def _clear_global_search() -> None:
    st.session_state["global_search_query"] = ""


def render_busqueda_global(query: str) -> None:
    """Renderiza los resultados del buscador general integrando todas las fuentes del sitio."""
    q_clean = query.strip()
    col_head, col_clear = st.columns([4, 1])
    with col_head:
        st.title(f'🔎 Buscador General: "{q_clean}"')
    with col_clear:
        st.write("")
        st.button("✕ Limpiar búsqueda", key="btn_clear_global_search", on_click=_clear_global_search, use_container_width=True)

    if len(q_clean) < 2:
        st.info("Escribe al menos **2 caracteres** en la barra de búsqueda superior para consultar todo Apocuna.")
        return

    resultados = buscar_en_todo_el_sitio(q_clean)
    if not resultados:
        st.warning(f'No se encontraron coincidencias para **"{q_clean}"** en los catálogos ni en las actualizaciones recientes.')
        return

    grupos_disponibles = ["Todas"] + sorted({r["grupo"] for r in resultados})
    col_info, col_filtro = st.columns([2.2, 1.3])
    with col_info:
        st.caption(
            f"Se encontraron **{len(resultados)}** coincidencias en normas, noticias actualizadas, "
            f"fichas técnicas, fuentes, monitoreo FEN y recursos formativos."
        )
    with col_filtro:
        grupo_sel = st.selectbox("Filtrar resultados por bloque:", grupos_disponibles, key="global_search_group_filter")

    filtrados = resultados if grupo_sel == "Todas" else [r for r in resultados if r["grupo"] == grupo_sel]

    cards_html: list[str] = []
    for idx, item in enumerate(filtrados[:60]):
        tipo_b = html.escape(str(item.get("tipo_badge") or "RECURSO"))
        est_b = html.escape(str(item.get("estado_badge") or ""))
        inst = html.escape(str(item.get("institucion") or ""))
        tit = html.escape(str(item.get("titulo") or ""))
        desc = html.escape(str(item.get("descripcion") or "")[:240])
        grupo_tag = html.escape(str(item.get("grupo") or ""))

        acciones = []
        url_ext = _safe_http_url(item.get("url_externa"))
        if url_ext:
            lbl_ext = html.escape(str(item.get("label_externa") or "Abrir ↗"))
            acciones.append(
                f'<a href="{html.escape(url_ext, quote=True)}" target="_blank" rel="noopener noreferrer" '
                f'class="btn-open">{lbl_ext}</a>'
            )
        url_int = item.get("url_interna")
        if url_int:
            lbl_int = html.escape(str(item.get("label_interna") or "Ver ficha →"))
            acciones.append(
                f'<a href="{html.escape(url_int, quote=True)}" target="_self" '
                f'class="btn-ficha-tecnica">{lbl_int}</a>'
            )

        cards_html.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta"><span class="badge-tipo">{tipo_b}</span><span class="badge-freq badge-freq-permanente">{est_b}</span></div>'
            f'<div class="inst">{grupo_tag} • {inst}</div>'
            f'<h4>{tit}</h4>'
            f'<p>{desc}</p>'
            f'</div>'
            f'<div class="card-actions-row">{"".join(acciones)}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

    # Botones nativos para abrir Notas internas si hay resultados de tipo Nota
    notas_hit = [r for r in filtrados if r.get("nota_id")]
    if notas_hit:
        st.markdown("---")
        st.subheader("📝 Abrir ensayos y notas encontradas")
        for idx, n_item in enumerate(notas_hit[:10]):
            if st.button(f"📖 Leer nota: {n_item['titulo']}", key=f"btn_open_nota_search_{idx}"):
                st.session_state["selected_note_id"] = n_item["nota_id"]
                st.session_state["global_search_query"] = ""
                st.session_state["current_page"] = "Notas"
                st.rerun()

    if len(filtrados) > 60:
        st.caption(f"Mostrando los primeros **60** de **{len(filtrados)}** resultados. Refina tu búsqueda con más palabras clave.")
