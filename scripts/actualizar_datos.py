import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import TIMEOUT_RED
except ImportError:
    TIMEOUT_RED = 10

from fuentes.noticias import fetch_noticias
from fuentes.ckan import fetch_ckan
from fuentes.normas import fetch_normas
from fuentes.academico import fetch_academico
from fuentes.polity_alertas import fetch_polity_alertas
from fuentes.eventos_alertas import fetch_eventos_alertas

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "generated")
ESTADO_FILE = os.path.join(DATA_DIR, "estado.json")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_json(data, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_iso_timestamp(val: str) -> float:
    if not val:
        return 0.0
    try:
        norm = val[:-1] + "+00:00" if val.endswith("Z") else val
        return datetime.fromisoformat(norm).timestamp()
    except Exception:
        return 0.0


def deduplicate_and_sort(old_data, new_data, limit_count=50, sort_field="fecha_iso"):
    clean_old = [d for d in old_data if not d.get("demo", False)]
    seen_urls = set()
    combined = []

    for item in list(new_data) + clean_old:
        item.pop("demo", None)
        url = item.get("url")
        if url not in seen_urls:
            seen_urls.add(url)
            combined.append(item)

    combined.sort(key=lambda x: _parse_iso_timestamp(x.get(sort_field, "")), reverse=True)
    return combined[:limit_count]


def generate_summary_with_gemini(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not (HAS_GENAI and text and api_key):
        return text
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Resume esta noticia en una sola frase corta (máximo 150 caracteres), directo al grano sin mencionar que es un resumen:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else text
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return text


def should_update(estado, name, freq_hours, force):
    if force:
        return True
    last_update_str = estado.get(name, {}).get("last_success")
    if not last_update_str:
        return True
    ts = _parse_iso_timestamp(last_update_str)
    if ts <= 0:
        return True
    last_update = datetime.fromtimestamp(ts, tz=timezone.utc)
    return (datetime.now(timezone.utc) - last_update) > timedelta(hours=freq_hours)


def print_sample(name, data):
    if not data:
        print(f"Muestra de {name}: Vacio")
        return
    print(f"Muestra de {name}: {json.dumps(data[0], ensure_ascii=False, indent=2)}")


def get_now_utc_str():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _summarize_noticias_if_enabled(nuevas: list):
    if not (os.getenv("GEMINI_API_KEY") and HAS_GENAI):
        return
    print("Usando Gemini para resumir noticias nuevas...")
    for n in nuevas:
        if len(n.get("resumen", "")) > 100:
            n["resumen"] = generate_summary_with_gemini(n["resumen"])


def _update_standard_feed(estado_fuentes: dict, key: str, filename: str, fetcher, freq_hours: int, force: bool, limit_count: int = 50, post_process=None):
    if not should_update(estado_fuentes, key, freq_hours, force):
        print(f"\n[{key}] No requiere actualización aún.")
        return

    print(f"\n[{key}] Actualizando {filename}...")
    nuevas, errores = fetcher(timeout_red=TIMEOUT_RED)
    if not nuevas:
        print(f"-> Falló la recolección de {key}. Se conservan datos anteriores.")
        estado_fuentes.setdefault(key, {})["errores_recientes"] = errores
        return

    if post_process:
        post_process(nuevas)

    final = deduplicate_and_sort(load_json(filename), nuevas, limit_count=limit_count, sort_field="fecha_iso")
    save_json(final, filename)
    estado_fuentes[key] = {
        "last_success": get_now_utc_str(),
        "items": len(nuevas),
        "errores": errores,
    }
    print(f"-> {key} actualizado: {len(nuevas)} nuevos obtenidos. Errores: {len(errores)}")
    print_sample(filename, final)


def _update_ckan_feed(estado_fuentes: dict, force: bool):
    if not should_update(estado_fuentes, "ckan", 6, force):
        print("\n[ckan] No requiere actualización aún.")
        return

    print("\n[ckan] Actualizando CKAN...")
    nuevas, desc_ckan = fetch_ckan(timeout_red=TIMEOUT_RED)
    portales_ckan, errores_ckan_list = desc_ckan if isinstance(desc_ckan, tuple) else ({}, list(desc_ckan))

    if nuevas:
        final = deduplicate_and_sort(load_json("ckan.json"), nuevas, sort_field="fecha_modificacion_iso")
        save_json(final, "ckan.json")
        estado_fuentes["ckan"] = {
            "last_success": get_now_utc_str(),
            "items": len(nuevas),
            "portales": portales_ckan,
            "errores": errores_ckan_list,
        }
        print_sample("ckan.json", final)
    else:
        print("-> CKAN sin datos en vivo disponibles. Escribiendo lista vacía en ckan.json.")
        save_json([], "ckan.json")
        estado_fuentes["ckan"] = {
            "items": 0,
            "portales": portales_ckan,
            "errores_recientes": errores_ckan_list,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forzar", action="store_true", help="Ignorar frecuencias y forzar actualización")
    args = parser.parse_args()

    estado = load_json("estado.json")
    if not isinstance(estado, dict):
        estado = {}
    estado_fuentes = estado.setdefault("fuentes", {})

    print("Iniciando actualización de datos...")
    _update_standard_feed(estado_fuentes, "noticias", "noticias.json", fetch_noticias, 3, args.forzar, post_process=_summarize_noticias_if_enabled)
    _update_standard_feed(estado_fuentes, "normas", "normas.json", fetch_normas, 3, args.forzar)
    _update_ckan_feed(estado_fuentes, args.forzar)
    _update_standard_feed(estado_fuentes, "academico", "academico.json", fetch_academico, 24, args.forzar, limit_count=50)
    _update_standard_feed(estado_fuentes, "polity", "polity_alertas.json", fetch_polity_alertas, 12, args.forzar, limit_count=50)
    _update_standard_feed(estado_fuentes, "eventos", "eventos_alertas.json", fetch_eventos_alertas, 24, args.forzar, limit_count=30)

    estado["last_run"] = get_now_utc_str()
    save_json(estado, "estado.json")
    print("\nActualización completada.")


if __name__ == "__main__":
    main()
