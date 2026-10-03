import json, glob

for f in glob.glob('data/*.json'):
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        def search_urls(obj):
            if isinstance(obj, dict):
                if 'url' in obj and not obj['url']:
                    print(f"Null or empty URL found in {f}: {obj.get('id', obj.get('titulo', 'unknown'))}")
                for v in obj.values():
                    search_urls(v)
            elif isinstance(obj, list):
                for item in obj:
                    search_urls(item)

        search_urls(data)
    except Exception as e:
        pass
