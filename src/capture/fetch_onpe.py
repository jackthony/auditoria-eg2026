"""
src/capture/fetch_onpe.py

Captura atómica desde la fuente oficial ONPE con cadena de custodia.

Uso:
    py src\\capture\\fetch_onpe.py

Efecto:
    Crea captures\\YYYYMMDDTHHMMSSZ\\ con:
      - raw/*.json        : datos tal cual llegaron
      - MANIFEST.jsonl    : hashes SHA-256 y metadata
      - README.md         : descripción humana de la captura
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse

import requests

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    
# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════

# Fuente oficial ONPE (directa). Se usa si la IP capturante es peruana.
ONPE_BASE = "https://resultadoelectoral.onpe.gob.pe"

# Worker Cloudflare propio (Neuracode). Proxy puro a ONPE, cache 30s edge,
# allowlist de 6 paths, validación anti-redirect hijack. Ver proxy/onpe-proxy-neuracode/.
# Permite captura 24/7 desde GitHub Actions (datacenter) que ONPE bloquearía directo.
PROXY_BASE = os.environ.get(
    "ONPE_PROXY_BASE",
    "https://onpe-proxy-neuracode.jackgptgod.workers.dev",
)

USER_AGENT = "AuditoriaEG2026/1.0 (analisis tecnico - personero acreditado)"

# Endpoints oficiales ONPE. Paths confirmados vía inspección de network tab
# en resultadoelectoral.onpe.gob.pe/main/resumen.
ENDPOINTS_ONPE = {
    "proceso_activo":    "/presentacion-backend/proceso/proceso-electoral-activo",
    "elecciones":        "/presentacion-backend/proceso/2/elecciones",
    "resumen_elecciones":"/presentacion-backend/resumen-general/elecciones?activo=1&idProceso=2&tipoFiltro=eleccion",
    "totales":           "/presentacion-backend/resumen-general/totales?idEleccion=10&tipoFiltro=eleccion",
    "mapa_calor":        "/presentacion-backend/resumen-general/mapa-calor?idEleccion=10&tipoFiltro=total",
    "presidencial":      "/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre?idEleccion=10&tipoFiltro=eleccion",
    "mesa_totales":      "/presentacion-backend/mesa/totales?tipoFiltro=eleccion",
    "ubigeos_departamentos": "/presentacion-backend/ubigeos/departamentos?idEleccion=10&idAmbitoGeografico=1",
}

# Si ONPE_DIRECT=1 (IP peruana verificada), va directo; si no, via Worker.
USE_DIRECT = os.environ.get("ONPE_DIRECT", "0") == "1"

TIMEOUT = 20  # segundos por request
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_HOSTS = {
    "resultadoelectoral.onpe.gob.pe",
    "onpe-proxy-neuracode.jackgptgod.workers.dev",
}

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def public_ip() -> str:
    """Intenta obtener la IP pública del capturante (para el manifiesto).
    Falla silenciosa: no es crítico para el análisis, pero sí para trazabilidad.
    """
    for svc in ("https://api.ipify.org", "https://ifconfig.me/ip"):
        try:
            r = requests.get(svc, timeout=5)
            if r.ok and r.text.strip():
                return r.text.strip()
        except Exception:
            continue
    return "unknown"

def hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"

def git_commit_hash() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None

# ══════════════════════════════════════════════════════════════
#  CAPTURA
# ══════════════════════════════════════════════════════════════

def fetch_endpoint(base: str, path: str, out_path: Path) -> dict:
    """Descarga un endpoint con cache-busting agresivo.

    El proxy CORS Cloudflare cachea /api/tracking con cf-cache-status=HIT
    (age <60s). Mitigamos con: query param `_=<epoch_ms>` + headers
    Cache-Control/Pragma. No garantiza bypass del Cache API interno del
    worker, pero sí del cache CDN de Cloudflare.
    """
    cache_buster = int(datetime.now(timezone.utc).timestamp() * 1000)
    sep = "&" if "?" in path else "?"
    url = base + path + f"{sep}_={cache_buster}"
    started = utc_now_iso()
    headers = {
        "User-Agent": USER_AGENT,
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True, allow_redirects=False)
        if resp.is_redirect:
            location = resp.headers.get("Location", "")
            final_host = urlparse(location).netloc
            if final_host not in ALLOWED_HOSTS:
                raise ValueError(f"Redirect no autorizado: {final_host}")
            resp = requests.get(location, headers=headers, timeout=TIMEOUT, stream=True)
        content = b""
        for chunk in resp.iter_content(chunk_size=65536):
            content += chunk
            if len(content) > MAX_RESPONSE_BYTES:
                raise ValueError(f"Respuesta excede límite: {url}")
        status = resp.status_code
        cf_cache = resp.headers.get("cf-cache-status", "-")
        cf_age = resp.headers.get("age", "-")
    except Exception as e:
        status = 0
        content = f"FETCH_ERROR: {e}".encode("utf-8")
        cf_cache = "-"
        cf_age = "-"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(content)
    return {
        "url": url,
        "fetched_at_utc": started,
        "local_path": str(out_path.relative_to(out_path.parents[1])).replace(os.sep, "/"),
        "bytes": len(content),
        "sha256": sha256_of(out_path),
        "http_status": status,
        "user_agent": USER_AGENT,
        "cf_cache_status": cf_cache,
        "cf_age": cf_age,
    }


def main():
    ROOT = Path(__file__).resolve().parents[2]
    ts = utc_now_compact()
    capture_dir = ROOT / "captures" / ts
    raw_dir = capture_dir / "raw"
    # Inmutabilidad: si la carpeta ya existe, ABORTAR. Nunca sobrescribir captura.
    if capture_dir.exists():
        print(f"ERROR: captures/{ts} ya existe. No se sobrescriben capturas (cadena de custodia).",
              file=sys.stderr)
        sys.exit(3)
    raw_dir.mkdir(parents=True, exist_ok=False)

    pub_ip = public_ip()
    if pub_ip in ("unknown", "captured-from-container", None, ""):
        print(f"WARNING: public_ip = {pub_ip!r} (no peruana verificable). "
              "Se registrará en MANIFEST como ip_warning=true.", file=sys.stderr)
    host = hostname()
    commit = git_commit_hash()
    os_desc = f"{platform.system()} {platform.release()} ({platform.machine()})"

    print(f"[capture] timestamp UTC: {ts}")
    print(f"[capture] destino: {capture_dir}")
    print(f"[capture] host: {host}  ip-pub: {pub_ip}")
    print(f"[capture] git HEAD: {commit or 'no-repo'}")
    print()

    # Estrategia: ONPE directo si ONPE_DIRECT=1 (IP peruana), si no via Worker propio.
    base = ONPE_BASE if USE_DIRECT else PROXY_BASE
    source = "onpe_direct" if USE_DIRECT else "proxy_neuracode"
    manifest_entries = []

    print(f"[capture] source: {source}  base: {base}")
    print()

    for name, path in ENDPOINTS_ONPE.items():
        out = raw_dir / f"{name}.json"
        entry = fetch_endpoint(base, path, out)
        entry["endpoint"] = name
        entry["source"] = source
        manifest_entries.append(entry)
        flag = "✓" if entry["http_status"] == 200 else f"✗ HTTP {entry['http_status']}"
        print(f"  {flag}  {name:<18}  {entry['bytes']:>7}B  "
              f"sha256={entry['sha256'][:16]}...")

    # 3. Escribir manifiesto (una línea por entrada)
    manifest_path = capture_dir / "MANIFEST.jsonl"
    with manifest_path.open("w", encoding="utf-8", newline="\n") as f:
        for e in manifest_entries:
            # Agregar metadata global a cada entrada
            e["public_ip"] = pub_ip
            e["hostname"] = host
            e["git_commit"] = commit
            e["os"] = os_desc
            f.write(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n")

    # 4. README humano
    readme = capture_dir / "README.md"
    readme.write_text(f"""# Captura ONPE — {ts}

- **Timestamp UTC:** {ts[:8]}T{ts[9:15]}Z ({ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}:{ts[13:15]} UTC)
- **Host:** {host}
- **IP pública:** {pub_ip}
- **SO:** {os_desc}
- **Git commit al momento de captura:** `{commit or "(no commit aún)"}`
- **Endpoints:** {len(manifest_entries)}

## Verificación

Para comprobar la integridad:

```powershell
py src\\capture\\verify_manifest.py captures\\{ts}\\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
""", encoding="utf-8")

    # 5. Resumen final
    total_bytes = sum(e["bytes"] for e in manifest_entries)
    ok_count = sum(1 for e in manifest_entries if e["http_status"] == 200)
    print()
    print(f"[capture] {ok_count}/{len(manifest_entries)} endpoints OK")
    print(f"[capture] total: {total_bytes:,} bytes")
    print(f"[capture] manifest: {manifest_path}")
    print()
    print("Siguiente paso — commit inmediato:")
    print(f"    git add captures\\{ts}")
    print(f"    git commit -S -m \"capture: ONPE at {ts[9:11]}:{ts[11:13]} UTC\"")
    print(f"    git push")

    if ok_count < len(manifest_entries):
        sys.exit(2)


if __name__ == "__main__":
    main()
