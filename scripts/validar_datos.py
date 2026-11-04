import json
import os
import sys


def _check_item_fields(item: dict, required_fields: list, label: str) -> bool:
    for field in required_fields:
        if field not in item:
            print(f"ERROR en {label} (ID: {item.get('id', '?')}): Falta el campo '{field}'")
            return False
    for url_key in ("url", "enlace"):
        val = item.get(url_key)
        if val and "google.com/search" in val:
            print(f"ERROR en {label}: {url_key} contiene google.com/search: {val}")
            return False
    return True


def validar_json(file_path: str, required_fields: list) -> bool:
    if not os.path.exists(file_path):
        print(f"ERROR: No se encontró {file_path}")
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Validando {file_path} ({len(data)} registros)...")
        for idx, item in enumerate(data):
            if not _check_item_fields(item, required_fields, f"registro {idx}"):
                return False
        print(f"OK: {file_path} es válido.")
        return True
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        return False


def validar_nested_json(file_path: str, sub_checks: list[tuple[str, list]]) -> bool:
    if not os.path.exists(file_path):
        return True
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Validando {file_path} ({len(data)} subsecciones)...")
        ok = True
        for sub in data:
            for key_list, req_fields in sub_checks:
                for item in sub.get(key_list, []):
                    ok &= _check_item_fields(item, req_fields, key_list[:-1])
        if ok:
            print(f"OK: {file_path} es válido.")
        return ok
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        return False


def main():
    print("Iniciando validación de datos...")
    checks = [
        (os.path.join("data", "fuentes.json"), ["id", "bloque", "nombre", "institucion", "descripcion_corta", "url", "tipo"]),
        (os.path.join("data", "eventos.json"), ["id", "tipo", "titulo", "tematica", "fecha_limite", "enlace", "descripcion"]),
        (os.path.join("data", "generated", "noticias.json"), ["id", "titulo", "fuente", "categoria", "fecha_iso", "url", "resumen"]),
        (os.path.join("data", "generated", "normas.json"), ["id", "titulo", "tipo_norma", "entidad", "fecha_iso", "url", "grupo"]),
        (os.path.join("data", "generated", "ckan.json"), ["id", "titulo", "portal", "fecha_modificacion_iso", "url"]),
    ]

    success = all(validar_json(path, fields) for path, fields in checks)
    success &= validar_nested_json(
        os.path.join("data", "polity.json"),
        [("tarjetas", ["id", "titulo", "descripcion", "frecuencia", "fuente", "url"])]
    )
    success &= validar_nested_json(
        os.path.join("data", "estudiantes.json"),
        [
            ("tarjetas", ["id", "titulo", "descripcion", "fuente", "frecuencia", "url"]),
            ("apuntes", ["id", "sistema", "curso", "titulo", "resumen", "normativa", "url"]),
        ]
    )

    if success:
        print("Todas las validaciones pasaron correctamente.")
        sys.exit(0)
    print("Fallaron algunas validaciones.")
    sys.exit(1)


if __name__ == "__main__":
    main()
