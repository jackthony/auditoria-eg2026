# auditoria-eg2026

> Análisis técnico-estadístico reproducible del escrutinio ONPE EG2026. Captura, cadena de custodia, pruebas de integridad electoral, informe forense.

**Estado (2026-04-20):** universo v2-92k · 4 findings vivos H1-H4 · cadena custodia 4 niveles.

## Tech Stack

- Python 3.11+, pip + venv
- **Data (obligatorio >100k filas):** Polars + DuckDB + PyArrow. **Pandas prohibido** para >100k filas (ver `memory/feedback_data_libs.md`).
- numpy / scipy (stats), matplotlib (figuras), python-docx, reportlab
- Cloudflare Worker (proxy ONPE) en `proxy/onpe-proxy-neuracode/`
- Dashboard estático gh-pages en `web/`
- **DBs:** local DuckDB `reports/hallazgos_20260420/eg2026.duckdb`, parquet en HuggingFace público, CIDs en IPFS Filebase.
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

# Rebuild DB + hallazgos (v2-92k):
py scripts/build_duckdb_and_fix.py     # reconstruye eg2026.duckdb
py scripts/analyze_hallazgos_0420_v2.py # regenera H1-H3
py scripts/stats_h4_especiales_900k.py  # regenera H4
py scripts/sync_findings_v2.py         # sincroniza 3 findings.json

# Cadena custodia nivel 4:
.venv/Scripts/python scripts/pin_to_filebase.py  # IPFS (requiere .env)
```

RTK prefix obligatorio en shell (`rtk git status`, `rtk pytest`, etc.). Ver `~/.claude/CLAUDE.md`.

## Structure (post-purga 2026-04-20)

```
captures/{tsUTC}/   # raw ONPE + MANIFEST.jsonl — INMUTABLE
src/capture/        # fetch_onpe*, verify_manifest, fetch_onpe_mesas_async
src/process/        # build_dataset
src/analysis/       # 23 tests (stats forenses, ml, reconcile, forecast)
src/report/         # figures, build_report (docx)
scripts/            # build_duckdb_and_fix, analyze_hallazgos_*, stats_h4_*,
                    # pin_to_filebase, pin_to_ipfs, sync_findings_v2,
                    # build_hf_dataset, test_universe_complete, build_og
proxy/              # Cloudflare Worker allowlist ONPE
web/                # dashboard gh-pages (post-rebuild)
data/processed/     # meta.json, regiones.csv, tracking.csv
reports/            # hallazgos_20260420/ (autoritativo), hf_dataset/,
                    # ipfs_cids.json, storytelling_brief.md, storytelling_pack.md
docs/               # ONPE_API_ENDPOINTS.md, README_PUBLICO.md (resto purgado)
evidence/           # legal_references, public_documents, personero_copies
tests/              # pytest (test_dataset_integrity.py: 12 tests polars+duckdb)
```

## Conventions

**Código:**
- CSV: `utf-8-sig`, `csv.DictReader(delimiter=';')`. Nunca utf-8 plano ni split manual.
- Type hints obligatorios. Dataclasses para DTOs. Inmutabilidad: retornar copias.
- `logging`, nunca `print()` en producción. CLI puede usar print.
- Archivos ≤400 L preferido (800 L máx). Un módulo = una responsabilidad.
- Naming: `snake_case` / `PascalCase` / `UPPER_SNAKE` / `_prefix`.
- **Data libs:** Polars/DuckDB/PyArrow para >100k filas. Pandas banned.

**Cadena de custodia (4 niveles, NO negociable):**

| # | Nivel | Ubicación | Prueba |
|---|-------|-----------|--------|
| 1 | Local | `captures/{ts}/` INMUTABLE | MANIFEST.jsonl SHA-256 |
| 2 | GitHub | `main` + tags firmados | commit hash |
| 3 | HuggingFace | `Neuracode/onpe-eg2026-mesa-a-mesa` | parquet inmutable |
| 4 | IPFS | Filebase (primary), Pinata (backup) | CIDs en `reports/ipfs_cids.json` |

- Re-captura = carpeta nueva UTC + commit inmediato.
- Ejecutar capturas SOLO desde IP peruana (ONPE bloquea datacenters).
- IPFS pin script: `scripts/pin_to_filebase.py` (requiere `.env` con credenciales).

**Enfoque forense:**
- **Nunca afirmar "fraude".** Decir "anomalía estadística que ONPE debe explicar" (ver `memory/feedback_defensa_h4_publica.md`).
- **Métodos permitidos:** z-test 2-prop Newcombe 1998, Cohen h, bootstrap Efron-Tibshirani, Mann-Whitney U.
- **Métodos prohibidos:** Benford-1 como evidencia única (refutado Deckert/Myagkov/Ordeshook 2011).
- Severidades: CRÍTICO / MEDIA / BAJA / INFO.
- Cada finding documenta H0, H1, método, criterio de alerta, limitaciones.
- Universo = 92,766 mesas (88,063 normales + 4,703 especiales 900k+). Toda métrica nueva usa este total.

## Output Contracts

- `MANIFEST.jsonl` → `{path, size, sha256, ts_iso, url, ua, ip}` por línea.
- `reports/hallazgos_20260420/findings_consolidado_0420.json` → findings autoritativos H1-H4 con `{id, severity, test, h0, statistic, p_value, threshold, method, interpretation, limitations, n_mesas_universo}`.
- `reports/ipfs_cids.json` → pins Filebase + backup Pinata, con SHA-256 local para doble verificación.
- `reports/storytelling_brief.md` → input canónico para agente `storytelling-pe`.
- Informe docx generado SOLO por `src/report/build_report.py`. Nunca editar a mano.
- PDF fiscal generado SOLO por `scripts/build_pdf_v3.py` (bloqueado hasta ticket PDF-01).

## Agentes especializados (cuándo activar)

Agentes en `.claude/agents/`:

| Agente | Cuándo | Output |
|--------|--------|--------|
| `storytelling-pe` | Findings estables, listos para audiencia peruana | `reports/storytelling_pack.md` |
| `memorial-fiscal` | Decisión explícita de presentar ante JNE/Fiscalía | `docs/MEMORIAL_TECNICO_FISCAL.md` + PDF |

**memorial-fiscal NO invocar hasta:**
1. `findings_consolidado_0420.json` estable (análisis cerrado).
2. `captures/` cerrado y MANIFEST validado (`py make.py verify` limpio).
3. Decisión explícita de presentar.

Antes de esos 3 puntos el agente no agrega valor y contamina contexto.

**storytelling-pe protocolo:** sigue "Protocolo de arranque obligatorio" (ver su .md). Debe presentar plan 7 bullets antes de producir.

## Flujo análisis → publicación

```
capture → build → analyze → QA (Polars/DuckDB)
                                    ↓
                    memorial-fiscal ←→ storytelling-pe
                    (JNE/Fiscalía)    (TV/redes/prensa)
```

Input compartido: `findings_consolidado_0420.json` + `ipfs_cids.json` + `storytelling_brief.md`. Un dato, dos salidas. ECC no aplica a este flujo.

## Agents & ECC Workflow

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

Mapa hooks → skills en `.claude/settings.json`. SessionStart lee `MEMORY.md` + `TICKETS.md` + `HALLAZGOS_VIGENTES.md`.

## CCA Domains (Claude Code Architecture)

**1. Agentic Architecture**
- Topología primaria: pipeline con fan-out para análisis paralelos (H1, H2, H3, H4 independientes).
- Sub-agents: 2 activos (`storytelling-pe`, `memorial-fiscal`). Ambos Opus — razonamiento forense + legal PE.
- Budget: Haiku para QA datos (data-engineer), Sonnet para dev, Opus solo forense/legal.

**2. MCP & Tools**
- MCP activos: engram (memoria), drawio (diagramas).
- Tools custom: `py make.py` (CLI), scripts/ (one-shot), walker async (`fetch_onpe_mesas_async`).
- IPFS: Filebase S3 + Pinata RPC (con `.env` gitignored).

**3. Context & Reliability**
- Context hierarchy: CLAUDE.md (este) → rules globales → `HALLAZGOS_VIGENTES.md` → `MEMORY.md` → `TICKETS.md`.
- Reliability: `.env` siempre gitignored. SHA-256 MANIFEST inmutable. IPFS CIDs verificables externamente.
- Fallback: si Filebase cae, Pinata como backup proof; si ambos caen, GitHub + HF + SHA-256 locales.

## Known Constraints

- IP peruana obligatoria para captures (403/451 desde datacenters).
- NUNCA editar `MANIFEST.jsonl` ni raw bajo `captures/{ts}/`.
- Benford nunca como evidencia única.
- Pandas prohibido >100k filas.
- Budget infra: $0 (todo local + gh-pages + CF Worker + HF + Filebase/Pinata free tier).
- Git push --force / reset --hard requieren confirmación + backup branch.
- Filebase gateway `<bucket>.myfilebase.com` requiere paid plan; usar `ipfs.filebase.io/ipfs/{CID}` en público.

## Active Decisions

- **MIT + data pública:** ONPE es público por naturaleza electoral.
- **Agregación actual:** regional + mesa-a-mesa vía walker (88,064 normales + 4,703 especiales 900k+). Acta-por-acta completa pendiente módulo org. políticas.
- **Mapping prefix→depto:** ONPE alfabético con Callao=24 (validado 2026-04-20). NO usar INEI.
- **Timestamp autoritativo:** commits GitHub. GPG opcional.
- **Sin afiliación política:** firma = responsabilidad técnica, no vocería.
- **Universo v2-92k definitivo:** 92,766 mesas; toda métrica nueva usa este total.

## Pointers

- **Hallazgos vigentes** → `HALLAZGOS_VIGENTES.md` (leer antes de afirmar rankings/%)
- **Findings consolidado** → `reports/hallazgos_20260420/findings_consolidado_0420.json`
- **DB autoritativa local** → `reports/hallazgos_20260420/eg2026.duckdb`
- **Dataset público** → https://huggingface.co/datasets/Neuracode/onpe-eg2026-mesa-a-mesa
- **Parquet IPFS** → `ipfs://QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L`
- **CIDs IPFS** → `reports/ipfs_cids.json`
- **Brief storytelling** → `reports/storytelling_brief.md`
- **Pack storytelling (output agente)** → `reports/storytelling_pack.md`
- **Tickets vivos** → `TICKETS.md`
- **Metodología forense** → `METHODOLOGY.md`
- **Cadena de custodia** → `CHAIN_OF_CUSTODY.md`
- **Rules globales** → `~/.claude/rules/common/` + `~/.claude/rules/python/`
- **Memoria sesión** → `~/.claude/projects/C--Users-.../memory/MEMORY.md`
