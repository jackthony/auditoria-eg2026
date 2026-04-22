---
description: Corre pipeline completo para un finding H<N> — data-forensic → stats-expert → challenger → narrator → sync → IPFS pin
argument-hint: H<N> (ej. H12)
---

# /publish $ARGUMENTS

Pipeline full para **$ARGUMENTS**. Cero pasos manuales.

## Pre-check

1. Verificar que `docs/specs/$ARGUMENTS.md` existe. Si no → STOP + pedir al usuario crearlo desde `docs/specs/_TEMPLATE.md`.
2. Leer spec. Extraer: universo, filtros, método, umbral.
3. Leer `.claude/rules/forensic-guardrails.md` + `.claude/rules/spec-first.md`.

## Ejecución (secuencial, 1 agente por paso)

### Paso 1 — data-forensic
Invocar `data-forensic` con spec `docs/specs/$ARGUMENTS.md`.
Output: `reports/raw_findings/raw_${ARGUMENTS,,}_<tsUTC>.json`

### Paso 2 — stats-expert
Invocar `stats-expert` con raw_finding. Aplicar test del spec.
Output: `reports/stat_findings/stat_${ARGUMENTS,,}_<tsUTC>.json`

### Paso 3 — forensic-challenger
Invocar `forensic-challenger` con spec + raw + stat.
Output: `reports/challenges/$ARGUMENTS_<tsUTC>.md`

**Si veredicto ≠ SOBREVIVE → STOP.** Reportar al usuario. No avanzar.

### Paso 4 — audit-narrator
Solo si challenger dice SOBREVIVE.
Output: `reports/narratives/HALL-*/$ARGUMENTS/{technical,scientific,citizen}.md`

### Paso 5 — sync
`py scripts/sync_findings_v2.py`
Propaga a `reports/findings.json` + dashboard.

### Paso 6 — IPFS pin (opcional, requiere API keys)
Preguntar: "¿pin a Filebase+Pinata ahora? (y/n)"
Si y → `py scripts/pin_to_filebase.py --finding $ARGUMENTS`
Append CID a `reports/ipfs_cids.json`.

## Checklist final

- [ ] `docs/specs/$ARGUMENTS.md` existe
- [ ] `reports/raw_findings/raw_*.json` creado
- [ ] `reports/stat_findings/stat_*.json` creado
- [ ] `reports/challenges/*.md` con SOBREVIVE
- [ ] `reports/narratives/HALL-*/$ARGUMENTS/` (3 archivos)
- [ ] `reports/findings.json` sincronizado
- [ ] `docs/HALLAZGOS_VIGENTES.md` actualizado con fila nueva
- [ ] Commit atómico con mensaje `feat($ARGUMENTS): publish finding`

## Output final

Reporte al usuario con:
- Veredicto challenger
- p-value + effect size
- 3 paths de narrativa
- SHA-256 DB usado
- CID IPFS (si se pineó)
