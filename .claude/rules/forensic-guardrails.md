# Forensic Guardrails — auditoria-eg2026

> Reglas **inviolables** para todo agente que toca findings, stats o narrativa.

## Invariantes numéricos

| Ítem | Valor | Penalidad si se viola |
|---|---|---|
| Universo mesas | **92,766** (88,063 norm + 4,703 esp 900k+) | Finding inválido, rechazar |
| DB autoritativa | `reports/hallazgos_20260420/eg2026.duckdb` | No leer de otra fuente |
| Mapping prefix→depto | ONPE alfabético + Callao=24 | NO usar INEI |
| Probabilidades <1e-15 | `scipy.stats.binom.logsf(k-1, n, p)` | NUNCA `1 - cdf` (underflow float64) |
| Severidad CRÍTICO | p<1e-6 + efecto grande + impacto resultado | No inflar |

## Paper registry (set cerrado)

Solo citar de `memory/reference_papers_forenses.md`. 8 permitidos:

- newcombe1998 · cohen1988 · efron1993 · clopper1934
- klimek2012 · mannwhitney1947 · bonferroni1936 · fisher1925

**Prohibidos:** Benford-1 standalone, Beber-Scacco último dígito, mesas gemelas.

## Lenguaje público

| ❌ Prohibido | ✅ Permitido |
|---|---|
| "fraude" | "anomalía que ONPE debe explicar" |
| "trampa", "robo" | "desviación estadística" |
| "demostrado" | "incompatible con H0 a p=X" |
| "seguro que" | "evidencia fuerte de que" |

**Regla oro:** causalidad NUNCA probada. Solo **concentración estadística**.

## Checklist finding publicable

- [ ] p < umbral declarado en spec
- [ ] Effect size (Cohen h, OR, z) reportado
- [ ] ≥2 limitaciones declaradas
- [ ] ≥2 contra-ataques anticipados con respuesta
- [ ] Paper citado del registry
- [ ] Spec `docs/specs/H<N>.md` existe antes del raw_finding
- [ ] raw + stat JSON en `reports/{raw,stat}_findings/`
- [ ] DB SHA-256 en stat_finding

## Aplicación

Todo agente (`data-forensic`, `stats-expert`, `audit-narrator`, `forensic-challenger`, `storytelling-pe`, `memorial-fiscal`) lee este archivo. Violación → detener pipeline, reportar al humano.
