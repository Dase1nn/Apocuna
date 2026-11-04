import requests
import json

headers = {'User-Agent': 'ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)'}

def test_gobpe_json_attributes():
    url = "https://www.gob.pe/busquedas.json?institucion=&q=gesti%C3%B3n+p%C3%BAblica"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and 'attributes' in data['data']:
                attrs = data['data']['attributes']
                print("gob.pe JSON attributes keys:", list(attrs.keys()))
                if 'results' in attrs:
                    print("results type:", type(attrs['results']))
                    if len(attrs['results']) > 0:
                        print("first result keys:", attrs['results'][0].keys())
                if 'documentos' in attrs:
                    print("documentos type:", type(attrs['documentos']))
    except Exception as e:
        print("gob.pe json error:", repr(e))

test_gobpe_json_attributes()
