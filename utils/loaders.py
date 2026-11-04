import os
import glob
import json
import markdown
import requests
import streamlit as st

try:
    from config import CKAN_MINSA_HABILITADO, CKAN_PCM_HABILITADO
except ImportError:
    CKAN_MINSA_HABILITADO = False
    CKAN_PCM_HABILITADO = False

USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"


@st.cache_resource
def get_http_headers() -> dict:
    """Proporciona cabeceras HTTP reutilizables en memoria."""
    return {"User-Agent": USER_AGENT}


def _read_local_json( *path_parts, default=None, warn_on_error=False):
    """Lee un archivo JSON local de forma segura con manejo uniforme de errores."""
    if default is None:
        default = []
    path = os.path.join(*path_parts)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        if warn_on_error:
            st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return default


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extrae metadatos YAML simples y cuerpo Markdown con baja complejidad ciclomática."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    meta = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, parts[2].strip()


def _extract_excerpt(body: str, max_len: int = 210) -> str:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    excerpt = " ".join(lines)[:max_len]
    return excerpt.rsplit(" ", 1)[0] + "…" if len(excerpt) == max_len else excerpt


def _build_nota_entry(filepath: str) -> dict | None:
    """Construye el diccionario enriquecido de una nota incluyendo tiempo de lectura precalculado."""
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
        meta, body = _parse_frontmatter(raw)
        base_title = os.path.splitext(filename)[0]
        words = len(body.split())

        return {
            "id": filename,
            "meta": {
                "titulo": meta.get("titulo") or base_title,
                "fecha": meta.get("fecha") or "2026-10-01",
                "imagen": meta.get("imagen", ""),
                "tipo": meta.get("tipo") or "NOTA DE INVESTIGACIÓN",
                "autor": meta.get("autor") or "Apocuna Hub",
                "lectura_min": max(1, round(words / 200)),
                "palabras": words,
                "extracto": _extract_excerpt(body),
            },
            "body": body,
        }
    except Exception as e:
        st.warning(f"Aviso: No se pudo leer nota {filename} ({e})")
        return None


@st.cache_data(show_spinner=False)
def load_fuentes():
    """Carga el catálogo de fuentes estructuradas."""
    return _read_local_json("data", "fuentes.json", warn_on_error=True)


@st.cache_data(show_spinner=False)
def load_eventos():
    """Carga las revistas y congresos."""
    return _read_local_json("data", "eventos.json", warn_on_error=True)


@st.cache_data(show_spinner=False)
def load_notas():
    """Carga y parsea las notas de investigación con frontmatter usando patrón *.md."""
    notas_dir = os.path.join("data", "notas")
    if not os.path.exists(notas_dir):
        return []
    md_files = sorted(glob.glob(os.path.join(notas_dir, "*.md")))
    notas = [_build_nota_entry(fp) for fp in md_files]
    return [n for n in notas if n is not None]


def _resolve_data_base_url() -> str | None:
    """Obtiene DATA_BASE_URL desde st.secrets o variables de entorno sin lanzar excepciones."""
    try:
        url = st.secrets.get("DATA_BASE_URL")
        if url:
            return url
    except Exception:
        pass
    return os.getenv("DATA_BASE_URL")


def load_remote_or_local_json(filename: str):
    """Intenta cargar JSON desde DATA_BASE_URL y recurre al archivo local como fallback inmediato."""
    data_base_url = _resolve_data_base_url()
    if data_base_url:
        url = f"{data_base_url.rstrip('/')}/{filename}"
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            st.warning(f"Aviso: No se pudo cargar remotamente {url} ({e})")

    return _read_local_json("data", "generated", filename, warn_on_error=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_noticias():
    """Carga el catálogo de noticias generadas y pre-ordenadas por fecha."""
    noticias = load_remote_or_local_json("noticias.json")
    return sorted(noticias, key=lambda x: x.get("fecha_iso", ""), reverse=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_noticias_grouped() -> dict:
    """Agrupa y cachea las noticias por categoría para renderizado instantáneo O(1) en Home."""
    noticias = load_noticias()
    return {
        "todas": noticias,
        "gestion": [n for n in noticias if n.get("categoria") == "gestion"],
        "politicas_publicas": [n for n in noticias if n.get("categoria") == "politicas_publicas"],
        "politica": [n for n in noticias if n.get("categoria") == "politica"],
    }


@st.cache_data(ttl=900, show_spinner=False)
def load_academico():
    """Carga alertas académicas (RSS/OpenAlex)."""
    return load_remote_or_local_json("academico.json")


@st.cache_data(ttl=900, show_spinner=False)
def load_polity_alertas():
    """Carga alertas de polity and policy."""
    return load_remote_or_local_json("polity_alertas.json")


@st.cache_data(ttl=900, show_spinner=False)
def load_eventos_alertas():
    """Carga alertas de eventos y convocatorias."""
    return load_remote_or_local_json("eventos_alertas.json")


@st.cache_data(ttl=900, show_spinner=False)
def load_normas():
    """Carga el catálogo de normas generadas."""
    return load_remote_or_local_json("normas.json")


@st.cache_data(ttl=900, show_spinner=False)
def load_ckan_fallback():
    """Carga el dataset fallback de portales CKAN."""
    return load_remote_or_local_json("ckan.json")


def _is_portal_enabled(portal: str) -> bool:
    if portal == "MINSA":
        return bool(CKAN_MINSA_HABILITADO)
    if portal == "PCM":
        return bool(CKAN_PCM_HABILITADO)
    return True


def _fetch_single_ckan_portal(portal: str, url: str) -> list:
    """Consulta un endpoint CKAN individual y transforma sus paquetes al esquema de tarjeta."""
    try:
        resp = requests.get(url, timeout=3.5, headers=get_http_headers())
        if resp.status_code != 200:
            return []
        results = resp.json().get("result", {}).get("results", [])
        base_host = "https://www.datosabiertos.gob.pe" if portal == "PCM" else "https://datos.minsa.gob.pe"
        return [
            {
                "id": pkg.get("id", ""),
                "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                "portal": portal,
                "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                "url": pkg.get("url") or f"{base_host}/dataset/{pkg.get('name')}",
                "demo": False,
            }
            for pkg in results[:5]
        ]
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ckan_datasets():
    """
    Consulta en vivo los endpoints CKAN habilitados con timeout corto.
    Si están deshabilitados o sin respuesta, recurre inmediatamente al fallback en caché.
    """
    datasets = []
    for f in load_fuentes():
        url = f.get("url", "")
        if f.get("tipo") == "api" and "action/package_search" in url:
            portal = "PCM" if "datosabiertos.gob.pe" in url else "MINSA"
            if _is_portal_enabled(portal):
                datasets.extend(_fetch_single_ckan_portal(portal, url))

    return datasets if datasets else load_ckan_fallback()


@st.cache_data(show_spinner=False)
def load_polity():
    """Carga las 4 subsecciones de Polity and Policy."""
    return _read_local_json("data", "polity.json", warn_on_error=True)


@st.cache_data(show_spinner=False)
def load_estudiantes():
    """Carga las 5 subsecciones de Estudiantes y apuntes de sistemas administrativos."""
    return _read_local_json("data", "estudiantes.json", warn_on_error=True)


@st.cache_data(show_spinner=False)
def load_cursos():
    """Carga el catálogo de cursos."""
    return _read_local_json("data", "cursos.json")


@st.cache_data(show_spinner=False)
def load_becas():
    """Carga las becas y oportunidades."""
    return _read_local_json("data", "becas.json")


@st.cache_data(show_spinner=False)
def load_sobre_el_sitio_html() -> str:
    """Lee y compila a HTML data/sobre_el_sitio.md una única vez en caché."""
    md_path = os.path.join("data", "sobre_el_sitio.md")
    if not os.path.exists(md_path):
        return ""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return markdown.markdown(f.read())
    except Exception:
        return ""


@st.cache_data(ttl=600, show_spinner=False)
def load_estado_pipeline() -> dict:
    """Carga el estado operativo del último pipeline automatizado."""
    return _read_local_json("data", "generated", "estado.json", default={})


@st.cache_data(ttl=600, show_spinner=False)
def load_dashboard_kpis() -> dict:
    """Calcula y cachea las métricas ejecutivas globales para navegación instantánea."""
    noticias = load_noticias()
    normas = load_normas()
    fuentes = load_fuentes()
    cursos = load_cursos()
    becas = load_becas()
    eventos = load_eventos()
    academico = load_academico()
    estado = load_estado_pipeline()

    last_run_raw = estado.get("last_run", "")
    last_run_short = last_run_raw[:16].replace("T", " ") + " UTC" if last_run_raw else "Activo"

    return {
        "noticias_total": len(noticias),
        "normas_total": len(normas),
        "fuentes_total": len(fuentes),
        "cursos_total": len(cursos),
        "becas_total": len(becas),
        "eventos_total": len(eventos),
        "academico_total": len(academico),
        "oportunidades_total": len(cursos) + len(becas) + len(eventos),
        "last_sync": last_run_short,
    }
