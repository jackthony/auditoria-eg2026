"""
scripts/build_hf_dataset.py — DATA-MARKET

Extrae capturas mesa-a-mesa → parquet + CSV long-format.
Sube al repo neuracode/onpe-eg2026-mesa-a-mesa en HuggingFace.

Uso:
    py scripts/build_hf_dataset.py              # solo extrae local
    py scripts/build_hf_dataset.py --upload     # extrae + sube a HF
    py scripts/build_hf_dataset.py --upload --ts 20260419T035056Z

Requisito:
    huggingface-cli login   (una sola vez)
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HF_REPO = "Neuracode/onpe-eg2026-mesa-a-mesa"
ID_ELECCION = 10  # presidencial 1ra vuelta 2026

# Mapeo ubigeo ONPE (NO INEI) → departamento.
# ONPE usa orden alfabético, EXCEPTO Callao movido a 24.
# Extranjero = prefix 91-95 (África+Diplomático/América/Asia/Europa/Oceanía).
# Validado empíricamente 2026-04-20 por muestreo locales (universidades + IE numbering).
# Ver scripts/validate_prefix_mapping.py.
DEPTO_NAMES = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa",
    "05": "Ayacucho", "06": "Cajamarca", "07": "Cusco", "08": "Huancavelica",
    "09": "Huánuco", "10": "Ica", "11": "Junín", "12": "La Libertad",
    "13": "Lambayeque", "14": "Lima", "15": "Loreto", "16": "Madre de Dios",
    "17": "Moquegua", "18": "Pasco", "19": "Piura", "20": "Puno",
    "21": "San Martín", "22": "Tacna", "23": "Tumbes", "24": "Callao",
    "25": "Ucayali",
    "91": "Extranjero", "92": "Extranjero", "93": "Extranjero",
    "94": "Extranjero", "95": "Extranjero",
}


def _find_latest_ts() -> str | None:
    caps = sorted(ROOT.glob("captures/*/mesas"), key=lambda p: p.parent.name, reverse=True)
    for cap in caps:
        if sum(1 for _ in cap.glob("*.json.gz")) > 1000:
            return cap.parent.name
    return None


def extract(ts: str) -> pd.DataFrame:
    mesas_dir = ROOT / "captures" / ts / "mesas"
    files = sorted(mesas_dir.glob("*.json.gz"))
    print(f"[HF] ts={ts}  archivos={len(files):,}")

    rows: list[dict] = []
    skipped = 0

    for i, f in enumerate(files):
        if i % 10000 == 0 and i:
            print(f"  {i:>6}/{len(files):,}  rows={len(rows):,}", flush=True)
        try:
            with gzip.open(f, "rb") as fh:
                d = json.loads(fh.read())
        except Exception:
            skipped += 1
            continue

        actas = d.get("data") or []
        acta = next((a for a in actas if a.get("idEleccion") == ID_ELECCION), None)
        if not acta:
            continue

        codigo = acta.get("codigoMesa", "")
        ubigeo = str(acta.get("idUbigeo", "")).zfill(6)
        depto_code = ubigeo[:2]
        depto = DEPTO_NAMES.get(depto_code, f"UBG{depto_code}")
        estado = acta.get("estadoActa", "")
        electores = acta.get("totalElectoresHabiles")
        emitidos = acta.get("totalVotosEmitidos")
        validos = acta.get("totalVotosValidos")
        pct_part = acta.get("porcentajeParticipacionCiudadana")
        local = acta.get("nombreLocalVotacion", "")

        detalle = acta.get("detalle") or []
        if not detalle:
            # Mesa sin detalle: 1 fila con nulos de votos
            rows.append({
                "codigo_mesa": codigo,
                "ubigeo": ubigeo,
                "departamento": depto,
                "estado_acta": estado,
                "electores_habiles": electores,
                "votos_emitidos": emitidos,
                "votos_validos": validos,
                "pct_participacion": pct_part,
                "local_votacion": local,
                "partido_codigo": None,
                "partido": None,
                "candidato": None,
                "votos": None,
                "pct_votos_validos": None,
                "es_voto_especial": False,
            })
            continue

        for item in detalle:
            codigo_agrup = item.get("adCodigo", "")
            partido = item.get("adDescripcion", "")
            votos_item = item.get("adVotos")
            pct_val = item.get("adPorcentajeVotosValidos")
            es_especial = codigo_agrup in ("00000081", "00000080")  # nulos, blancos

            candidatos = item.get("candidato") or [{}]
            cand = candidatos[0]
            nombre_cand = None
            if not es_especial:
                ap = cand.get("apellidoPaterno", "") or ""
                am = cand.get("apellidoMaterno", "") or ""
                nb = cand.get("nombres", "") or ""
                nombre_cand = f"{ap} {am}, {nb}".strip(", ") or None

            rows.append({
                "codigo_mesa": codigo,
                "ubigeo": ubigeo,
                "departamento": depto,
                "estado_acta": estado,
                "electores_habiles": electores,
                "votos_emitidos": emitidos,
                "votos_validos": validos,
                "pct_participacion": pct_part,
                "local_votacion": local,
                "partido_codigo": codigo_agrup,
                "partido": partido,
                "candidato": nombre_cand,
                "votos": votos_item,
                "pct_votos_validos": pct_val,
                "es_voto_especial": es_especial,
            })

    print(f"  done. rows={len(rows):,}  skipped={skipped}")
    df = pd.DataFrame(rows)
    # tipos
    for col in ("electores_habiles", "votos_emitidos", "votos_validos", "votos"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in ("pct_participacion", "pct_votos_validos"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
    return df


def save_local(df: pd.DataFrame, ts: str) -> Path:
    out_dir = ROOT / "reports" / "hf_dataset"
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / f"onpe_eg2026_mesas_{ts}.parquet"
    csv_path = out_dir / f"onpe_eg2026_mesas_{ts}.csv"
    df.to_parquet(parquet_path, index=False, compression="zstd")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"OK parquet: {parquet_path.relative_to(ROOT)}  ({parquet_path.stat().st_size/1e6:.1f} MB)")
    print(f"OK csv:     {csv_path.relative_to(ROOT)}  ({csv_path.stat().st_size/1e6:.1f} MB)")
    return out_dir


def write_readme(out_dir: Path, ts: str, n_mesas: int, n_rows: int) -> None:
    readme = f"""---
license: cc-by-4.0
language:
- es
tags:
- elections
- peru
- onpe
- electoral-audit
- mesa-a-mesa
pretty_name: ONPE EG2026 — Resultados mesa a mesa (primera vuelta)
size_categories:
- 1M<n<10M
---

# ONPE EG2026 — Resultados electorales mesa a mesa

**Fuente:** API pública ONPE (`resultadoelectoral.onpe.gob.pe`)
**Captura:** `{ts}` UTC — SHA-256 en [MANIFEST.jsonl](https://github.com/jackthony/auditoria-eg2026)
**Licencia:** CC-BY-4.0 — datos electorales públicos por naturaleza (Ley 26859)
**Proyecto:** [auditoria-eg2026](https://github.com/jackthony/auditoria-eg2026) · Jack de Neuracode

## Descripción

Dataset long-format con los resultados presidenciales (idEleccion=10) de la primera vuelta
de las Elecciones Generales del Perú 2026 (12 abril 2026), extraídos mesa a mesa desde
la API oficial de la ONPE.

- **{n_mesas:,} mesas** | **{n_rows:,} filas** (1 fila = mesa × partido)
- Incluye: votos por partido, candidato presidencial, estado del acta, electores hábiles
- `estadoActa`: D=Contabilizada, I=Impugnada, P=Pendiente, O=Observada

## Schema

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_mesa` | str | Código ONPE de 6 dígitos |
| `ubigeo` | str | Ubigeo 6 dígitos (depto+prov+dist) |
| `departamento` | str | Nombre del departamento |
| `estado_acta` | str | D/I/P/O |
| `electores_habiles` | Int64 | Padrón habilitado en la mesa |
| `votos_emitidos` | Int64 | Total votos emitidos |
| `votos_validos` | Int64 | Votos válidos (excluye nulos/blancos) |
| `pct_participacion` | float32 | % participación ciudadana |
| `local_votacion` | str | Nombre del local de votación |
| `partido_codigo` | str | Código agrupación política ONPE |
| `partido` | str | Nombre del partido |
| `candidato` | str | Apellidos, Nombres del candidato presidencial |
| `votos` | Int64 | Votos obtenidos (null si acta impugnada) |
| `pct_votos_validos` | float32 | % sobre votos válidos |
| `es_voto_especial` | bool | True = NULOS o BLANCOS |

## Uso rápido

```python
import pandas as pd

df = pd.read_parquet("onpe_eg2026_mesas_{ts}.parquet")

# Resultados presidenciales nacionales
nacional = (
    df[~df.es_voto_especial]
    .groupby("partido")["votos"]
    .sum()
    .sort_values(ascending=False)
)

# Mesas impugnadas por departamento
imp = df[df.estado_acta == "I"].groupby("departamento")["codigo_mesa"].nunique()
```

## Hallazgos del proyecto de auditoría

Ver [reports/findings.json](https://github.com/jackthony/auditoria-eg2026/blob/main/reports/findings.json)
y el [dashboard público](https://jackthony.github.io/auditoria-eg2026/).

## Cadena de custodia

Cada captura incluye MANIFEST.jsonl con SHA-256 por archivo, timestamp UTC y URL de origen.
Verificar con: `python src/capture/verify_manifest.py captures/{ts}/`

## Cita

```bibtex
@dataset{{neuracode2026onpe,
  author    = {{Aguilar, Jack}},
  title     = {{ONPE EG2026 — Resultados mesa a mesa (primera vuelta)}},
  year      = {{2026}},
  publisher = {{HuggingFace}},
  url       = {{https://huggingface.co/datasets/neuracode/onpe-eg2026-mesa-a-mesa}},
  note      = {{Captura {ts} UTC. Datos públicos ONPE. CC-BY-4.0.}}
}}
```
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    print(f"OK README.md escrito")


def upload(out_dir: Path, ts: str) -> None:
    from huggingface_hub import HfApi
    api = HfApi()
    print(f"[HF] subiendo a {HF_REPO} ...")
    api.create_repo(HF_REPO, repo_type="dataset", exist_ok=True, private=False)
    api.upload_folder(
        folder_path=str(out_dir),
        repo_id=HF_REPO,
        repo_type="dataset",
        commit_message=f"data: captura {ts} — {len(list(out_dir.glob('*.parquet')))} archivos",
    )
    print(f"OK → https://huggingface.co/datasets/{HF_REPO}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ts", default=None)
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()

    ts = args.ts
    if ts is None:
        caps = sorted(ROOT.glob("captures/*/mesas"), key=lambda p: p.parent.name, reverse=True)
        for cap in caps:
            if sum(1 for _ in cap.glob("*.json.gz")) > 1000:
                ts = cap.parent.name
                break
    if not ts:
        print("ERROR: sin captura mesa-a-mesa", file=sys.stderr)
        sys.exit(1)

    out_dir = ROOT / "reports" / "hf_dataset"
    parquet_path = out_dir / f"onpe_eg2026_mesas_{ts}.parquet"

    if parquet_path.exists():
        print(f"[HF] parquet ya existe — skip extracción ({parquet_path.stat().st_size/1e6:.1f} MB)")
        import pandas as pd
        df = pd.read_parquet(parquet_path)
    else:
        df = extract(ts)
        save_local(df, ts)

    n_mesas = df["codigo_mesa"].nunique()
    n_rows = len(df)
    write_readme(out_dir, ts, n_mesas, n_rows)

    if args.upload:
        upload(out_dir, ts)
    else:
        print(f"\n[HF] dataset listo localmente en reports/hf_dataset/")
        print(f"     Para subir: py scripts/build_hf_dataset.py --upload")
        print(f"     Primero: huggingface-cli login")


if __name__ == "__main__":
    main()
