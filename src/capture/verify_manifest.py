"""
src/capture/verify_manifest.py

Verifica la integridad de una captura ONPE recalculando los hashes.

Uso:
    py src\\capture\\verify_manifest.py captures\\20260417T062711Z\\

Exit codes:
    0  todos los archivos coinciden con el manifiesto
    1  al menos un archivo no coincide (modificación posterior a captura)
    2  error en el input (ruta inexistente, manifiesto inválido)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(capture_dir: Path) -> int:
    manifest = capture_dir / "MANIFEST.jsonl"
    if not manifest.exists():
        print(f"ERROR: manifiesto no encontrado: {manifest}", file=sys.stderr)
        return 2

    total = 0
    ok = 0
    fails = []

    with manifest.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"ERROR: manifest línea {lineno} inválida: {e}", file=sys.stderr)
                return 2

            total += 1
            local = capture_dir / entry["local_path"]
            expected = entry["sha256"]

            if not local.exists():
                fails.append((entry["endpoint"], "MISSING", expected, "—"))
                continue

            actual = sha256_of(local)
            if actual == expected:
                print(f"  OK       {entry['endpoint']:<15}  sha256={actual[:16]}...")
                ok += 1
            else:
                fails.append((entry["endpoint"], "MISMATCH", expected, actual))

    print()
    print(f"Verificados: {ok}/{total}")
    if fails:
        print()
        print("FALLOS:")
        for endpoint, status, expected, actual in fails:
            print(f"  {status:<10} {endpoint}")
            print(f"    esperado: {expected}")
            print(f"    actual:   {actual}")
        return 1

    print("✓ Integridad verificada. Todos los archivos coinciden con el manifiesto.")
    return 0


def main():
    if len(sys.argv) != 2:
        print("Uso: py src\\capture\\verify_manifest.py <captures/YYYYMMDDTHHMMSSZ/>",
              file=sys.stderr)
        sys.exit(2)

    capture_dir = Path(sys.argv[1])
    if not capture_dir.exists() or not capture_dir.is_dir():
        print(f"ERROR: no es una carpeta válida: {capture_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"Verificando: {capture_dir}")
    print()
    sys.exit(verify(capture_dir))


if __name__ == "__main__":
    main()
