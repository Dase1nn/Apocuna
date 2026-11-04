import requests
import json
import re
from datetime import datetime

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_json():
    url = "https://www.gob.pe/busquedas.json?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("gob.pe JSON search status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                print("gob.pe JSON keys:", list(data.keys()))
                if 'data' in data:
                    print("Sample items:", len(data['data']))
            else:
                print("gob.pe JSON list length:", len(data))
    except Exception as e:
        print("gob.pe JSON error:", e)

def test_elperuano_normas_html():
    url = "https://diariooficial.elperuano.pe/Normas"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("elperuano Normas html size:", len(r.text))
        # Find any text that looks like a norm title, e.g., "Decreto Supremo" or "Resolución"
        norms = re.findall(r'>(Decreto Supremo[^<]+|Resolución[^<]+)<', r.text)
        print("Sample norms found:", norms[:5])
        
        # Check if there is an iframe or API call
        iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', r.text)
        print("Iframes:", iframes)
    except Exception as e:
        print("elperuano Normas html error:", e)

test_gobpe_json()
test_elperuano_normas_html()
