import json
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse
import urllib.robotparser
import requests

USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"
HEADERS = {"User-Agent": USER_AGENT}
WAF_TERMS = ("cloudwaf", "imperva", "incapsula", "cloudflare ray id", "challenge-platform", "access denied", "waf")


def load_manual_verified() -> dict:
    path = os.path.join("data", "links_verificados_manual.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("verificados", {})
    except Exception as e:
        print(f"Aviso: no se pudo cargar {path}: {e}")
        return {}


def is_manually_verified(url: str, manual_dict: dict) -> bool:
    if not url:
        return False
    u_clean = url.strip().rstrip("/")
    return any(m_url.strip().rstrip("/") == u_clean for m_url in manual_dict)


def _extract_flat_file(rel_path: str, title_key: str, url_key: str) -> list:
    if not os.path.exists(rel_path):
        return []
    with open(rel_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        {
            "archivo": rel_path.replace("\\", "/"),
            "id": x.get("id", ""),
            "titulo": x.get(title_key, ""),
            "url": x.get(url_key, "").strip() if x.get(url_key) else None,
        }
        for x in data
    ]


def _extract_nested_file(rel_path: str, child_keys: tuple) -> list:
    if not os.path.exists(rel_path):
        return []
    with open(rel_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for sub in data:
        for k in child_keys:
            for c in sub.get(k, []):
                raw_u = c.get("url")
                items.append({
                    "archivo": rel_path.replace("\\", "/"),
                    "id": c.get("id", ""),
                    "titulo": c.get("titulo", ""),
                    "url": raw_u.strip() if raw_u else None,
                })
    return items


def load_all_urls() -> list:
    items = []
    items.extend(_extract_flat_file(os.path.join("data", "fuentes.json"), "nombre", "url"))
    items.extend(_extract_flat_file(os.path.join("data", "eventos.json"), "titulo", "enlace"))
    items.extend(_extract_nested_file(os.path.join("data", "polity.json"), ("tarjetas",)))
    items.extend(_extract_nested_file(os.path.join("data", "estudiantes.json"), ("tarjetas", "apuntes")))
    items.extend(_extract_flat_file(os.path.join("data", "cursos.json"), "nombre", "url"))
    items.extend(_extract_flat_file(os.path.join("data", "becas.json"), "nombre", "url"))
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
        elapsed_global = time.time() - self.last_global_req_time
        if elapsed_global < 1.0:
            time.sleep(1.0 - elapsed_global)
        if has_crawl_delay:
            elapsed_dom = time.time() - self.last_domain_req_time.get(netloc, 0.0)
            if elapsed_dom < 10.0:
                time.sleep(10.0 - elapsed_dom)
        t = time.time()
        self.last_global_req_time = t
        self.last_domain_req_time[netloc] = t

    def get_robots_info(self, scheme, netloc):
        if netloc in self.robots_cache:
            return self.robots_cache[netloc]
        rp = urllib.robotparser.RobotFileParser()
        has_crawl_delay = False
        try:
            self._wait_rate_limits(netloc, has_crawl_delay=False)
            r = self.session.get(f"{scheme}://{netloc}/robots.txt", timeout=10)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
                delay = rp.crawl_delay("ApocunaBot") or rp.crawl_delay("*")
                has_crawl_delay = bool(delay and delay > 0)
            else:
                rp.allow_all = True
        except Exception:
            rp.allow_all = True
        info = {"parser": rp, "has_crawl_delay": has_crawl_delay}
        self.robots_cache[netloc] = info
        return info

    def _classify_response(self, resp, raw_url: str, is_manual: bool) -> tuple[str, int | str]:
        code = resp.status_code
        if code in (401, 403, 418, 429):
            return ("ok (verificado a mano)" if is_manual else "bloquea bots"), code
        text_lower = resp.text[:1000].lower()
        if any(t in text_lower for t in WAF_TERMS) and (code != 200 or "captcha" in text_lower or "waf" in text_lower):
            return ("ok (verificado a mano)" if is_manual else "bloquea bots"), f"{code} (WAF / Challenge detectado)"
        if code in (404, 410):
            return "roto", code
        if code >= 500:
            return ("ok (verificado a mano)" if is_manual else "sin conexión"), code
        if code == 200:
            is_redir = len(resp.history) > 0 and resp.url.rstrip("/") != raw_url.rstrip("/")
            return ("redirige" if is_redir else "ok"), code
        return ("ok (verificado a mano)" if is_manual else "roto"), code

    def _classify_exception(self, exc: Exception, is_manual: bool) -> tuple[str, str]:
        if isinstance(exc, requests.exceptions.Timeout):
            return ("ok (verificado a mano)" if is_manual else "sin conexión"), "timeout (15s)"
        err_str = str(exc).lower()
        if "name or service not known" in err_str or "getaddrinfo failed" in err_str:
            return "roto", "error DNS"
        if "connection refused" in err_str:
            return ("ok (verificado a mano)" if is_manual else "roto"), "conexión rechazada"
        return ("ok (verificado a mano)" if is_manual else "sin conexión"), f"error: {type(exc).__name__}"

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
            "fecha_utc": now_utc,
        }
        if not raw_url:
            base_res.update({"estado": "demo (sin url)", "codigo": "N/A"})
            return base_res
        if not raw_url.startswith("http"):
            base_res.update({"estado": "roto", "codigo": "URL inválida"})
            return base_res

        is_manual = is_manually_verified(raw_url, self.manual_dict)
        parsed = urlparse(raw_url)
        robots_info = self.get_robots_info(parsed.scheme or "https", parsed.netloc)
        try:
            can_fetch = robots_info["parser"].can_fetch("ApocunaBot", raw_url)
        except Exception:
            can_fetch = True
        if not can_fetch:
            base_res.update({"codigo": "bloqueado por robots.txt", "estado": "ok (verificado a mano)" if is_manual else "bloquea bots"})
            return base_res

        self._wait_rate_limits(parsed.netloc, has_crawl_delay=robots_info["has_crawl_delay"])
        try:
            resp = self.session.get(raw_url, timeout=15, allow_redirects=True)
            base_res["url_final"] = resp.url
            base_res["estado"], base_res["codigo"] = self._classify_response(resp, raw_url, is_manual)
        except Exception as exc:
            base_res["estado"], base_res["codigo"] = self._classify_exception(exc, is_manual)
        return base_res


def _interleave_by_domain(items: list) -> list:
    por_dominio = defaultdict(list)
    for it in items:
        u = it["url"]
        dom = urlparse(u).netloc if (u and u.startswith("http")) else "nohost"
        por_dominio[dom].append(it)
    ordered = []
    while any(por_dominio.values()):
        for dom in list(por_dominio.keys()):
            if por_dominio[dom]:
                ordered.append(por_dominio[dom].pop(0))
            else:
                del por_dominio[dom]
    return ordered


def main():
    print("=== Iniciando Verificación de Links (ApocunaBot) ===")
    manual_dict = load_manual_verified()
    ordered_items = _interleave_by_domain(load_all_urls())
    checker = LinkChecker(manual_dict=manual_dict)
    resultados = []

    for i, it in enumerate(ordered_items, 1):
        res = checker.check_url(it)
        print(f"[{i}/{len(ordered_items)}] {it['archivo']}:{it['id']} -> {res['estado']} ({res['codigo']})")
        resultados.append(res)

    out_dir = os.path.join("data", "generated")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "reporte_links.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    for k, v in Counter(r["estado"] for r in resultados).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
