import os
import glob
import json
import html
import requests
import streamlit as st

try:
    from config import CKAN_MINSA_HABILITADO, CKAN_PCM_HABILITADO
except ImportError:
    CKAN_MINSA_HABILITADO = False
    CKAN_PCM_HABILITADO = False

@st.cache_data
def load_fuentes():
    """Carga el catálogo de fuentes estructuradas."""
    try:
        with open(os.path.join("data", "fuentes.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar data/fuentes.json ({e})")
        return []

@st.cache_data
def load_eventos():
    """Carga las revistas y congresos."""
    try:
        with open(os.path.join("data", "eventos.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar data/eventos.json ({e})")
        return []

@st.cache_data
def load_notas():
    """Carga y parsea las notas de investigación con frontmatter usando patrón *.md."""
    notas = []
    notas_dir = os.path.join("data", "notas")
    if not os.path.exists(notas_dir):
        return notas
        
    md_files = glob.glob(os.path.join(notas_dir, "*.md"))
    for filepath in sorted(md_files):
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                meta = {}
                body = content
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        body = parts[2].strip()
                        for line in frontmatter.strip().split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                meta[k.strip()] = v.strip().strip('"').strip("'")
                
                # Valores por defecto si el frontmatter está incompleto
                base_title = os.path.splitext(filename)[0]
                meta_completa = {
                    "titulo": meta.get("titulo") or base_title,
                    "fecha": meta.get("fecha") or "2026-10-01",
                    "imagen": meta.get("imagen", ""),
                    "tipo": meta.get("tipo") or "NOTA DE INVESTIGACIÓN",
                    "autor": meta.get("autor") or "Apocuna Hub"
                }
                
                notas.append({
                    "id": filename,
                    "meta": meta_completa,
                    "body": body
                })
        except Exception as e:
            st.warning(f"Aviso: No se pudo leer nota {filename} ({e})")
    return notas

def load_remote_or_local_json(filename):
    data_base_url = None
    try:
        data_base_url = st.secrets.get("DATA_BASE_URL")
    except Exception:
        data_base_url = None
        
    if not data_base_url:
        data_base_url = os.getenv("DATA_BASE_URL")
        
    if data_base_url:
        url = f"{data_base_url.rstrip('/')}/{filename}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            st.warning(f"Aviso: No se pudo cargar remotamente {url} ({e})")
            
    # Fallback to local
    path = os.path.join("data", "generated", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar localmente {path} ({e})")
        return []

@st.cache_data(ttl=900)
def load_noticias():
    """Carga el catálogo de noticias de ejemplo o generadas."""
    return load_remote_or_local_json("noticias.json")

@st.cache_data(ttl=900)
def load_academico():
    """Carga alertas académicas (RSS/OpenAlex)."""
    return load_remote_or_local_json("academico.json")

@st.cache_data(ttl=900)
def load_polity_alertas():
    """Carga alertas de polity and policy."""
    return load_remote_or_local_json("polity_alertas.json")

@st.cache_data(ttl=900)
def load_eventos_alertas():
    """Carga alertas de eventos y convocatorias."""
    return load_remote_or_local_json("eventos_alertas.json")

@st.cache_data(ttl=900)
def load_normas():
    """Carga el catálogo de normas de ejemplo o generadas."""
    return load_remote_or_local_json("normas.json")

@st.cache_data(ttl=900)
def load_ckan_fallback():
    """Carga el dataset fallback de portales CKAN."""
    return load_remote_or_local_json("ckan.json")

@st.cache_data(ttl=300)
def fetch_ckan_datasets():
    """
    Consulta en vivo los endpoints CKAN de fuentes.json con timeout y try/except.
    Si la red falla o se agota el tiempo, recurre a data/generated/ckan.json.
    """
    fuentes = load_fuentes()
    datasets = []
    
    # Buscar endpoints CKAN en fuentes
    endpoints = []
    for f in fuentes:
        if f.get("tipo") == "api" and "action/package_search" in f.get("url", ""):
            portal = "PCM" if "datosabiertos.gob.pe" in f.get("url", "") else "MINSA"
            if portal == "MINSA" and not CKAN_MINSA_HABILITADO:
                continue
            if portal == "PCM" and not CKAN_PCM_HABILITADO:
                continue
            endpoints.append((portal, f.get("url")))
            
    for portal, url in endpoints:
        try:
            resp = requests.get(url, timeout=3.5, headers={"User-Agent": "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"})
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("result", {}).get("results", [])
                for pkg in results[:5]:
                    datasets.append({
                        "id": pkg.get("id", ""),
                        "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                        "portal": portal,
                        "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                        "url": pkg.get("url") or (
                            f"https://www.datosabiertos.gob.pe/dataset/{pkg.get('name')}" if portal == "PCM"
                            else f"https://datos.minsa.gob.pe/dataset/{pkg.get('name')}"
                        ),
                        "demo": False
                    })
        except Exception:
            # En caso de timeout o error de red, continuar
            pass
            
    # Si no se pudo obtener ningún dataset en vivo, usar fallback
    if not datasets:
        datasets = load_ckan_fallback()
        
    return datasets

@st.cache_data
def load_polity():
    """Carga las 4 subsecciones de Polity and Policy."""
    path = os.path.join("data", "polity.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return []

@st.cache_data
def load_estudiantes():
    """Carga las 5 subsecciones de Estudiantes y apuntes de sistemas administrativos."""
    path = os.path.join("data", "estudiantes.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return []

@st.cache_data
def load_cursos():
    """Carga el catálogo de cursos."""
    path = os.path.join("data", "cursos.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return []

@st.cache_data
def load_becas():
    """Carga las becas y oportunidades."""
    path = os.path.join("data", "becas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return []
