import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import urllib.robotparser
import requests

USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"
HEADERS = {"User-Agent": USER_AGENT}

def load_manual_verified():
    path = os.path.join("data", "links_verificados_manual.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("verificados", {})
        except Exception as e:
            print(f"Aviso: no se pudo cargar {path}: {e}")
    return {}

def is_manually_verified(url, manual_dict):
    if not url:
        return False
    u_clean = url.strip().rstrip("/")
    for m_url in manual_dict:
        if m_url.strip().rstrip("/") == u_clean:
            return True
    return False

def load_all_urls():
    items = []
    
    # 1. data/fuentes.json
    f_path = os.path.join("data", "fuentes.json")
    if os.path.exists(f_path):
        with open(f_path, "r", encoding="utf-8") as f:
            fuentes = json.load(f)
            for x in fuentes:
                raw_u = x.get("url")
                items.append({
                    "archivo": "data/fuentes.json",
                    "id": x.get("id", ""),
                    "titulo": x.get("nombre", ""),
                    "url": raw_u.strip() if raw_u else None
                })
                
    # 2. data/eventos.json
    e_path = os.path.join("data", "eventos.json")
    if os.path.exists(e_path):
        with open(e_path, "r", encoding="utf-8") as f:
            eventos = json.load(f)
            for x in eventos:
                raw_u = x.get("enlace")
                items.append({
                    "archivo": "data/eventos.json",
                    "id": x.get("id", ""),
                    "titulo": x.get("titulo", ""),
                    "url": raw_u.strip() if raw_u else None
                })
                
    # 3. data/polity.json
    p_path = os.path.join("data", "polity.json")
    if os.path.exists(p_path):
        with open(p_path, "r", encoding="utf-8") as f:
            polity = json.load(f)
            for sub in polity:
                for c in sub.get("tarjetas", []):
                    raw_u = c.get("url")
                    items.append({
                        "archivo": "data/polity.json",
                        "id": c.get("id", ""),
                        "titulo": c.get("titulo", ""),
                        "url": raw_u.strip() if raw_u else None
                    })

    # 4. data/estudiantes.json
    est_path = os.path.join("data", "estudiantes.json")
    if os.path.exists(est_path):
        with open(est_path, "r", encoding="utf-8") as f:
            est = json.load(f)
            for sub in est:
                for c in sub.get("tarjetas", []):
                    raw_u = c.get("url")
                    items.append({
                        "archivo": "data/estudiantes.json",
                        "id": c.get("id", ""),
                        "titulo": c.get("titulo", ""),
                        "url": raw_u.strip() if raw_u else None
                    })
                for a in sub.get("apuntes", []):
                    raw_u = a.get("url")
                    items.append({
                        "archivo": "data/estudiantes.json",
                        "id": a.get("id", ""),
                        "titulo": a.get("titulo", ""),
                        "url": raw_u.strip() if raw_u else None
                    })
                    
    return items

class LinkChecker:
    def __init__(self, manual_dict=None):
        self.robots_cache = {}
        self.last_global_req_time = 0.0
        self.last_domain_req_time = {}
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.manual_dict = manual_dict or {}
        
    def _wait_rate_limits(self, netloc, has_crawl_delay):
        now = time.time()
        
        # 1. Al menos 1 segundo entre cualquier petición
        elapsed_global = now - self.last_global_req_time
        if elapsed_global < 1.0:
            time.sleep(1.0 - elapsed_global)
            
        # 2. Si tiene Crawl-delay en robots.txt, al menos 10 segundos para el mismo dominio
        if has_crawl_delay:
            last_dom = self.last_domain_req_time.get(netloc, 0.0)
            elapsed_dom = time.time() - last_dom
            if elapsed_dom < 10.0:
                wait_time = 10.0 - elapsed_dom
                print(f"   [RateLimit] Esperando {wait_time:.1f}s por Crawl-delay en {netloc}...")
                time.sleep(wait_time)
                
        t = time.time()
        self.last_global_req_time = t
        self.last_domain_req_time[netloc] = t

    def get_robots_info(self, scheme, netloc):
        if netloc in self.robots_cache:
            return self.robots_cache[netloc]
            
        rp = urllib.robotparser.RobotFileParser()
        robots_url = f"{scheme}://{netloc}/robots.txt"
        has_crawl_delay = False
        
        try:
            self._wait_rate_limits(netloc, has_crawl_delay=False)
            r = self.session.get(robots_url, timeout=10)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
                delay = rp.crawl_delay("ApocunaBot") or rp.crawl_delay("*")
                if delay and delay > 0:
                    has_crawl_delay = True
            else:
                rp.allow_all = True
        except Exception:
            rp.allow_all = True
            
        info = {
            "parser": rp,
            "has_crawl_delay": has_crawl_delay
        }
        self.robots_cache[netloc] = info
        return info

    def check_url(self, item):
        raw_url = item["url"]
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        base_res = {
            "archivo": item["archivo"],
            "id": item["id"],
            "titulo": item["titulo"],
            "url": raw_url,
            "estado": "",
            "codigo": None,
            "url_final": None,
            "fecha_utc": now_utc
        }
        
        # 1. Caso: URL nula o vacía (tarjetas demo)
        if raw_url is None or raw_url == "":
            base_res["estado"] = "demo (sin url)"
            base_res["codigo"] = "N/A"
            return base_res
            
        # 2. Caso: marcador de posición (#)
        if raw_url == "#":
            base_res["estado"] = "roto"
            base_res["codigo"] = "placeholder (#)"
            return base_res
            
        # 3. Caso: URL no HTTP/HTTPS
        if not raw_url.startswith("http"):
            base_res["estado"] = "roto"
            base_res["codigo"] = "URL inválida (no http)"
            return base_res
            
        is_manual = is_manually_verified(raw_url, self.manual_dict)
        parsed = urlparse(raw_url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc
        
        # Comprobar robots.txt
        robots_info = self.get_robots_info(scheme, netloc)
        rp = robots_info["parser"]
        has_crawl_delay = robots_info["has_crawl_delay"]
        
        try:
            can_fetch = rp.can_fetch("ApocunaBot", raw_url)
        except Exception:
            can_fetch = True
            
        if not can_fetch:
            base_res["codigo"] = "bloqueado por robots.txt"
            base_res["estado"] = "ok (verificado a mano)" if is_manual else "bloquea bots"
            return base_res
            
        # Petición GET con timeout de 15 segundos
        self._wait_rate_limits(netloc, has_crawl_delay=has_crawl_delay)
        
        try:
            resp = self.session.get(raw_url, timeout=15, allow_redirects=True)
            status_code = resp.status_code
            final_url = resp.url
            base_res["codigo"] = status_code
            base_res["url_final"] = final_url
            
            # WAF checks o bloqueos de bots
            if status_code in (401, 403, 418, 429):
                base_res["estado"] = "ok (verificado a mano)" if is_manual else "bloquea bots"
                return base_res
                
            # WAF en página de éxito (CloudWAF, Incapsula, Cloudflare challenge)
            text_lower = resp.text[:1000].lower()
            if any(term in text_lower for term in ["cloudwaf", "imperva", "incapsula", "cloudflare ray id", "challenge-platform", "access denied", "waf"]):
                if status_code != 200 or "captcha" in text_lower or "waf" in text_lower:
                    base_res["codigo"] = f"{status_code} (WAF / Challenge detectado)"
                    base_res["estado"] = "ok (verificado a mano)" if is_manual else "bloquea bots"
                    return base_res
                    
            if status_code in (404, 410):
                base_res["estado"] = "roto"
                return base_res
                
            if status_code >= 500:
                base_res["estado"] = "ok (verificado a mano)" if is_manual else "sin conexión"
                return base_res
                
            if status_code == 200:
                if len(resp.history) > 0 and final_url.rstrip("/") != raw_url.rstrip("/"):
                    base_res["estado"] = "redirige"
                else:
                    base_res["estado"] = "ok"
                return base_res
                
            # Otros códigos
            base_res["estado"] = "ok (verificado a mano)" if is_manual else "roto"
            return base_res
            
        except requests.exceptions.Timeout:
            base_res["codigo"] = "timeout (15s)"
            base_res["estado"] = "ok (verificado a mano)" if is_manual else "sin conexión"
            return base_res
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            err_str = str(e).lower()
            if "name or service not known" in err_str or "getaddrinfo failed" in err_str:
                base_res["estado"] = "roto"
                base_res["codigo"] = "error DNS"
            elif "connection refused" in err_str:
                base_res["codigo"] = "conexión rechazada"
                base_res["estado"] = "ok (verificado a mano)" if is_manual else "roto"
            else:
                base_res["codigo"] = "error de conexión"
                base_res["estado"] = "ok (verificado a mano)" if is_manual else "sin conexión"
            return base_res
        except Exception as e:
            base_res["codigo"] = f"error: {type(e).__name__}"
            base_res["estado"] = "ok (verificado a mano)" if is_manual else "sin conexión"
            return base_res

def main():
    print("=== Iniciando Verificación de Links (ApocunaBot) ===")
    manual_dict = load_manual_verified()
    print(f"Cargadas {len(manual_dict)} URLs verificadas manualmente por el usuario.")
    
    items = load_all_urls()
    print(f"Total de registros a evaluar: {len(items)}")
    
    checker = LinkChecker(manual_dict=manual_dict)
    resultados = []
    
    from collections import defaultdict
    por_dominio = defaultdict(list)
    for it in items:
        u = it["url"]
        dom = urlparse(u).netloc if (u and u.startswith("http")) else "nohost"
        por_dominio[dom].append(it)
        
    ordered_items = []
    while any(por_dominio.values()):
        for dom in list(por_dominio.keys()):
            if por_dominio[dom]:
                ordered_items.append(por_dominio[dom].pop(0))
            else:
                del por_dominio[dom]
                
    for i, it in enumerate(ordered_items, 1):
        url_disp = it['url'] if it['url'] else "(sin url - demo)"
        print(f"[{i}/{len(ordered_items)}] Verificando ({it['archivo']}:{it['id']}): {url_disp[:60]}...")
        res = checker.check_url(it)
        print(f"   -> Estado: {res['estado']} | Código: {res['codigo']} | Final: {res['url_final']}")
        resultados.append(res)
        
    out_dir = os.path.join("data", "generated")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "reporte_links.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
        
    print(f"\nReporte guardado exitosamente en: {out_file}")
    
    from collections import Counter
    conteos = Counter(r["estado"] for r in resultados)
    print("\nResumen de estados:")
    for k, v in conteos.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
