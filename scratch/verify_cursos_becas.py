import requests
import re
from datetime import datetime, timezone

urls = {
    "Santander Open Academy": "https://www.santanderopenacademy.com/",
    "Coursera": "https://www.coursera.org/",
    "Campus Virtual CEPAL": "https://www.cepal.org/es/capacitacion",
    "ENAP SERVIR": "https://www.enap.edu.pe/",
    "Academia BID": "https://cursos.iadb.org/es",
    "Banco Mundial OLC": "https://olc.worldbank.org/",
    "Aspire": "https://www.aspireleaders.org/",
    "PRONABEC": "https://www.pronabec.gob.pe/",
    "SENAJU": "https://juventud.gob.pe/",
    "Aplijoven": "https://aplijoven.pe/"
}

print("Resultados de verificación:")
headers = {"User-Agent": "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"}
for name, url in urls.items():
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        title_match = re.search(r'<title[^>]*>(.*?)</title>', r.text, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Sin title"
        print(f"[{name}] HTTP {r.status_code} | URL Final: {r.url} | Title: {title}")
    except Exception as e:
        print(f"[{name}] ERROR: {str(e)}")
