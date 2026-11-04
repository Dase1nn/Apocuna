import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from config import CKAN_MINSA_HABILITADO, CKAN_PCM_HABILITADO
except ImportError:
    CKAN_MINSA_HABILITADO = False
    CKAN_PCM_HABILITADO = False

USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"

PORTALS_CONFIG = [
    {
        "key": "PCM",
        "enabled": CKAN_PCM_HABILITADO,
        "url": "https://www.datosabiertos.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10",
        "base_dataset": "https://www.datosabiertos.gob.pe/dataset",
        "disabled_code": "deshabilitado",
        "disabled_reason": "deshabilitado: el portal bloquea clientes automáticos (HTTP 418 de un WAF, verificado 2026-10-02)",
    },
    {
        "key": "MINSA",
        "enabled": CKAN_MINSA_HABILITADO,
        "url": "https://datos.minsa.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10",
        "base_dataset": "https://datos.minsa.gob.pe/dataset",
        "disabled_code": "sin conexión",
        "disabled_reason": "sin conexión: portal deshabilitado en config.py (no disponible, verificado 2026-10-02)",
    },
]


def _format_http_error(status_code: int) -> str:
    if status_code == 404:
        return "404: ruta de API CKAN inexistente"
    if status_code == 418:
        return "418: bloqueado por CloudWAF"
    return f"{status_code}: respuesta HTTP no exitosa"


def _query_portal(cfg: dict, limit: int, timeout_red: int) -> tuple[list, dict, str | None]:
    key = cfg["key"]
    if not cfg["enabled"]:
        return [], {"codigo": cfg["disabled_code"], "causa": cfg["disabled_reason"]}, f"{key}: {cfg['disabled_reason']}"

    try:
        resp = requests.get(cfg["url"], timeout=timeout_red, headers={"User-Agent": USER_AGENT})
        if resp.status_code != 200:
            causa = _format_http_error(resp.status_code)
            return [], {"codigo": str(resp.status_code), "causa": causa}, f"{key}: {causa}"

        results = resp.json().get("result", {}).get("results", [])
        items = [
            {
                "id": f"ckan_{key.lower()}_{pkg.get('id', '')[:8]}",
                "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                "portal": key,
                "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                "url": pkg.get("url") or f"{cfg['base_dataset']}/{pkg.get('name')}",
            }
            for pkg in results[:limit]
        ]
        return items, {"codigo": "200", "causa": "OK"}, None
    except requests.exceptions.ConnectTimeout:
        causa = "sin conexión: tiempo de espera agotado"
        return [], {"codigo": "sin conexión", "causa": causa}, f"{key}: {causa}"
    except Exception:
        causa = "sin conexión: causa no determinada"
        return [], {"codigo": "sin conexión", "causa": causa}, f"{key}: {causa}"


def fetch_ckan(limit=10, timeout_red=10):
    datasets = []
    portales_estado = {}
    errores_lista = []

    for cfg in PORTALS_CONFIG:
        items, estado, err = _query_portal(cfg, limit, timeout_red)
        datasets.extend(items)
        portales_estado[cfg["key"]] = estado
        if err:
            errores_lista.append(err)

    return datasets, (portales_estado, errores_lista)
