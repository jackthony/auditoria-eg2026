# auditoria-eg2026

> Análisis técnico-estadístico reproducible del escrutinio ONPE EG2026. Captura, cadena de custodia, pruebas de integridad electoral, informe forense.

## Tech Stack

- Python 3.11+, pip + venv
- pandas / numpy / scipy, matplotlib, python-docx, reportlab
- Cloudflare Worker (proxy ONPE) en `proxy/onpe-proxy-neuracode/`
- Dashboard estático gh-pages en `web/`
- Sin DB. Todo CSV/JSON en `data/` y `captures/`
- Windows local (ejecución manual desde IP peruana)

## Commands

```bash
py make.py capture         # backend ONPE agregado + MANIFEST SHA-256
py make.py capture-mesas   # walker mesa-a-mesa (async, vía Worker)
py make.py verify          # verifica hashes de capturas
py make.py build           # consolida CSVs
py make.py analyze         # tests agregados (run_all)
py make.py analyze-mesas   # tests mesa-a-mesa (auto-detecta ts último)
py make.py report          # figures + docx
py make.py test            # pytest
py make.py clean           # borra outputs regenerables
```

RTK prefix obligatorio en shell (`rtk git status`, `rtk pytest`, etc.). Ver `~/.claude/CLAUDE.md`.

## Structure

```
captures/{tsUTC}/   # raw ONPE + MANIFEST.jsonl — INMUTABLE
src/capture/        # fetch_onpe*, verify_manifest
src/process/        # build_dataset
src/analysis/       # 16 tests (benford, temporal, forecast, reconcile*, ml)
src/report/         # figures, build_report (docx)
scripts/            # build_dashboard_json, build_pdf_v3, build_og, telegram, capture_loop
proxy/              # Cloudflare Worker allowlist ONPE
web/                # dashboard + chat + historia (gh-pages)
data/processed/     # meta.json, regiones.csv, tracking.csv
reports/            # findings.json, forecast.json, figures/, PDFs, perito/
docs/               # memorial, evidencia, hipotesis, briefing
dossier-perito/     # paquete fiscal congelado
evidence/           # legal_references, public_documents, personero_copies
tests/              # pytest
```

## Conventions

**Código:**
- CSV: `utf-8-sig`, `csv.DictReader(delimiter=';')`. Nunca utf-8 plano ni split manual.
- Type hints obligatorios. Dataclasses para DTOs. Inmutabilidad: retornar copias.
- `logging`, nunca `print()` en producción. CLI puede usar print.
- Archivos ≤400 L preferido (800 L máx). Un módulo = una responsabilidad.
- Naming: `snake_case` / `PascalCase` / `UPPER_SNAKE` / `_prefix`.

**Cadena de custodia (NO negociable):**
- `captures/{ts}/` INMUTABLE. Re-captura = carpeta nueva.
- Cada captura → `MANIFEST.jsonl` con SHA-256, URL, UA, IP + commit firmado.
- Ejecutar capturas SOLO desde IP peruana (ONPE bloquea datacenters).

**Enfoque forense:**
- NO afirmar "fraude". Reportar desviación + p-valor + limitaciones. Ver `METHODOLOGY.md`.
- Benford-1 es señal complementaria, nunca evidencia única (Deckert/Myagkov/Ordeshook 2011).
- Severidades: CRÍTICO / MEDIA / BAJA / INFO.
- Cada test documenta H0, H1, método, criterio de alerta, limitaciones.

## Output Contracts

- `MANIFEST.jsonl` → `{path, size, sha256, ts_iso, url, ua, ip}` por línea.
- `reports/findings.json` → `[{id, severity, test, h0, statistic, p_value, threshold, interpretation, limitations}]`.
- Informe docx generado SOLO por `src/report/build_report.py`. Nunca editar a mano.
- PDF fiscal generado SOLO por `scripts/build_pdf_v3.py` (bloqueado hasta ticket PDF-01).

## Agents & Workflow

**Topología:** pipeline (capture → build → analyze → report). Fan-out para análisis independientes.

**Activación automática:**
- Nuevo test estadístico → `planner` + `tdd-guide`
- Cambios en `src/` → `code-reviewer` + `python-reviewer`
- `src/capture/` → `security-reviewer` obligatorio (path traversal, redirects)
- Decisión metodológica → `architect` (solo si Sonnet insuficiente)

**ECC workflow (disparado por hooks):**

```
/ecc:plan → /ecc:tdd → [implementar] → /ecc:code-review →
/ecc:quality-gate → /ecc:verify → /ecc:e2e → [commit] → /ecc:checkpoint
```

Mapa hooks → skills en `.claude/settings.json`. SessionStart lee `MEMORY.md` + `TICKETS.md`.

## Known Constraints

- IP peruana obligatoria para captures (403/451 desde datacenters).
- NUNCA editar `MANIFEST.jsonl` ni raw bajo `captures/{ts}/`.
- Benford nunca como evidencia única.
- Budget infra: $0 (todo local + gh-pages + CF Worker free tier).
- Git push --force / reset --hard requieren confirmación + backup branch.

## Active Decisions

- **MIT + data pública**: ONPE es público por naturaleza electoral.
- **Agregación actual = regional + mesa-a-mesa vía walker**. Acta-por-acta completa pendiente módulo org. políticas.
- **Timestamp autoritativo = commits GitHub**. GPG opcional.
- **Sin afiliación política.** Firma = responsabilidad técnica, no vocería.

## Pointers

- **Tickets vivos** → `TICKETS.md`
- **Metodología forense** → `METHODOLOGY.md`
- **Cadena de custodia** → `CHAIN_OF_CUSTODY.md`
- **Rules globales** → `~/.claude/rules/common/` + `~/.claude/rules/python/`
- **Memoria sesión** → `~/.claude/projects/C--Users-.../memory/MEMORY.md`
