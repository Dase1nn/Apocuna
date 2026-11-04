import requests
import json
import xml.etree.ElementTree as ET

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_json_content():
    url = "https://www.gob.pe/busquedas.json?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                print("gob.pe JSON keys:", list(data.keys()))
                if 'data' in data:
                    print("gob.pe JSON data type:", type(data['data']))
                    if len(data['data']) > 0:
                        print("gob.pe JSON first item keys:", data['data'][0].keys() if isinstance(data['data'][0], dict) else type(data['data'][0]))
                        if isinstance(data['data'][0], dict):
                            print("title:", data['data'][0].get('title', 'N/A'))
                            print("url:", data['data'][0].get('url', 'N/A'))
            else:
                print("gob.pe JSON is list, len:", len(data))
    except Exception as e:
        print("gob.pe json error", repr(e))

def test_elperuano_sitemap_normas():
    url = "https://busquedas.elperuano.pe/sitemap/sitemap-normas_legales.xml"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("elperuano sitemap normas status:", r.status_code)
        if r.status_code == 200:
            print(r.text[:500])
    except Exception as e:
        print("sitemap error:", repr(e))

test_gobpe_json_content()
test_elperuano_sitemap_normas()
