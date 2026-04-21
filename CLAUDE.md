# auditoria-eg2026

> Análisis técnico-estadístico reproducible del escrutinio ONPE EG2026. Captura, cadena de custodia, pruebas de integridad electoral.

**Estado (2026-04-21):** universo v2-92k · **6 findings blindados** (H1, H2, H3, H4, H9, H12) · **FORENSIS L3 autónomo** (12 agentes) · cadena custodia 4 niveles.

## Tech Stack

- Python 3.11+, venv.
- **Data obligatorio >100k filas:** Polars + DuckDB + PyArrow. **Pandas prohibido** (`memory/feedback_data_libs.md`).
- scipy (stats), matplotlib (figuras), python-docx (informe).
- DB local: `reports/hallazgos_20260420/eg2026.duckdb` (autoritativa).
- Parquet HF: `Neuracode/onpe-eg2026-mesa-a-mesa`.
- IPFS: Filebase (primary) + Pinata (backup).
- Probabilidades <1e-15 → `scipy.stats.binom.logsf` (nunca `1-cdf`, ver `memory/feedback_logsf_underflow.md`).

## Commands

```bash
py make.py verify       # SHA-256 MANIFEST
py make.py analyze      # run_all (4 módulos vivos)
py make.py report       # figures + docx
py make.py test         # pytest 15 tests
py make.py sync         # sync findings 3 JSONs
py make.py rebuild-db   # rebuild eg2026.duckdb
```

RTK prefix en shell (`rtk git status`, `rtk pytest`). Ver `~/.claude/CLAUDE.md`.

## Structure

```
captures/{tsUTC}/   # raw ONPE + MANIFEST SHA-256 — INMUTABLE
src/capture/        # fetch_onpe*, verify_manifest, walker async
src/process/        # build_dataset
src/analysis/       # run_all + 4 módulos vivos (impugnation_rates, bias, ausentismo, mesa_impugnadas)
src/report/         # figures, build_report (docx)
scripts/            # build_duckdb_and_fix, analyze_hallazgos_0420_v2, stats_h4, sync_findings_v2, pin_to_filebase
                    # FORENSIS: confidence_scorer, hitl_router, snapshot_diff, run_pipeline
proxy/              # Cloudflare Worker ONPE
web/                # dashboard gh-pages + _tpl/finding.html (template landings)
data/processed/     # meta.json, regiones.csv
reports/
  raw_findings/     # 6 raw_h*.json (data-forensic output)
  stat_findings/    # 6 stat_h*.json (stats-expert output)
  hallazgos_20260420/  # eg2026.duckdb + findings_consolidado_0420.json
  hf_dataset/       # parquet público
tests/              # test_dataset_integrity.py (polars+duckdb)
.claude/agents/     # FORENSIS team (12): forensis-orchestrator, sensor, data-forensic,
                    # stats-expert, forensic-challenger, narrator-technical, narrator-market,
                    # virality-engine, web-builder, publishing-guard, comment-router,
                    # expert-synthesizer + sidecars (audit-narrator, storytelling-pe)
.github/workflows/  # capture, sensor, pipeline, comment-router, deploy-pages
```

## Conventions

**Código:**
- CSV: `utf-8-sig`, `csv.DictReader(delimiter=';')`. Nunca utf-8 plano.
- Type hints obligatorios. Inmutabilidad. `logging` > `print` en prod.
- Naming: `snake_case` / `PascalCase` / `UPPER_SNAKE`.
- Archivos ≤400 L preferido (800 máx).

**Cadena de custodia (4 niveles):**

| # | Nivel | Prueba |
|---|-------|--------|
| 1 | Local `captures/{ts}/` inmutable | MANIFEST.jsonl SHA-256 |
| 2 | GitHub main + tags | commit hash |
| 3 | HuggingFace dataset | parquet inmutable |
| 4 | IPFS Filebase + Pinata | CIDs en `reports/ipfs_cids.json` |

Re-captura = carpeta nueva UTC + commit inmediato. IP peruana obligatoria (ONPE bloquea datacenters).

**Enfoque forense:**
- **Nunca "fraude".** Decir "anomalía que ONPE debe explicar".
- **Métodos permitidos:** solo los del paper registry (`memory/reference_papers_forenses.md`).
- **Benford-1 prohibido** (Deckert-Myagkov-Ordeshook 2011).
- Universo = **92,766 mesas** (88,063 normales + 4,703 especiales 900k+).
- Mapping prefix→depto = ONPE alfabético + Callao=24. NO INEI.

## Pipeline FORENSIS (12 agentes, L3 autónomo)

```
[sensor 6h] → signal.json
    ↓
[orchestrator] → data-forensic → stats-expert → forensic-challenger
    ↓
[confidence_scorer.py] → tier AUTO | PENDING-JACK | DRAFT
    ↓
narrator-technical + narrator-market → virality-engine → publishing-guard → web-builder
    ↓
gh-pages (landing) + Giscus (comments)
    ↓
[comment-router] → auto-reply | expert-synthesizer | jack
```

**Scope agente:** solo `web/` + `reports/{raw,stat,narrative,challenge,feedback}_findings/` + `audit_log.jsonl`.
**Branch:** `forensis/<finding_id>-<ts>`. Jack merge manual. Nunca push directo a `main`.

### Tabla agentes

| # | Agente | Modelo | Rol |
|---|--------|--------|-----|
| 0 | `forensis-orchestrator` | Sonnet | Coordina + dispatch |
| 1 | `sensor` | Haiku | Detecta deltas ONPE 6h |
| 2 | `data-forensic` | Haiku | SQL → raw_finding.json |
| 3 | `stats-expert` | Sonnet | Stats + paper → stat_finding.json |
| 4 | `forensic-challenger` | Sonnet | Red-team adversarial |
| 5 | `narrator-technical` | Sonnet | tech.md + scientific.md |
| 6 | `narrator-market` | Haiku | mercado.md sin jerga |
| 7 | `virality-engine` | Sonnet | meta/og/share JSON |
| 8 | `web-builder` | Opus | Render landing |
| 9 | `publishing-guard` | Haiku | Veto final (tone + fact-check) |
| 10 | `comment-router` | Haiku | Clasifica Giscus 6 tipos |
| 11 | `expert-synthesizer` | Sonnet | Refuta técnica → PR spec |

### Tier routing (confidence score)

```
score = 0.4·p_factor + 0.3·effect_factor + 0.3·challenger_factor
```

- **AUTO ≥ 0.90:** publica directo + PR auto. Jack revisa post-merge.
- **PENDING-JACK 0.70-0.89:** PR + issue `urgent-jack`. Bloqueado hasta merge.
- **DRAFT < 0.70:** queda en `reports/drafts/`. No se publica.

### Agentes sidecar (legacy/opcional)

| Agente | Cuándo |
|--------|--------|
| `storytelling-pe` | Findings estables → pack TV/redes/prensa PE |
| `audit-narrator` | Pipeline 3-agentes pre-FORENSIS (legacy) |

## Output Contracts

- `MANIFEST.jsonl` → `{path, size, sha256, ts_iso, url, ua, ip}` por línea.
- `raw_findings/raw_<slug>_<ts>.json` → métricas numéricas + db_sha256.
- `stat_findings/stat_<slug>_<ts>.json` → test + p-value + paper + limitaciones.
- `findings_consolidado_0420.json` → findings autoritativos sincronizados.
- `reports/ipfs_cids.json` → pins Filebase + Pinata con SHA-256 doble.
- Informe docx generado SOLO por `src/report/build_report.py`. Nunca a mano.

## Known Constraints

- IP peruana obligatoria para captures.
- NUNCA editar MANIFEST.jsonl ni raw bajo `captures/{ts}/`.
- Benford nunca como evidencia única.
- Pandas prohibido >100k filas.
- Budget infra: $0 (local + gh-pages + Worker + HF + Filebase/Pinata free tier).

## Active Decisions

- MIT + data pública (ONPE electoral).
- Universo v2-92k definitivo.
- Timestamp autoritativo = commits GitHub.
- Sin afiliación política — firma técnica.

## Pointers

- **Arquitectura + scope** → `docs/ARCHITECTURE.md`
- **Multi-elección** → `docs/ELECCIONES.md`
- **Hallazgos vigentes** → `docs/HALLAZGOS_VIGENTES.md`
- **Metodología** → `docs/METHODOLOGY.md`
- **Cadena de custodia** → `docs/CHAIN_OF_CUSTODY.md`
- **Tickets** → `docs/TICKETS.md`
- **FORENSIS SDD** → `docs/specs/FEAT-autonomous-auditor.md`
- **Paper registry** → `memory/reference_papers_forenses.md`
- **DB** → `reports/hallazgos_20260420/eg2026.duckdb`
- **Dataset público** → https://huggingface.co/datasets/Neuracode/onpe-eg2026-mesa-a-mesa
- **CIDs IPFS** → `reports/ipfs_cids.json`
