# SPEC H<N> — <título corto imperativo>

**Autor:** <nombre humano>
**Fecha:** YYYY-MM-DD
**Severity propuesta:** CRÍTICO | MEDIA | BAJA | INFO

## Pregunta

<1 línea cuantificable. Si no es número → reformular>

## Hipótesis

- **H0:** <numérico bajo proceso limpio>
- **H1:** <numérico bajo anomalía>

## Dato esperado

- Métrica: <pct | conteo | ratio | z-score>
- Universo: 92,766 mesas (o subset declarado)
- Filtros: <estado_acta, prefix, depto, etc>
- Umbral publicable: **p < 1e-6** (o justificar otro)

## Método propuesto

- Test: <z-test 2-prop | binomial exacto | χ² | MW-U | Cohen h>
- Paper: <key de `memory/reference_papers_forenses.md`>
- Corrección múltiple: <Bonferroni | Benjamini-Hochberg | none>
- Probabilidades <1e-15: usar `binom.logsf` (ver `memory/feedback_logsf_underflow.md`)

## Limitaciones previsibles

- <lim 1>
- <lim 2>

## Anti-ataque esperado

- <contra-argumento 1 + respuesta>
- <contra-argumento 2 + respuesta>

## Criterio de publicación

Se publica si:
- [ ] p < umbral
- [ ] effect size documentado
- [ ] limitaciones declaradas (≥2)
- [ ] anti-ataque preparado (≥2)
- [ ] paper del registry
- [ ] regla oro: "anomalía que ONPE debe explicar"

## Flujo (no editar)

1. data-forensic → `reports/raw_findings/raw_h<N>_<ts>.json`
2. stats-expert → `reports/stat_findings/stat_h<N>_<ts>.json`
3. audit-narrator → `reports/narratives/HALL-0420-H<N>/{technical,scientific,citizen}.md`
4. humano aprueba → `sync_findings_v2.py` + IPFS pin
