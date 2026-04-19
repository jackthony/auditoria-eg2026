# Señales exploratorias — EG2026

> **Estatus:** estas son **señales estadísticas complementarias**, no findings publicables. Se mueven fuera de la portada hasta contar con:
> - Corrección de múltiples tests (Bonferroni/FDR) aplicada en bloque.
> - Análisis de sensibilidad (distintos priors, ventanas, parámetros).
> - Revisión de pares.
>
> Referirse a `METHODOLOGY.md` y `reports/findings.json` (3 findings sólidos publicados).

---

## A1 · Impugnación anómala en "Extranjero" (MEDIA)

Una región supera ±2σ de la tasa promedio regional (7.29% ± 4.88%): Extranjero con 26.35% (z=+3.90).

**Limitación:** Extranjero es estructuralmente distinto (logística, ubigeo, densidad consular) y suele ser outlier en todas las elecciones. Señal esperada, no anómala.

## A2 · Lima+Callao vs resto: diferencia de impugnación (MEDIA)

- Lima+Callao: 4.32% · Resto: 7.22% · z=−17.38, p≈0.
- La asimetría **no perjudica** a candidatos con mayor voto en Lima+Callao.

**Limitación:** Patrón histórico recurrente en Perú (infraestructura y capacitación desigual). Significancia estadística alta ≠ anomalía interpretativa.

## C1 · Benford (primer dígito, agregado) — INFO

- Pool 5 candidatos × 26 regiones (n=130): χ²=11.91, p=0.155. No se rechaza conformidad.

**Limitación documentada (Deckert/Myagkov/Ordeshook 2011):** Benford-1 en datos electorales tiene alta tasa de falsos positivos y falsos negativos. Se reporta como control, no como evidencia.

## D1 · Artefactos de caché en tracking — INFO

72 oscilaciones pct↓↑ idénticas: condición de carrera del proxy caché, **no** movimiento real.

## D2 · Sin saltos temporales anómalos — INFO

Ningún delta entre cortes supera 0.5pp en 117 cortes.

## D3 · Cruce Sánchez↔RLA único — INFO

1 cambio de signo, consistente con ingreso de actas rurales tras Lima y extranjero.

## G1 · Correlación impugnación–share_RLA (MEDIA → DOWNGRADE)

- Pearson r=0.506, p=0.0083 (n=26 regiones).
- **Spearman r=0.14, p=0.49** (no significativo).
- **Bootstrap CI95 = [−0.32, +0.87]** (cruza cero).

**Interpretación honesta:** la asociación es sensible a outliers (Lima, Extranjero). No se puede afirmar correlación robusta.

## H1 · H2 · Cambio de velocidad JEE en cruce (MEDIA)

- ±6h: +182.6 vs +92.4 actas/h (Mann-Whitney p=0.0127).
- ±12h: +169.0 vs +76.4 actas/h (ratio 0.45×).

**Limitación:** correlación temporal con el momento del cruce puede reflejar procesamiento natural (batch cierre de impugnaciones), no causalidad. Falta CUSUM / changepoint bayesiano para decidir.

## M1 · Último dígito uniforme — INFO

5/5 candidatos conformes a uniforme (χ² p>0.05).

## M2 · Clustering espacial (Moran's I) — MEDIA

- tasa_impugnacion: I=0.27, p=0.035.
- share_rla: I=0.32, p=0.011.
- pct_fuera: I=0.26, p=0.041.
- Bivariado rla↔impugnación: I=−0.03, p=0.79 (**aleatorio**, contradice narrativa fraude).

**Limitación:** n=26 regiones está bajo el mínimo recomendado (30–50) para estadística espacial robusta.

## M3 · IsolationForest sobre serie temporal (MEDIA)

- 30 saltos atípicos (contamination=0.05, n=117), 6 por candidato.

**Limitación crítica:** `contamination=0.05` **fija** el 5% de anomalías por construcción. Reportar con 0.02 y 0.10 antes de reintroducir como finding.

---

## Pendiente para ascenso a findings públicos

- [ ] Aplicar FDR (Benjamini-Hochberg) sobre los 16+ p-valores del pipeline.
- [ ] Sensitivity analysis: Bayesiano con prior uniforme vs Dirichlet(votos+1).
- [ ] ML-anomalies con 3 valores de contamination.
- [ ] CUSUM / Bayesian changepoint en H1/H2.
- [ ] Revisión de pares (MIT Election Lab / Mebane / Linzer).
