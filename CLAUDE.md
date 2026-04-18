# auditoria-eg2026

## Purpose
Análisis técnico-estadístico reproducible del escrutinio ONPE EG2026 (captura, cadena de custodia, pruebas de integridad electoral, informe).

## Stack
- **Language**: Python 3.11+
- **Framework**: CLI + Jupyter (pandas/numpy/scipy, matplotlib, python-docx)
- **Database**: None (CSV/JSON en `data/` y `captures/`)
- **Package Manager**: pip + venv
- **Deployment**: Local (Windows). Ejecución manual con IP peruana.

## Commands
```bash
py make.py capture    # Descarga backend ONPE + MANIFEST.jsonl con SHA-256
py make.py verify     # Verifica hashes de capturas
py make.py build      # Consolida CSVs (src/process/build_dataset.py)
py make.py analyze    # Ejecuta todos los tests (src/analysis/run_all.py)
py make.py report     # figures.py + build_report.py -> Informe_Tecnico_v{N}.docx
py make.py test       # pytest tests/ -v
py make.py clean      # Borra outputs regenerables
py make.py all        # build + analyze + report
```

## Structure
```
auditoria-eg2026/
├── captures/{tsUTC}/   # raw ONPE + MANIFEST.jsonl (INMUTABLE, commit inmediato)
├── src/capture/        # fetch_onpe, hash_manifest, verify_manifest
├── src/process/        # build_dataset, reconcile
├── src/analysis/       # benford, impugnation_rates, temporal, jee_sim, strat
├── src/report/         # figures, build_report (docx)
├── data/{processed,external}/
├── reports/            # figures/, findings.json, Informe_Tecnico_v{N}.docx
├── evidence/           # legal_references, public_documents, personero_copies
├── tests/              # pytest del pipeline
└── notebooks/          # 01_exploratory.ipynb
```

## Conventions
- **Inmutabilidad de capturas:** nada en `captures/{tsUTC}/` se edita nunca. Cualquier re-captura = carpeta nueva con timestamp UTC distinto.
- **Cadena de custodia:** cada captura => MANIFEST.jsonl (SHA-256, URL origen, UA, IP) + commit firmado (`git commit -S`).
- CSV: `utf-8-sig`, `csv.DictReader(delimiter=';')`. Nunca `utf-8` plano ni split manual.
- Logging via `logging`, nunca `print()` en código de producción. CLI puede usar print para UX.
- Type hints obligatorios. Dataclasses para DTOs. Inmutabilidad: retornar copias, no mutar.
- Archivos ≤400 líneas preferido, 800 máx. Un módulo = una responsabilidad (parse / classify / analyze / report).
- Naming: `snake_case` funciones, `PascalCase` clases, `UPPER_SNAKE` constantes, `_prefix` privados.

## Enfoque forense/estadístico (crítico)
- **NO se afirma "fraude".** Se reporta desviación + p-valor + limitaciones conocidas. Ver `METHODOLOGY.md`.
- Benford-1 con χ² gl=8: **señal complementaria**, NO evidencia única (Deckert/Myagkov/Ordeshook 2011).
- Hallazgos etiquetados: CRÍTICO / MEDIA / BAJA / INFO. Política en `METHODOLOGY.md §5`.
- Todo test debe documentar H0, H1, método, criterio de alerta y limitaciones.

---
<!-- CCA Domain 1: Agentic Architecture -->
## Agent Architecture
- **Topología**: Pipeline (capture → build → analyze → report). Fan-out para análisis independientes (benford, temporal, strat, jee_sim).
- **Orchestrator**: Sonnet (main). **Workers**: Haiku (tareas determinísticas: parsing, validación, formato).
- **Activación**:
  - Nueva prueba estadística → `planner` (estructura) + `tdd-guide` (tests primero).
  - Cambios de código → `code-reviewer` + `python-reviewer`.
  - Manipulación de CSV/entrada externa → `security-reviewer` (injection, path traversal).
  - Decisiones metodológicas (elegir un test, justificar estratificación) → `architect` (Opus) SOLO si Sonnet insuficiente.

<!-- CCA Domain 2: Claude Code Configuration -->
## Claude Code Config
- Rules globales: `~/.claude/rules/common/` + `~/.claude/rules/python/` aplican.
- Overrides de este proyecto: este archivo. Convenciones forenses (inmutabilidad de capturas, cadena de custodia) NO son negociables.
- Memoria por sesión en: `~/.claude/projects/C--Users-jaaguilar-Documents-elecciones2026-auditoria-eg2026/memory/`.

<!-- CCA Domain 3: Prompt Engineering & Structured Output -->
## Output Contracts
- `MANIFEST.jsonl`: una línea por archivo capturado `{path, size, sha256, ts_iso, url, ua, ip}`.
- `reports/findings.json`: lista de `{id, severity, test, h0, statistic, p_value, threshold, interpretation, limitations}`.
- Validación: schema-first. Usar pydantic si crece la complejidad; hoy dataclasses + validadores manuales.
- Informe docx: generado SOLO por `src/report/build_report.py` desde `findings.json` + figures. No editar el docx a mano.

<!-- CCA Domain 4: Tool Design & MCP -->
## MCP & Tools
- MCP activos: hereda globales (`engram`, `drawio`).
- CLI interno: `make.py` + scripts bajo `src/`. No hay tools custom MCP.
- Seguridad: validar paths de capture (no escapar `captures/`), no seguir redirects a hosts distintos de ONPE oficial, User-Agent identificable.

<!-- CCA Domain 5: Context & Reliability -->
## Reliability
- **Reproducibilidad**: requirements.txt pinneado. `verify_manifest.py` reexaminable por cualquier tercero.
- **Fallo en captura** (ONPE 5xx / timeout): reintento 2x con backoff; si falla, registrar incidente en `captures/{ts}/README.md` y NO reintentar silenciosamente al día siguiente bajo el mismo timestamp.
- **Error de red desde IP no-PE**: ONPE bloquea datacenters. Si 403/451 → abortar con mensaje claro, no intentar proxy.
- RTK: prefijo obligatorio en shell (git, pytest, pip list, grep, etc.) para ahorro de tokens.

---

## Active Decisions
- **MIT + data pública**: datos ONPE son públicos por naturaleza electoral; código MIT.
- **Nivel de agregación actual = regional**: acta-por-acta requiere acceso al módulo de organizaciones políticas (pendiente).
- **Cadena de custodia via Git + SHA-256**: los commits en GitHub son el timestamp autoritativo. GPG opcional pero recomendado.
- **Sin afiliación política**: el repo analiza números, no hace vocería. La firma del autor implica responsabilidad técnica, no política.

## Known Constraints
- Ejecutar capturas SOLO desde IP peruana (ONPE bloquea extranjeras).
- No se debe editar NUNCA un MANIFEST.jsonl ni archivos bajo `captures/{ts}/raw/`.
- No usar Benford como evidencia única de fraude — siempre acompañar de otros tests y contexto.
- Budget de infra: $0 (todo local).
