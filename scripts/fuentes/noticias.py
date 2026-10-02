import feedparser
import requests
import hashlib
from datetime import datetime, timezone, timedelta
import html
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import EXCLUDED_DOMAINS
except ImportError:
    EXCLUDED_DOMAINS = []

FEEDS = [
    {"url": "https://news.google.com/rss/search?q=gestion+publica+peru&hl=es-419&gl=PE&ceid=PE:es-419", "categoria": "gestion"},
    {"url": "https://news.google.com/rss/search?q=politicas+publicas+peru&hl=es-419&gl=PE&ceid=PE:es-419", "categoria": "politicas_publicas"},
    {"url": "https://news.google.com/rss/search?q=politica+peru&hl=es-419&gl=PE&ceid=PE:es-419", "categoria": "politica"}
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = html.unescape(cleantext)
    return cleantext.strip()

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

def generate_id(url):
    return "noticia_" + hashlib.md5(url.encode()).hexdigest()[:8]

def fetch_noticias(limit=10, timeout_red=10):
    noticias = []
    descartados = []
    warnings = []
    
    for feed_info in FEEDS:
        try:
            resp = requests.get(feed_info["url"], timeout=timeout_red)
            resp.raise_for_status()
            
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:limit]:
                # Verificar dominios excluidos
                url_str = entry.link.lower()
                if any(domain in url_str for domain in EXCLUDED_DOMAINS):
                    continue
                    
                real_source = getattr(entry, "source", {}).get("title", "Google News")
                titulo_limpio = clean_html(entry.title)[:300]
                resumen_limpio = clean_html(getattr(entry, "summary", ""))[:300]
                
                # Si resumen es casi igual al titulo, omitirlo
                if resumen_limpio.startswith(titulo_limpio) or titulo_limpio in resumen_limpio:
                    resumen_limpio = ""
                
                noticia = {
                    "id": generate_id(entry.link),
                    "titulo": titulo_limpio,
                    "fuente": real_source,
                    "categoria": feed_info["categoria"],
                    "fecha_iso": parse_date(entry.get("published", ""), entry.link, warnings),
                    "url": entry.link,
                    "resumen": resumen_limpio
                }
                noticias.append(noticia)
        except Exception as e:
            descartados.append(f"{feed_info['url']} - Error: {e}")
            
    # Añadimos warnings a descartados para que se guarden en errores_recientes
    descartados.extend(warnings)
    return noticias, descartados

