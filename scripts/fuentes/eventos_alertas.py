import requests
import feedparser
from datetime import datetime, timezone, timedelta
import html
import re
import hashlib

FEEDS = [
    {"url": "https://news.google.com/rss/search?q=%22Congreso+Nacional+de+Ciencia+Pol%C3%ADtica%22+Per%C3%BA&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "Congresos Nacionales"},
    {"url": "https://news.google.com/rss/search?q=%22Macrocoloquio+de+Estudiantes+de+Ciencia+Pol%C3%ADtica%22&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "Macrocoloquio"},
    {"url": "https://news.google.com/rss/search?q=%22Seminario+de+Investigaci%C3%B3n+Educativa%22+SIEP+Per%C3%BA&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "SIEP"},
    {"url": "https://news.google.com/rss/search?q=CLAD+Congreso+Administraci%C3%B3n+P%C3%BAblica&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "CLAD"}
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext).strip()

def parse_date(date_str):
    tz_lima = timezone(timedelta(hours=-5))
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.astimezone(tz_lima).isoformat()
    except:
        return datetime.now(tz_lima).isoformat()

def fetch_eventos_alertas(timeout_red=10):
    items = []
    errores = []
    
    for feed_info in FEEDS:
        try:
            resp = requests.get(feed_info["url"], timeout=timeout_red)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:3]:
                    titulo = clean_html(entry.title)[:300]
                    items.append({
                        "id": "evt_" + hashlib.md5(entry.link.encode()).hexdigest()[:8],
                        "titulo": titulo,
                        "fuente": feed_info["fuente"],
                        "fecha_iso": parse_date(entry.get("published", "")),
                        "url": entry.link,
                        "resumen": ""
                    })
            else:
                errores.append(f"{feed_info['fuente']}: HTTP {resp.status_code}")
        except Exception as e:
            errores.append(f"{feed_info['fuente']}: Error ({str(e)})")
            
    return items, errores
