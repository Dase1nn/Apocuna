import os
import json
import requests
import feedparser
from datetime import datetime, timezone
from time import mktime
from urllib.parse import urlparse

HEADERS = {"User-Agent": "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"}
FEEDS = [
    {"fuente": "Politai", "url": "https://revistas.pucp.edu.pe/index.php/politai/gateway/plugin/WebFeedGatewayPlugin/rss2"},
    {"fuente": "CLACSO", "url": "https://www.clacso.org/feed/"},
]
QUERIES = [
    "gobernanza subnacional Perú",
    "políticas públicas Perú",
    "sociología política Perú",
    "gestión pública Perú",
]


def _root_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_known_domains() -> list:
    path = os.path.join(_root_dir(), "data", "fuentes.json")
    domains = ["openalex.org"]
    if not os.path.exists(path):
        return domains
    try:
        with open(path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                u = item.get("url", "")
                if u:
                    domains.append(urlparse(u).netloc.replace("www.", ""))
    except Exception:
        pass
    return domains


def write_fuentes_propuestas(url: str, http_code: int):
    path = os.path.join(_root_dir(), "data", "fuentes_propuestas.json")
    try:
        data = json.load(open(path, "r", encoding="utf-8")) if os.path.exists(path) else []
        if any(item.get("url") == url for item in data):
            return
        data.append({"url": url, "estado": "pendiente", "codigo_http": http_code})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _parse_entry_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt_obj = datetime.fromtimestamp(mktime(entry.published_parsed), timezone.utc)
        return dt_obj.isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fetch_rss_feeds(timeout_red: int) -> tuple[list, list]:
    items, errores = [], []
    for f in FEEDS:
        try:
            r = requests.get(f["url"], headers=HEADERS, timeout=timeout_red)
            if r.status_code != 200:
                errores.append(f"{f['fuente']}: HTTP {r.status_code}")
                continue
            for entry in feedparser.parse(r.content).entries[:5]:
                items.append({
                    "id": entry.get("id", entry.link),
                    "titulo": entry.title,
                    "autores": entry.get("author", "Autor Institucional"),
                    "fuente": f["fuente"],
                    "fecha_iso": _parse_entry_date(entry),
                    "url": entry.link,
                    "tipo": "articulo",
                    "resumen": entry.get("summary", "")[:300],
                })
        except Exception as e:
            errores.append(f"{f['fuente']}: Error de conexión ({e})")
    return items, errores


def _is_candidate_domain(domain: str, known_domains: list) -> bool:
    if domain in known_domains:
        return False
    return domain.endswith((".gob.pe", ".edu.pe", ".org.pe", ".org"))


def _fetch_openalex_works(timeout_red: int, known_domains: list) -> tuple[list, list]:
    items, errores = [], []
    email = os.environ.get("OPENALEX_EMAIL", "")
    base_url = "https://api.openalex.org/works"

    for q in QUERIES:
        params = {"search": q, "sort": "publication_date:desc", "per-page": 3}
        if email:
            params["mailto"] = email
        try:
            r = requests.get(base_url, headers=HEADERS, params=params, timeout=timeout_red)
            if r.status_code != 200:
                errores.append(f"OpenAlex ({q}): HTTP {r.status_code}")
                continue
            for work in r.json().get("results", []):
                wid = work.get("id")
                url = work.get("primary_location", {}).get("landing_page_url") or wid
                dt = work.get("publication_date", "")
                dt_iso = f"{dt}T00:00:00Z" if dt else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                authors = ", ".join(a.get("author", {}).get("display_name", "") for a in work.get("authorships", []))
                if url and url != wid:
                    domain = urlparse(url).netloc.replace("www.", "")
                    if _is_candidate_domain(domain, known_domains):
                        write_fuentes_propuestas(url, 200)
                items.append({
                    "id": wid,
                    "titulo": work.get("title") or "Sin título",
                    "autores": authors,
                    "fuente": "OpenAlex",
                    "fecha_iso": dt_iso,
                    "url": url,
                    "tipo": "articulo",
                    "resumen": "",
                })
        except Exception as e:
            errores.append(f"OpenAlex ({q}): Error de conexión ({e})")
    return items, errores


def fetch_academico(timeout_red=10):
    rss_items, rss_err = _fetch_rss_feeds(timeout_red)
    oa_items, oa_err = _fetch_openalex_works(timeout_red, get_known_domains())
    return rss_items + oa_items, rss_err + oa_err
