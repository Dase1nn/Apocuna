import requests
import json

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_json_content():
    url = "https://www.gob.pe/busquedas.json?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and len(data['data']) > 0:
                print("gob.pe JSON first item:", json.dumps(data['data'][0], indent=2)[:500])
    except Exception as e:
        print("error", e)

def test_elperuano_rss():
    url = "https://elperuano.pe/rss/normaslegales.xml"
    url2 = "https://diariooficial.elperuano.pe/rss/normaslegales"
    try:
        r1 = requests.get(url, headers=headers, timeout=10)
        print("elperuano RSS 1 status:", r1.status_code)
        r2 = requests.get(url2, headers=headers, timeout=10)
        print("elperuano RSS 2 status:", r2.status_code)
    except Exception as e:
        pass

test_gobpe_json_content()
test_elperuano_rss()
