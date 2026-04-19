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

---

## ECC Workflow (POLÍTICA OBLIGATORIA — auto-disparada por hooks)

**Regla cero:** Para CUALQUIER cambio de código, UX o documento jurídico, se ejecuta el ciclo ECC. Los hooks en `.claude/settings.json` recuerdan automáticamente qué corresponde según el archivo modificado.

**Mapa hook → skill ECC:**

| Trigger | Acción esperada |
|---------|------------------|
| `SessionStart` | Leer `MEMORY.md`, recordar política ECC, ver `§UX_UI_BACKLOG`. |
| `PostToolUse` Edit/Write en `web/**` o `scripts/build_dashboard_json.py` | `/ecc:quality-gate` + `/ecc:e2e` (smoke dashboard) antes de commit. Actualizar OG image y hash de `data.json`. |
| `PostToolUse` Edit/Write en `src/analysis/**` o `src/process/**` | `/ecc:test-coverage` + `/ecc:code-review` (python-reviewer + security-reviewer). |
| `PostToolUse` Edit/Write en `src/capture/**` | `/ecc:verify` + `/ecc:code-review` (security-reviewer obligatorio). |
| `PostToolUse` Edit/Write en `docs/MEMORIAL_*` o `METHODOLOGY*` | Validar referencias cruzadas. Commit con prefijo `docs(memorial|methodology):`. |
| `PreToolUse` Bash con `git commit` | Confirmar que se ejecutaron quality-gate, code-review y verify. |
| `PreToolUse` Bash con `git push --force` o `git reset --hard` | Confirmar con usuario + crear backup branch. |
| `Stop` | `/ecc:checkpoint` + `/ecc:save-session`. Issue/TODO si quedó UX a medias. |

**Ciclo estándar para nuevo ticket UX/UI:**

```
/ecc:plan          (planifica el ticket sobre UX_UI_BACKLOG)
/ecc:tdd           (tests primero — Playwright para UX, pytest para data)
[implementación]
/ecc:code-review   (python-reviewer si toca src/, typescript-reviewer si toca web/)
/ecc:quality-gate  (lint + format + types + size budget)
/ecc:verify        (regen data.json + verify_manifest)
/ecc:e2e           (smoke en jackthony.github.io/auditoria-eg2026/)
[git commit]
/ecc:checkpoint    (snapshot de progreso)
```

---

## UX_UI_BACKLOG (priorizado, dispara `/ecc:plan` por ticket)

> Cada ítem va con esfuerzo estimado y un único responsable humano (Tony / Jack). Marcar `[x]` al completar. Sprint 1 = quick wins (alto impacto / bajo costo). El loop `--publish` debe seguir verde tras cada cambio.

### Sprint 1 — Quick wins (~10 h totales)
- [ ] **MAPA-01** Mapa choropleth Perú (Leaflet + GeoJSON regiones) coloreado por margen RLA−Sánchez. Esfuerzo 4 h. Owner: Tony.
- [ ] **LIVE-01** Auto-refresh `data.json` cada 5 min sin reload + badge "EN VIVO" pulsante + "Actualizado hace X min". Esfuerzo 1.5 h. Owner: Tony.
- [ ] **SHARE-01** Botón "Compartir" → X / WhatsApp / Telegram con texto pre-armado del corte. Esfuerzo 1 h. Owner: Tony.
- [ ] **OG-01** OG image dinámica generada en cada loop (margen + corte + timestamp), referenciada en `<meta property="og:image">`. Esfuerzo 2 h. Owner: Tony.
- [ ] **HASH-01** Hash SHA-256 del último `data.json` visible en footer + link "verificar inline". Esfuerzo 30 min. Owner: Tony.
- [ ] **FOOT-01** Footer con redes (TikTok / IG / GitHub) + link directo al memorial PDF. Esfuerzo 30 min. Owner: Tony.

### Sprint 2 — Diferenciador técnico (~23 h)
- [ ] **TABS-01** Tabs (Resultado · Hallazgos · Forecast · Verificación). Esfuerzo 2 h.
- [ ] **TABLE-01** Tabla findings con sort/filter por severidad CRÍTICO/MEDIA/BAJA y búsqueda por test. Esfuerzo 3 h.
- [ ] **DIFF-01** Diff visual entre snapshots (slider de tiempo, "antes/después" por candidato y región). Esfuerzo 4 h.
- [ ] **FCAST-INT-01** Forecast bayesiano interactivo: slider "% actas RLA pendientes" → P(2°) recalcula en cliente. Esfuerzo 6 h.
- [ ] **TG-BOT-01** Bot Telegram `@AuditoriaEG2026` que postea cambios ≥0.1 pp en margen o nuevo finding CRÍTICO. Esfuerzo 3 h.
- [ ] **API-01** Endpoint `/api/findings.json` y `/api/forecast.json` servidos desde mismo gh-pages para terceros consumidores. Esfuerzo 1 h.
- [ ] **HIST-01** Comparador 2026 vs 2021 vs 2016 (gráfico paralelo de ausentismo y curvas de impugnación). Esfuerzo 4 h.

### Sprint 3 — Diferenciación absoluta (~1 semana)
- [ ] **MESA-01** Mesa-a-mesa: ingestar universo JEE vía `/actas/observadas` + `/actas/{id}`. Walker departamento→provincia→distrito→actas. Ref: artvepa80/onpe-2026-forecast. Esfuerzo 6 h. Owner: Tony.
- [x] **MESA-02** Reconcile contable cross-endpoint (totales vs mesa/totales vs mapa-calor vs presidencial). 7 checks, 0 findings en captura 20260419T025134Z. ✓ 2026-04-18.
- [x] **RESEARCH-01** Endpoints mesa-a-mesa confirmados 2026-04-18: `/presentacion-backend/actas/observadas?pagina=N&tamanio=100&idAmbitoGeografico=1&idUbigeo={u}`, `/presentacion-backend/actas/{id}` (con lineaTiempo T/D/C/O/E), `/presentacion-backend/ubigeos/{departamentos,provincias,distritos}`. Limitación: `/actas/observadas` sólo universo JEE, no todas las mesas. Pendiente: Network tab `/main/acta-detalle/{id}` para confirmar votos-por-candidato-por-mesa.
- [ ] **MESA-03** Ampliar Worker allowlist a 3 nuevos paths (actas/observadas, actas/{id}, ubigeos/*). Esfuerzo 30 min. Owner: Tony.
- [ ] **MESA-04** Inspeccionar Network tab `/main/acta-detalle/{id}` en resultadoelectoral.onpe.gob.pe para confirmar endpoint con votos por candidato por mesa. Esfuerzo 30 min. Owner: Tony (manual, browser DevTools).
- [ ] **CALAG-MAP-01** Mapa de las 211 mesas no instaladas (CALAG): círculos en Lima con popup de electores afectados.
- [ ] **PROC-TL-01** Timeline procesal denuncia JNE→ONPE: hitos auto-actualizados desde `evidence/legal_references/`.
- [ ] **IPFS-01** IPFS pinning de cada captura → hash IPFS junto al SHA-256 (timestamp criptográfico irrefutable).
- [ ] **PERITO-01** Modo perito: ZIP firmado con captura + análisis + memorial, listo para Fiscalía.
- [ ] **I18N-01** Multi-idioma EN para visibilidad internacional.

### Sueño (sin fecha, requiere alineación)
- [ ] **ML-ANOM** Isolation forest sobre serie temporal para detectar saltos atípicos automáticamente.
- [ ] **NEEDLE** Dashboard tipo NYT Election Needle (aguja oscilante con confidence interval bayesiano).
- [ ] **NOTARY** Hash-chain pública firmada + publicada en blockchain (Polygon, gas mínimo).
- [ ] **PYPI** Empaquetar como `pip install electoral-audit` para reuso en Bolivia 2025 / Ecuador 2025 / Colombia 2027.
- [ ] **PEER** Peer-review formal con MIT Election Lab / Linzer / Mebane.
