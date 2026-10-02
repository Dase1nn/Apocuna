import requests

CKAN_ENDPOINTS = [
    {"url": "https://www.datosabiertos.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10", "portal": "PCM"},
    {"url": "https://datos.minsa.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10", "portal": "MINSA"}
]

def fetch_ckan(limit=10, timeout_red=10):
    datasets = []
    descartados = []
    
    for endpoint in CKAN_ENDPOINTS:
        try:
            resp = requests.get(endpoint["url"], timeout=timeout_red, headers={"User-Agent": "Apocuna/1.0"})
            resp.raise_for_status()
            data = resp.json()
            results = data.get("result", {}).get("results", [])
            for pkg in results[:limit]:
                datasets.append({
                    "id": f"ckan_{endpoint['portal'].lower()}_{pkg.get('id', '')[:8]}",
                    "titulo": pkg.get("title") or pkg.get("name", "Dataset sin título"),
                    "portal": endpoint["portal"],
                    "fecha_modificacion_iso": pkg.get("metadata_modified", ""),
                    "url": pkg.get("url") or (
                        f"https://www.datosabiertos.gob.pe/dataset/{pkg.get('name')}" if endpoint["portal"] == "PCM"
                        else f"https://datos.minsa.gob.pe/dataset/{pkg.get('name')}"
                    )
                })
        except Exception as e:
            descartados.append(f"{endpoint['url']} - Error: {e}")
            
    return datasets, descartados
