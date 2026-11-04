import requests
import json
import re

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_json_content():
    url = "https://www.gob.pe/busquedas.json?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and isinstance(data['data'], dict):
                print("gob.pe JSON data keys:", list(data['data'].keys()))
                if 'resultados' in data['data']:
                    print("gob.pe JSON first result:", list(data['data']['resultados'][0].keys()) if len(data['data']['resultados']) > 0 else "empty")
                elif 'results' in data['data']:
                    print("gob.pe JSON first result:", list(data['data']['results'][0].keys()) if len(data['data']['results']) > 0 else "empty")
                elif 'aggs' in data['data'] or 'hits' in data['data']:
                    # Looks like elasticsearch
                    print("elasticsearch-like data")
    except Exception as e:
        print("gob.pe json error", repr(e))

def test_elperuano_norma():
    url = "https://busquedas.elperuano.pe/dispositivo/NL/2558606-1"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("elperuano norma HTML size:", len(r.text))
        # Look for typical norm structure
        content = re.search(r'<div class="texto-norma">(.*?)</div>', r.text, re.DOTALL | re.IGNORECASE)
        if content:
            print("elperuano norma content found, size:", len(content.group(1)))
        else:
            # Maybe the text is directly in p tags or we can see if it mentions "Que," or "Considerando:"
            if "Considerando:" in r.text or "CONSIDERANDO:" in r.text:
                print("elperuano norma text found (Considerando)")
            elif "Que," in r.text or "QUE," in r.text:
                print("elperuano norma text found (Que,)")
            else:
                print("elperuano norma text not obviously found")
            # print sample
            print("elperuano norma HTML excerpt:", r.text[:200])
    except Exception as e:
        print("elperuano norma error:", repr(e))

test_gobpe_json_content()
test_elperuano_norma()
