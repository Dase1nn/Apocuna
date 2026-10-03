import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

# Add parent to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import TIMEOUT_RED
except ImportError:
    TIMEOUT_RED = 10

from fuentes.noticias import fetch_noticias
from fuentes.ckan import fetch_ckan
from fuentes.normas import fetch_normas

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "generated")
ESTADO_FILE = os.path.join(DATA_DIR, "estado.json")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_json(data, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def deduplicate_and_sort(old_data, new_data, limit_count=50, sort_field='fecha_iso'):
    # Remove demo items from old_data if we want true data only
    old_data = [d for d in old_data if not d.get("demo", False)]
    
    seen_urls = set()
    combined = []
    
    # Add new first to prefer them
    for item in new_data:
        item.pop("demo", None)
        if item.get("url") not in seen_urls:
            seen_urls.add(item.get("url"))
            combined.append(item)
            
    # Then old
    for item in old_data:
        item.pop("demo", None)
        if item.get("url") not in seen_urls:
            seen_urls.add(item.get("url"))
            combined.append(item)
            
    # Sort with parsed datetime if possible
    def get_sort_key(x):
        val = x.get(sort_field, "")
        try:
            # Reemplazar Z por +00:00 para parsear
            if val.endswith('Z'):
                val = val[:-1] + '+00:00'
            dt = datetime.fromisoformat(val)
            return dt.timestamp()
        except:
            return 0
            
    combined.sort(key=get_sort_key, reverse=True)
    return combined[:limit_count]

def generate_summary_with_gemini(text):
    if not HAS_GENAI or not text:
        return text
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return text
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') 
        prompt = f"Resume esta noticia en una sola frase corta (máximo 150 caracteres), directo al grano sin mencionar que es un resumen:\n\n{text}"
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Error con Gemini: {e}")
    return text

def should_update(estado, name, freq_hours, force):
    if force:
        return True
    last_update_str = estado.get(name, {}).get("last_success")
    if not last_update_str:
        return True
    try:
        if last_update_str.endswith('Z'):
            last_update_str = last_update_str[:-1] + '+00:00'
        last_update = datetime.fromisoformat(last_update_str)
        now_utc = datetime.now(timezone.utc)
        if now_utc - last_update > timedelta(hours=freq_hours):
            return True
        return False
    except:
        return True

def print_sample(name, data):
    if not data:
        print(f"Muestra de {name}: Vacio")
        return
    sample = data[0].copy()
    print(f"Muestra de {name}: {json.dumps(sample, ensure_ascii=False, indent=2)}")

def get_now_utc_str():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forzar", action="store_true", help="Ignorar frecuencias y forzar actualización")
    args = parser.parse_args()
    
    estado = {}
    if os.path.exists(ESTADO_FILE):
        with open(ESTADO_FILE, 'r', encoding='utf-8') as f:
            try:
                estado = json.load(f)
            except:
                pass
                
    if "fuentes" not in estado:
        estado["fuentes"] = {}
        
    print("Iniciando actualización de datos...")
    
    # 1. Noticias (cada 3 horas)
    if should_update(estado.get("fuentes", {}), "noticias", 3, args.forzar):
        print("\n[1] Actualizando noticias...")
        nuevas, desc_noticias = fetch_noticias(timeout_red=TIMEOUT_RED)
        if nuevas:
            viejas = load_json("noticias.json")
            if os.getenv("GEMINI_API_KEY") and HAS_GENAI:
                print("Usando Gemini para resumir noticias nuevas...")
                for n in nuevas:
                    if len(n.get("resumen", "")) > 100:
                        n["resumen"] = generate_summary_with_gemini(n["resumen"])
                        
            final = deduplicate_and_sort(viejas, nuevas, sort_field="fecha_iso")
            save_json(final, "noticias.json")
            estado["fuentes"]["noticias"] = {
                "last_success": get_now_utc_str(),
                "items": len(nuevas),
                "errores": desc_noticias
            }
            print(f"-> Noticias actualizadas: {len(nuevas)} nuevas obtenidas. Errores: {len(desc_noticias)}")
            if desc_noticias:
                print("   Errores en noticias:", desc_noticias)
            print_sample("noticias.json", final)
        else:
            print("-> Falló la recolección de noticias. Se conservan datos anteriores.")
            if "noticias" not in estado["fuentes"]:
                 estado["fuentes"]["noticias"] = {}
            estado["fuentes"]["noticias"]["errores_recientes"] = desc_noticias
            print("   Errores:", desc_noticias)
    else:
        print("\n[1] Noticias no requieren actualización aún.")
        
    # 2. Normas (cada 3 horas)
    if should_update(estado.get("fuentes", {}), "normas", 3, args.forzar):
        print("\n[2] Actualizando normas...")
        nuevas, desc_normas = fetch_normas(timeout_red=TIMEOUT_RED)
        if nuevas:
            viejas = load_json("normas.json")
            final = deduplicate_and_sort(viejas, nuevas, sort_field="fecha_iso")
            save_json(final, "normas.json")
            estado["fuentes"]["normas"] = {
                "last_success": get_now_utc_str(),
                "items": len(nuevas),
                "errores": desc_normas
            }
            print(f"-> Normas actualizadas: {len(nuevas)} nuevas obtenidas. Errores: {len(desc_normas)}")
            if desc_normas:
                print("   Errores en normas:", desc_normas)
            print_sample("normas.json", final)
        else:
            print("-> Falló la recolección de normas. Se conservan datos anteriores.")
            if "normas" not in estado["fuentes"]:
                 estado["fuentes"]["normas"] = {}
            estado["fuentes"]["normas"]["errores_recientes"] = desc_normas
            print("   Errores:", desc_normas)
    else:
        print("\n[2] Normas no requieren actualización aún.")
        
    # 3. CKAN (cada 6 horas)
    if should_update(estado.get("fuentes", {}), "ckan", 6, args.forzar):
        print("\n[3] Actualizando CKAN...")
        nuevas, desc_ckan = fetch_ckan(timeout_red=TIMEOUT_RED)
        portales_ckan = {}
        errores_ckan_list = []
        if isinstance(desc_ckan, tuple):
            portales_ckan, errores_ckan_list = desc_ckan
        elif isinstance(desc_ckan, list):
            errores_ckan_list = desc_ckan

        if nuevas:
            viejas = load_json("ckan.json")
            final = deduplicate_and_sort(viejas, nuevas, sort_field="fecha_modificacion_iso")
            save_json(final, "ckan.json")
            estado["fuentes"]["ckan"] = {
                "last_success": get_now_utc_str(),
                "items": len(nuevas),
                "portales": portales_ckan,
                "errores": errores_ckan_list
            }
            print(f"-> CKAN actualizado: {len(nuevas)} nuevos obtenidos. Errores: {len(errores_ckan_list)}")
            if errores_ckan_list:
                print("   Errores en CKAN:", errores_ckan_list)
            print_sample("ckan.json", final)
        else:
            print("-> Falló la recolección de CKAN (sin datos disponibles). Escribiendo lista vacía en ckan.json.")
            save_json([], "ckan.json")
            estado["fuentes"]["ckan"] = {
                "items": 0,
                "portales": portales_ckan,
                "errores_recientes": errores_ckan_list
            }
            print("   Estado por portal:", portales_ckan)
    else:
        print("\n[3] CKAN no requiere actualización aún.")
        
    estado["last_run"] = get_now_utc_str()
    save_json(estado, "estado.json")
    print("\nActualización completada.")

if __name__ == "__main__":
    main()

