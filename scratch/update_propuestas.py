import json

path = 'C:\\Users\\Gaston Silva\\Apocuna\\data\\fuentes_propuestas.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    estado = item.get("estado", "")
    if estado == "propuesta sin aplicar" or estado == "pendiente" or estado == "por confirmar":
        item["estado"] = "aplicado por el sistema"

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
