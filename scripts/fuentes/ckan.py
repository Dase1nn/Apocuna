import os
import sys
import requests

# Importar configuración del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from config import CKAN_MINSA_HABILITADO, CKAN_PCM_HABILITADO
except ImportError:
    CKAN_MINSA_HABILITADO = False
    CKAN_PCM_HABILITADO = False

USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"

def fetch_ckan(limit=10, timeout_red=10):
    datasets = []
    portales_estado = {}
    errores_lista = []
    
    # 1. Portal PCM (Plataforma Nacional de Datos Abiertos)
    if not CKAN_PCM_HABILITADO:
        causa = "deshabilitado: el portal bloquea clientes automáticos (HTTP 418 de un WAF, verificado 2026-10-02)"
        portales_estado["PCM"] = {"codigo": "deshabilitado", "causa": causa}
        errores_lista.append(f"PCM: {causa}")
    else:
        pcm_url = "https://www.datosabiertos.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10"
        try:
            resp = requests.get(pcm_url, timeout=timeout_red, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("result", {}).get("results", [])
                for pkg in results[:limit]:
                    datasets.append({
                        "id": f"ckan_pcm_{pkg.get('id', '')[:8]}",
                        "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                        "portal": "PCM",
                        "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                        "url": pkg.get("url") or f"https://www.datosabiertos.gob.pe/dataset/{pkg.get('name')}"
                    })
                portales_estado["PCM"] = {"codigo": "200", "causa": "OK"}
            else:
                causa = "404: ruta de API CKAN inexistente" if resp.status_code == 404 else f"{resp.status_code}: respuesta HTTP no exitosa"
                if resp.status_code == 418:
                    causa = "418: bloqueado por CloudWAF"
                portales_estado["PCM"] = {"codigo": str(resp.status_code), "causa": causa}
                errores_lista.append(f"PCM: {causa}")
        except requests.exceptions.ConnectTimeout:
            causa = "sin conexión: tiempo de espera agotado"
            portales_estado["PCM"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"PCM: {causa}")
        except requests.exceptions.RequestException:
            causa = "sin conexión: causa no determinada"
            portales_estado["PCM"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"PCM: {causa}")
        except Exception:
            causa = "sin conexión: causa no determinada"
            portales_estado["PCM"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"PCM: {causa}")

    # 2. Portal MINSA
    if not CKAN_MINSA_HABILITADO:
        causa = "sin conexión: portal deshabilitado en config.py (no disponible, verificado 2026-10-02)"
        portales_estado["MINSA"] = {"codigo": "sin conexión", "causa": causa}
        errores_lista.append(f"MINSA: {causa}")
    else:
        minsa_url = "https://datos.minsa.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10"
        try:
            resp = requests.get(minsa_url, timeout=timeout_red, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("result", {}).get("results", [])
                for pkg in results[:limit]:
                    datasets.append({
                        "id": f"ckan_minsa_{pkg.get('id', '')[:8]}",
                        "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                        "portal": "MINSA",
                        "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                        "url": pkg.get("url") or f"https://datos.minsa.gob.pe/dataset/{pkg.get('name')}"
                    })
                portales_estado["MINSA"] = {"codigo": "200", "causa": "OK"}
            else:
                causa = f"{resp.status_code}: respuesta HTTP no exitosa"
                portales_estado["MINSA"] = {"codigo": str(resp.status_code), "causa": causa}
                errores_lista.append(f"MINSA: {causa}")
        except requests.exceptions.ConnectTimeout:
            causa = "sin conexión: tiempo de espera agotado"
            portales_estado["MINSA"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"MINSA: {causa}")
        except requests.exceptions.RequestException:
            causa = "sin conexión: causa no determinada"
            portales_estado["MINSA"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"MINSA: {causa}")
        except Exception:
            causa = "sin conexión: causa no determinada"
            portales_estado["MINSA"] = {"codigo": "sin conexión", "causa": causa}
            errores_lista.append(f"MINSA: {causa}")

    return datasets, (portales_estado, errores_lista)
