import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from utils.loaders import load_noticias, load_normas, load_ckan_fallback

REMOTE_URL = "https://raw.githubusercontent.com/Dase1nn/Apocuna/refs/heads/data/data/generated"
INVALID_URL = "https://raw.githubusercontent.com/Dase1nn/Apocuna/refs/heads/data/invalid_non_existent_path"

original_get = requests.get
last_fetch = {}

def spied_get(url, *args, **kwargs):
    try:
        resp = original_get(url, *args, **kwargs)
        last_fetch[url] = resp.status_code
        return resp
    except Exception as e:
        last_fetch[url] = f"Error: {e}"
        raise

requests.get = spied_get

def test_case(name, base_url):
    print(f"=== CASO {name} ===")
    if base_url is not None:
        os.environ["DATA_BASE_URL"] = base_url
    else:
        os.environ.pop("DATA_BASE_URL", None)
        
    load_noticias.clear()
    load_normas.clear()
    load_ckan_fallback.clear()
    
    for fn, fname in [(load_noticias, "noticias.json"), (load_normas, "normas.json"), (load_ckan_fallback, "ckan.json")]:
        last_fetch.clear()
        data = fn()
        count = len(data)
        
        expected_remote = f"{base_url.rstrip('/')}/{fname}" if base_url else None
        if expected_remote and last_fetch.get(expected_remote) == 200:
            origen = f"REMOTO (HTTP 200 de {expected_remote})"
        else:
            local_path = os.path.join("data", "generated", fname)
            remote_status = last_fetch.get(expected_remote) if expected_remote else "no configurado"
            origen = f"LOCAL ({local_path}) [Intento remoto: {remote_status}]"
            
        print(f"  {fname}: {count} ítems | Origen: {origen}")
    print()

if __name__ == "__main__":
    test_case("(a) Variable definida y URL correcta", REMOTE_URL)
    test_case("(b) Variable definida con URL inválida", INVALID_URL)
    test_case("(c) Sin variable de entorno (solo local)", None)
