import os
import json
import requests
import feedparser
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_known_domains():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "fuentes.json")
    domains = ["openalex.org"]
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for item in data:
                    u = item.get("url", "")
                    if u:
                        d = urlparse(u).netloc.replace("www.", "")
                        domains.append(d)
            except:
                pass
    return domains

def write_fuentes_propuestas(url, http_code):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "fuentes_propuestas.json")
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        for item in data:
            if item.get("url") == url:
                return
        data.append({
            "url": url,
            "estado": "pendiente",
            "codigo_http": http_code
        })
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def fetch_academico(timeout_red=10):
    items = []
    errores = []

    headers = {"User-Agent": "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"}

    feeds = [
        {"fuente": "Politai", "url": "https://revistas.pucp.edu.pe/index.php/politai/gateway/plugin/WebFeedGatewayPlugin/rss2"},
        {"fuente": "CLACSO", "url": "https://www.clacso.org/feed/"}
    ]

    for f in feeds:
        try:
            r = requests.get(f["url"], headers=headers, timeout=timeout_red)
            if r.status_code == 200:
                d = feedparser.parse(r.content)
                for entry in d.entries[:5]:
                    dt = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        from time import mktime
                        dt_obj = datetime.fromtimestamp(mktime(entry.published_parsed), timezone.utc)
                        dt = dt_obj.isoformat().replace('+00:00', 'Z')
                    
                    items.append({
                        "id": entry.get("id", entry.link),
                        "titulo": entry.title,
                        "autores": entry.get("author", "Autor Desconocido"),
                        "fuente": f["fuente"],
                        "fecha_iso": dt,
                        "url": entry.link,
                        "tipo": "articulo",
                        "resumen": entry.get("summary", "")[:300]
                    })
            else:
                errores.append(f"{f['fuente']}: HTTP {r.status_code}")
        except Exception as e:
            errores.append(f"{f['fuente']}: Error de conexión ({str(e)})")

    queries = [
        "gobernanza subnacional Perú",
        "políticas públicas Perú",
        "sociología política Perú",
        "gestión pública Perú"
    ]
    email = os.environ.get("OPENALEX_EMAIL", "")
    base_url = "https://api.openalex.org/works"
    
    known_domains = get_known_domains()

    for q in queries:
        try:
            params = {
                "search": q,
                "sort": "publication_date:desc",
                "per-page": 3
            }
            if email:
                params["mailto"] = email
            r = requests.get(base_url, headers=headers, params=params, timeout=timeout_red)
            if r.status_code == 200:
                data = r.json()
                for work in data.get("results", []):
                    wid = work.get("id")
                    title = work.get("title") or "Sin título"
                    authors = ", ".join([a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])])
                    url = work.get("primary_location", {}).get("landing_page_url") or wid
                    dt = work.get("publication_date", "")
                    dt_iso = dt + "T00:00:00Z" if dt else datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    
                    if url and url != wid:
                        domain = urlparse(url).netloc.replace("www.", "")
                        if domain not in known_domains and (domain.endswith(".gob.pe") or domain.endswith(".edu.pe") or domain.endswith(".org.pe") or domain.endswith(".org")):
                            write_fuentes_propuestas(url, 200)

                    items.append({
                        "id": wid,
                        "titulo": title,
                        "autores": authors,
                        "fuente": "OpenAlex",
                        "fecha_iso": dt_iso,
                        "url": url,
                        "tipo": "articulo",
                        "resumen": ""
                    })
            else:
                errores.append(f"OpenAlex ({q}): HTTP {r.status_code}")
        except Exception as e:
            errores.append(f"OpenAlex ({q}): Error de conexión ({str(e)})")

    return items, errores
