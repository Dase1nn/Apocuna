import requests
import re
import time

urls = [
    "https://cies.org.pe/",
    "https://cies.org.pe/investigaciones/",
    "https://iep.org.pe/",
    "https://repositorio.iep.org.pe/",
    "https://www.grade.org.pe/",
    "https://revistas.pucp.edu.pe/index.php/politai",
    "https://www.clacso.org/",
    "https://cybertesis.unmsm.edu.pe/"
]

headers = {"User-Agent": "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"}

for url in urls:
    try:
        time.sleep(1)
        r = requests.get(url, headers=headers, timeout=10)
        html = r.text
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "No Title"
        print(f"\nURL: {url} | HTTP {r.status_code} | {title}")
        
        links = re.findall(r'<link[^>]+rel=[\'"]?alternate[\'"]?[^>]*>', html, re.IGNORECASE)
        for link in links:
            if 'rss' in link.lower() or 'atom' in link.lower():
                href_match = re.search(r'href=[\'"]([^\'"]+)[\'"]', link, re.IGNORECASE)
                href = href_match.group(1) if href_match else 'None'
                type_match = re.search(r'type=[\'"]([^\'"]+)[\'"]', link, re.IGNORECASE)
                typ = type_match.group(1) if type_match else 'None'
                print(f"  -> RSS/Atom: {href} ({typ})")
    except Exception as e:
        print(f"\nURL: {url} | Error: {e}")
