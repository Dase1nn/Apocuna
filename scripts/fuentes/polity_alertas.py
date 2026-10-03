import requests
import feedparser
from datetime import datetime, timezone, timedelta
import html
import re
import hashlib

FEEDS = [
    {"url": "https://news.google.com/rss/search?q=%22Contralor%C3%ADa+General+de+la+Rep%C3%BAblica%22+Per%C3%BA+informe+control&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "Contraloría"},
    {"url": "https://news.google.com/rss/search?q=%22Defensor%C3%ADa+del+Pueblo%22+conflictos+sociales+Per%C3%BA&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "Defensoría"},
    {"url": "https://news.google.com/rss/search?q=%22Instituto+de+Estudios+Peruanos%22+encuesta&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "IEP"},
    {"url": "https://news.google.com/rss/search?q=%22GRADE%22+pol%C3%ADticas+p%C3%BAblicas+Per%C3%BA&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "GRADE"},
    {"url": "https://news.google.com/rss/search?q=%22CEPAL%22+Per%C3%BA+econom%C3%ADa&hl=es-419&gl=PE&ceid=PE:es-419", "fuente": "CEPAL"}
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

def fetch_polity_alertas(timeout_red=10):
    items = []
    errores = []
    
    for feed_info in FEEDS:
        try:
            resp = requests.get(feed_info["url"], timeout=timeout_red)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:4]:
                    titulo = clean_html(entry.title)[:300]
                    items.append({
                        "id": "pol_" + hashlib.md5(entry.link.encode()).hexdigest()[:8],
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
