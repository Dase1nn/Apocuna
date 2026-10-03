import requests
import json

url = 'https://api.openalex.org/works'
params = {
    'search': 'gestión pública Perú',
    'sort': 'publication_date:desc',
    'per-page': 3
}

r = requests.get(url, params=params)
if r.status_code == 200:
    data = r.json()
    for item in data.get('results', []):
        print(f"Title: {item.get('title')}")
        print(f"Date: {item.get('publication_date')}")
        print(f"URL: {item.get('id')}")
else:
    print(f"Error {r.status_code}")
