import json

path = 'C:\\Users\\Gaston Silva\\Apocuna\\data\\fuentes_propuestas.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

data.append({
    "url": "https://www.aspireleaders.org/",
    "estado": "pendiente",
    "codigo_http": 200,
    "nota": "El usuario mencionó 'Aspire' sin más datos. Podría referirse al Aspire Leaders Program de Harvard."
})

data.append({
    "url": "https://aplijoven.pe/",
    "estado": "pendiente",
    "codigo_http": "Error DNS",
    "nota": "El usuario mencionó 'Aplijoven' pero el dominio no resuelve o no existe. Por verificar."
})

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
