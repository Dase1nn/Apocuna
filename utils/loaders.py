import os
import glob
import json
import html
import requests
import streamlit as st

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

@st.cache_data
def load_noticias():
    """Carga el catálogo de noticias de ejemplo o generadas."""
    path = os.path.join("data", "generated", "noticias.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return []

@st.cache_data
def load_normas():
    """Carga el catálogo de normas de ejemplo o generadas."""
    path = os.path.join("data", "generated", "normas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return []

@st.cache_data
def load_ckan_fallback():
    """Carga el dataset fallback de portales CKAN."""
    path = os.path.join("data", "generated", "ckan.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Aviso: No se pudo cargar {path} ({e})")
        return []

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
            endpoints.append((portal, f.get("url")))
            
    for portal, url in endpoints:
        try:
            resp = requests.get(url, timeout=3.5)
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
