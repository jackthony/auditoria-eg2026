# Cadena de Custodia — Snapshots ONPE y Documentos

Trazabilidad SHA-256 de los archivos que sustentan este dossier.

**Fecha generación:** 2026-04-17.
**Método:** `sha256sum` (POSIX).

---

## Snapshots ONPE capturados

| Timestamp UTC | Corte % | Directorio |
|---------------|---------|------------|
| 2026-04-17T06:27:11Z | 92.91% | `captures/20260417T062711Z/` |
| 2026-04-17T08:41:14Z | 93.17% | `captures/20260417T084114Z/` |

Cada captura contiene:
- `raw/snap1.json` + `raw/snap2.json` (datos crudos API ONPE).
- `raw/health.json` (metadata API).
- `raw/tracking.json` (histórico de acumulación).
- `MANIFEST.jsonl` (índice con hash individual por archivo).
- `README.md` (descripción del snapshot).

**Hashes por snapshot se generan en MANIFEST.jsonl automáticamente.**

Para verificación independiente:

```bash
cd captures/20260417T084114Z/
cat MANIFEST.jsonl
sha256sum raw/*.json
```

Los hashes impresos deben coincidir con los de MANIFEST.jsonl.

---

## Documentos metodológicos

| Documento | SHA-256 (al momento pre-registro 2026-04-17) |
|-----------|----------------------------------------------|
| `docs/HIPOTESIS_CIENTIFICAS.md` | `0aa1e92f7acad561941b52d33eb7ca98ad3057a86676be183cb93ab946c7f121` |
| `docs/TESTS_FORENSES_EXTENDIDOS.md` | `70d9bc91b4a96e93cbde739362427bb404ce683b7e1b14eb906bac60b9d475e0` |

**Verificación:**

```bash
cd auditoria-eg2026/
git checkout 413d6a1   # commit pre-registro
sha256sum docs/HIPOTESIS_CIENTIFICAS.md
sha256sum docs/TESTS_FORENSES_EXTENDIDOS.md
```

Los valores deben coincidir con los listados arriba.

---

## Commits git relevantes

| Commit | Contenido |
|--------|-----------|
| `9257a0f` | Scaffolding inicial + primera captura ONPE |
| `c877507` | Forecast bayesiano + memorial técnico + dashboard |
| `15ae5dd` | Tests forenses M1 + M2 |
| `413d6a1` | 5 hipótesis H1-H5 (Mebane/Hicken) — **pre-registro** |

Remoto público: `github.com/jackthony/auditoria-eg2026`.

---

## Reproducibilidad bit-a-bit

```bash
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
git log --oneline                     # verificar cadena commits
pip install -r requirements.txt
python src/process/build_dataset.py   # procesa snapshots → CSVs
python -m src.analysis.run_all        # ejecuta los 15 tests
diff reports/findings.json dossier-perito/reports/findings.json
# (salvo timestamp, debe ser idéntico)
```

---

## Limitaciones de la cadena de custodia

Ver `05_LIMITACIONES.md` sección L11.

**Faltan para admisibilidad judicial formal:**
- Certificación notarial.
- Time-stamping RFC3161.
- Firma digital acreditada por el perito colegiado.

Estos elementos debe aportarlos el perito al momento de firmar el dossier.
