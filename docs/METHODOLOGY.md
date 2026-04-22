# METHODOLOGY.md — Metodología

## Marco

Election forensics (Mebane et al.). Objetivo: detectar desviaciones estadísticas vs proceso limpio. NO "probar fraude". Cada finding declara H0, método, p-value, limitaciones.

## Tests aplicados (blindados 2026-04-21)

| Test | Paper | Finding | Uso |
|------|-------|---------|-----|
| z-test 2-prop Wilson | Newcombe 1998. Statist. Med. 17:873-890 | H1, H4 | Comparar proporciones |
| Cohen's h | Cohen 1988. Stat Power Analysis 2ed | H2, H4, H12 | Effect size |
| Bootstrap IC95 | Efron-Tibshirani 1993. Intro to Bootstrap | H4 | IC no paramétrico |
| Clopper-Pearson | Clopper-Pearson 1934. Biometrika 26:404 | H12 | IC binomial exacto |
| Binomial exacto (logsf) | — | H9, H12 | P(X≥k) para p<1e-15 |
| χ² homogeneidad | Fisher 1925 | H1, H4 | Test tabla contingencia |
| Bonferroni | Bonferroni 1936 | H1 | Corrección múltiple |
| Mann-Whitney U | Mann-Whitney 1947. Annals Math Stat 18:50 | H3 | No paramétrico |
| Klimek 2D | Klimek et al 2012. PNAS 109:16469 | H4 (negativo) | Reportado por honestidad |

## Reglas numéricas

- Probabilidades <1e-15 → `scipy.stats.binom.logsf(k-1, n, p)`. Nunca `1 - cdf` (underflow float64).
- Reportar en log10 cuando |log10 P| > 20.
- Bootstrap B=10,000 mínimo para IC95.

## Métodos prohibidos

| Método | Razón | Refutación |
|--------|-------|------------|
| Benford-1 standalone | Falsos positivos en datos electorales | Deckert-Myagkov-Ordeshook 2011. Political Analysis 19(3):245 |
| Beber-Scacco último dígito | Artefacto power-law mesas pequeñas | Mebane 2013 caveats |
| Mesas gemelas | Sin paper directo validable | — |

## Severidades

| Nivel | Criterio |
|-------|----------|
| CRÍTICO | p<1e-6 + efecto grande + impacto en resultado |
| MEDIA | p<0.001 + efecto moderado |
| BAJA | p<0.05 |
| INFO | sin anomalía |

## Limitaciones globales

1. Solo data pública ONPE. No acceso a logs STAE/ODPE.
2. No-adversarial: adversario sofisticado puede pasar tests.
3. Causalidad no probada — solo concentración estadística.
4. Cada finding documenta sus limitaciones específicas.

## Regla de oro pública

"Anomalía estadística que ONPE debe explicar". Nunca "fraude", "trampa", "robo".
