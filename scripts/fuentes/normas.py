import feedparser
import requests
import hashlib
from datetime import datetime, timezone, timedelta
import html
import re

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = html.unescape(cleantext)
    return cleantext.strip()

def generate_id(url):
    return "norma_" + hashlib.md5(url.encode()).hexdigest()[:8]

def parse_date(date_str, url, warnings):
    tz_lima = timezone(timedelta(hours=-5))
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        dt_lima = dt.astimezone(tz_lima)
        now_lima = datetime.now(tz_lima)
        if dt_lima > now_lima:
            warnings.append(f"Advertencia: Fecha futura en {url} ({dt_lima.isoformat()})")
        return dt_lima.isoformat()
    except:
        return datetime.now(tz_lima).isoformat()

def get_tipo_norma(titulo):
    titulo = titulo.upper()
    if "RESOLUCIÓN" in titulo or "RESOLUCION" in titulo:
        return "Resolución"
    if "DECRETO SUPREMO" in titulo:
        return "Decreto Supremo"
    if "LEY" in titulo:
        return "Ley"
    if "DECRETO LEGISLATIVO" in titulo:
        return "Decreto Legislativo"
    return "Norma Legal"

def fetch_normas(limit=10, timeout_red=10):
    normas = []
    descartados = []
    warnings = []
    
    feed_url = "https://news.google.com/rss/search?q=site:elperuano.pe+normas+legales&hl=es-419&gl=PE&ceid=PE:es-419"
    
    try:
        resp = requests.get(feed_url, timeout=timeout_red)
        resp.raise_for_status()
        
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:limit]:
            titulo_limpio = clean_html(entry.title)[:300]
            real_source = getattr(entry, "source", {}).get("title", "Google News")
            
            normas.append({
                "id": generate_id(entry.link),
                "titulo": titulo_limpio,
                "tipo_norma": get_tipo_norma(titulo_limpio),
                "entidad": real_source,
                "fecha_iso": parse_date(entry.get("published", ""), entry.link, warnings),
                "url": entry.link,
                "grupo": "Noticias sobre normas legales"
            })
    except Exception as e:
        descartados.append(f"{feed_url} - Error: {e}")
        
    descartados.extend(warnings)
    return normas, descartados


