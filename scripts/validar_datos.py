import json
import os
import sys

def validar_json(file_path, required_fields):
    if not os.path.exists(file_path):
        print(f"ERROR: No se encontró {file_path}")
        return False
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"Validando {file_path} ({len(data)} registros)...")
        for idx, item in enumerate(data):
            for field in required_fields:
                if field not in item:
                    print(f"ERROR en registro {idx} (ID: {item.get('id', '?')}): Falta el campo '{field}'")
                    return False
                    
            if "url" in item and "google.com/search" in item["url"]:
                print(f"ERROR en registro {idx}: URL contiene google.com/search: {item['url']}")
                return False
                
            if "enlace" in item and "google.com/search" in item["enlace"]:
                print(f"ERROR en registro {idx}: Enlace contiene google.com/search: {item['enlace']}")
                return False
                
        print(f"OK: {file_path} es válido.")
        return True
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        return False

def main():
    success = True
    print("Iniciando validación de datos...")
    
    # Validar fuentes
    success &= validar_json(
        os.path.join("data", "fuentes.json"), 
        ["id", "bloque", "nombre", "institucion", "descripcion_corta", "url", "tipo"]
    )
    
    # Validar eventos
    success &= validar_json(
        os.path.join("data", "eventos.json"), 
        ["id", "tipo", "titulo", "tematica", "fecha_limite", "enlace", "descripcion"]
    )
    
    # Validar noticias
    success &= validar_json(
        os.path.join("data", "generated", "noticias.json"),
        ["id", "titulo", "fuente", "categoria", "fecha_iso", "url", "resumen", "demo"]
    )
    
    # Validar normas
    success &= validar_json(
        os.path.join("data", "generated", "normas.json"),
        ["id", "titulo", "tipo_norma", "entidad", "fecha_iso", "url", "grupo", "demo"]
    )
    
    # Validar ckan
    success &= validar_json(
        os.path.join("data", "generated", "ckan.json"),
        ["id", "titulo", "portal", "fecha_modificacion_iso", "url", "demo"]
    )
    
    # Validar polity
    polity_path = os.path.join("data", "polity.json")
    if os.path.exists(polity_path):
        with open(polity_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
            print(f"Validando {polity_path} ({len(p_data)} subsecciones)...")
            for sub in p_data:
                for card in sub.get("tarjetas", []):
                    for field in ["id", "titulo", "descripcion", "frecuencia", "fuente", "url"]:
                        if field not in card:
                            print(f"ERROR en tarjeta {card.get('id', '?')}: Falta el campo '{field}'")
                            success = False
                    if "url" in card and "google.com/search" in card["url"]:
                        print(f"ERROR en tarjeta: URL contiene google.com/search: {card['url']}")
                        success = False
            print(f"OK: {polity_path} es válido.")
            
    # Validar estudiantes
    est_path = os.path.join("data", "estudiantes.json")
    if os.path.exists(est_path):
        with open(est_path, "r", encoding="utf-8") as f:
            e_data = json.load(f)
            print(f"Validando {est_path} ({len(e_data)} subsecciones)...")
            for sub in e_data:
                for card in sub.get("tarjetas", []):
                    for field in ["id", "titulo", "descripcion", "fuente", "frecuencia", "url"]:
                        if field not in card:
                            print(f"ERROR en tarjeta {card.get('id', '?')}: Falta el campo '{field}'")
                            success = False
                    if "url" in card and "google.com/search" in card["url"]:
                        print(f"ERROR en tarjeta: URL contiene google.com/search: {card['url']}")
                        success = False
                for apunte in sub.get("apuntes", []):
                    for field in ["id", "sistema", "curso", "titulo", "resumen", "normativa", "url"]:
                        if field not in apunte:
                            print(f"ERROR en apunte {apunte.get('id', '?')}: Falta el campo '{field}'")
                            success = False
                    if "url" in apunte and "google.com/search" in apunte["url"]:
                        print(f"ERROR en apunte: URL contiene google.com/search: {apunte['url']}")
                        success = False
            print(f"OK: {est_path} es válido.")
    
    if success:
        print("Todas las validaciones pasaron correctamente.")
        sys.exit(0)
    else:
        print("Fallaron algunas validaciones.")
        sys.exit(1)

if __name__ == "__main__":
    main()
