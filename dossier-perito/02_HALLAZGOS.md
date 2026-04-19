# Hallazgos — Finding-by-finding

Cada finding incluye: ID, severidad, descripción, método, resultado numérico,
interpretación honesta, lo que NO implica.

---

## A0 — Inconsistencia de agregación ONPE [MEDIA]

### Resultado

Snapshot 2026-04-17T08:41:14Z, corte 93.17%:

| Métrica | Nacional | Σ Regional | Diff |
|---------|----------|------------|------|
| totalActas | 92,766 | 92,766 | 0 ✓ |
| contabilizadas | 86,438 | 86,434 | **−4** |
| enviadasJee | 5,555 | 5,538 | **−17** |
| pendientesJee | 773 | 794 | **+21** |

### Nota metodológica (post red-team)

Los 4 campos están algebraicamente ligados: `totalActas = contabilizadas +
enviadasJee + pendientesJee`. Por tanto los diffs están acoplados (la suma
ingenua de |diffs| triplicaría la magnitud real). **Métrica correcta:**
`actas_movidas = max(|diff|) = 21 actas` — es el mínimo número de actas que
deben reclasificarse para reconciliar.

- Votos promedio por acta = ~218.
- **Votos potenciales en zona gris: ~4,582 (ratio 0.78× del margen 5,875).**

### Interpretación honesta

La UI/API de ONPE no reconcilia consigo misma. Puede deberse a:
- Timestamp desalineado entre endpoints.
- Categoría no contabilizada en desagregado.
- Actas migrando entre estados durante el cálculo.

### Lo que NO implica

**NO prueba error en conteo de votos.** El autor del post ciudadano original
hizo ese salto lógico; no se sostiene. Agregador UI ≠ pipeline de conteo.

### Acción requerida

ONPE debe explicar formalmente. Si el motivo es timestamp, publicar
timestamps separados por endpoint.

---

## A1 — Tasa impugnación Extranjero anómala [MEDIA]

### Resultado

- Extranjero: 24.11% impugnación.
- Nacional: 5.99%.
- z-statistic: +3.66.
- p-valor: <0.0005 (bilateral).

### Interpretación honesta

Extranjero tiene patrón muy distinto al nacional. Puede deberse a:
- Volumen bajo (sensibilidad a outliers).
- Procesos logísticos distintos (consulados).
- Dificultad material para revisar físicamente las actas.

### Lo que NO implica

No prueba sesgo deliberado. Sí amerita explicación operativa de ONPE.

---

## A-AUS-3 — Ratio afectados vs margen [ALTA procesal]

### Resultado

- Electores afectados oficialmente en Lima por CALAG/Galaga: 63,300.
- Margen Sánchez−RLA al corte 93.474% (2026-04-18): **13,624** (histórico al 93.17%: 5,898).
- **Ratio vigente: 4.64×** (ratio histórico: 10.73×).

### Interpretación honesta

El número oficial (no la denuncia RLA de 600K) de afectados supera en
4.64× al margen vigente que define la elección. Si incluso un 21% de esos electores
hubiera preferido a RLA por encima de Sánchez, el margen se invierte.

### Lo que NO implica

No prueba fraude. **Sí abre el estándar del Artículo 363 Ley 26859**
(nulidad parcial por evento que *podría* alterar el resultado).

---

## A-AUS-1 — Ausentismo 2026 vs 2016 [MEDIA]

### Resultado

| Elección | Ausentismo |
|----------|-----------|
| 2016 (pre-pandemia) | 18.21% |
| 2021 (durante pandemia) | 29.15% |
| 2026 proy (post-pandemia) | 26.16% |

- Delta 2026 vs 2016: **+7.95 pp** = ~3.0M electores adicionales no votaron.
- Delta 2026 vs 2021: −2.99 pp.

### Interpretación honesta

Post-pandemia no volvió a niveles pre-pandemia. Pero es multifactorial:
desconfianza institucional, fallas operativas (CALAG, STAE), clima, etc.

### Lo que NO implica

No atribuible a una sola causa. Narrativa "subió post-pandemia vs pandemia"
NO se sostiene (A-AUS-2).

---

## F1 — Forecast bayesiano [CRÍTICO]

### Resultado

Modelo Dirichlet-Multinomial + Beta prior JEE, n=10,000 simulaciones:

- **P(RLA supera Sánchez) central: 42.6%.**
- P(RLA supera Sánchez) mixto: 42.2%.
- Margen final p50 central: +5,773 a +3,800 (oscila con corte).
- Margen final p5−p95: [−4,100, +12,500] aproximadamente.

### Interpretación honesta

Cerca de empate estadístico. La distribución posterior es bimodal:
hay masa de probabilidad relevante en ambos escenarios de ganador.

### Lo que NO implica

No predice el ganador. Cuantifica la incertidumbre condicional a la data
disponible al corte 93.17%.

---

## G1 — Correlación impugnación × share RLA [MEDIA, NO ROBUSTA]

### Resultado

- Pearson r = 0.477, p = 0.014.
- Spearman r = 0.20, p = 0.34 (**no significativo**).
- Bootstrap CI95: incluye 0.

### Interpretación honesta

La correlación existe en media pero está dominada por Lima y Extranjero
(outliers). Con métodos robustos, desaparece.

### Lo que NO implica

NO es evidencia robusta de focalización adversa. Es hallazgo **borderline**
que debe replicarse a nivel mesa (M3 pendiente).

---

## H1, H2 — Velocidad JEE pre/post cruce [MEDIA]

### Resultado H1

- Ventana ±6h alrededor del cruce Sánchez>RLA.
- Velocidad pre: +182.6 actas/h.
- Velocidad post: +92.4 actas/h.
- Mann-Whitney p = 0.013.

### Resultado H2

- Ventana ±12h.
- Ratio velocidades post/pre: 0.45×.
- Actas acumuladas pre: +1,522. Post: +556.

### Interpretación honesta

Hubo inflexión. Dos interpretaciones alternativas:
1. **Procesamiento natural** (actas más "fáciles" primero, remanentes más difíciles).
2. **Cambio de política de impugnaciones** post-cruce.

### Lo que NO implica

**H2 CONTRADICE narrativa viral** de "aceleración post-cruce". Hubo
DESACELERACIÓN. Reportar lo opuesto habría sido falso.

---

## M1 — Último dígito [INFO]

### Resultado

Chi-cuadrado contra uniforme por candidato:

| Candidato | chi2 p | Veredicto |
|-----------|--------|-----------|
| Fujimori | 0.403 | CONFORME |
| López Aliaga (RLA) | 0.550 | CONFORME |
| Nieto | 0.954 | CONFORME |
| Belmont | 0.231 | CONFORME |
| Sánchez | 0.338 | CONFORME |
| Pooled | 0.128 | CONFORME |

### Interpretación honesta

No se detecta adulteración manual a escala regional.

### Lo que NO implica

**NO descarta manipulación a menor granularidad** (mesa). Con n=26 por
candidato, el poder estadístico es limitado. Se requiere M3 (mesa-a-mesa).

---

## M2 — Moran's I espacial [MEDIA]

### Resultado

| Variable | Moran's I | p-valor | Veredicto |
|----------|-----------|---------|-----------|
| tasa_impugnacion | +0.261 | 0.051 | ALEATORIO (borderline) |
| share_RLA | +0.317 | **0.011** | **CLUSTERING+** |
| share_Sánchez | +0.026 | 0.854 | ALEATORIO |
| pct_fuera | +0.229 | 0.088 | ALEATORIO |

Bivariado RLA × impug: **I = −0.023, p = 0.837 → ALEATORIO**.

### Interpretación honesta

1. RLA tiene clustering geográfico fuerte (base electoral concentrada).
   Normal.
2. Sánchez es disperso (apoyo geográfico diverso). Normal.
3. **La tasa impug NO co-clusteriza con share_RLA.** Debilita la hipótesis
   de focalización geográfica dirigida.

### Lo que NO implica

NO refuta completamente focalización — solo a nivel regional. A nivel
mesa puede existir (M3 pendiente).

---

## Findings INFO reportados por transparencia

- **R1:** Reconciliación Σ regional == nacional dentro redondeo.
- **C1:** Benford 1er dígito conforme.
- **D1-D3:** Captura temporal sin anomalías técnicas relevantes.
- **A-AUS-2:** Ausentismo 2026 < 2021 (pandemia).

---

**Todos los findings están en `reports/findings.json` con metadata completa.**
