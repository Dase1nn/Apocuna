import requests
url = "https://www.gob.pe/institucion/contraloria/noticias.rss"
r = requests.get(url, headers={"User-Agent": "ApocunaBot"})
print(r.status_code, r.text[:200])
