import requests
import time
import re

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_spij_home():
    try:
        r = requests.get('https://spij.minjus.gob.pe/spij-ext-web/', headers=headers, timeout=10)
        print("SPIJ home status:", r.status_code)
        print(r.text[:500])
    except Exception as e:
        print("SPIJ home error:", e)

def test_elperuano_home():
    try:
        r = requests.get('https://busquedas.elperuano.pe/', headers=headers, timeout=10)
        print("elperuano home status:", r.status_code)
        forms = re.findall(r'<form[^>]+action=["\']([^"\']+)["\']', r.text)
        print("El Peruano search form actions:", forms)
        # Also check for links
        links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
        print("Sample links elperuano:", [l for l in links if 'normas' in l.lower()][:5])
    except Exception as e:
        print("elperuano home error:", e)

def test_gobpe_search():
    url = "https://www.gob.pe/busquedas?institucion=&q=gesti%C3%B3n+p%C3%BAblica&tipo_norma="
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("gob.pe search HTML length:", len(r.text))
        links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
        norm_links = [a for a in links if '/normas/' in a or '/institucion/' in a]
        print("Sample norm links from gob.pe:", norm_links[:5])
    except Exception as e:
        print("gob.pe error:", e)

test_spij_home()
time.sleep(10)
test_elperuano_home()
time.sleep(10)
test_gobpe_search()
