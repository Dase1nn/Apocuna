import json

path = r'C:\Users\Gaston Silva\Apocuna\data\estudiantes.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Modify URLs
for sub in data:
    for t in sub.get('tarjetas', []):
        if t.get('id') == 'est_card_3_1':
            t['url'] = 'https://www.gob.pe/jne'
        elif t.get('id') == 'est_card_4_1':
            t['url'] = 'https://linktr.ee/ximacrocp'
            
    for a in sub.get('apuntes', []):
        if a.get('id') == 'apunte_001':
            a['url'] = 'https://www.mef.gob.pe/'
        elif a.get('id') == 'apunte_002':
            a['url'] = 'https://www.gob.pe/institucion/pcm/normas-legales/3233804-103-2022-pcm'
        elif a.get('id') == 'apunte_003':
            a['url'] = 'https://www.ceplan.gob.pe/'
        elif a.get('id') == 'apunte_004':
            a['url'] = 'https://www.mef.gob.pe/es/inversion-publica'
        elif a.get('id') == 'apunte_006':
            a['url'] = 'https://www.servir.gob.pe/'
        elif a.get('id') == 'apunte_007':
            a['url'] = 'https://www.mef.gob.pe/es/sistema-nacional-de-abastecimiento'
        elif a.get('id') == 'apunte_008':
            a['url'] = 'https://www.mef.gob.pe/es/tesoro-publico'

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
