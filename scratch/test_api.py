import requests
import json
import re

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_api():
    url = "https://www.gob.pe/api/v1/documentos?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("gob.pe API status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                print("API response keys:", list(data.keys()))
            elif isinstance(data, list):
                print("API response is a list, first item:", data[0].keys() if len(data)>0 else "empty")
        else:
            print(r.text[:100])
    except Exception as e:
        print("gob.pe API error:", e)

def test_elperuano_diario():
    url = "https://diariooficial.elperuano.pe/Normas"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("elperuano Normas status:", r.status_code)
        links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
        norm_links = [l for l in links if 'normas' in l.lower() or 'norma' in l.lower()]
        print("Sample links elperuano Normas:", norm_links[:5])
    except Exception as e:
        print("elperuano Normas error:", e)

test_gobpe_api()
test_elperuano_diario()
