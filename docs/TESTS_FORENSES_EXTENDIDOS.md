# Tests Forenses Extendidos — EG2026 Perú

Documento técnico de los 4 tests forenses adicionales (M1-M4) diseñados para
detectar manipulación sofisticada difícil de ver con tests clásicos (Benford,
reconciliación, velocidades).

**Fecha:** 2026-04-17
**Corte:** ONPE 92.91%
**Responsable técnico:** Jack Aguilar (Neuracode). Aporte ciudadano, sin afiliación.

---

## M1 — Test de Último Dígito (Mebane 2006 / Beber & Scacco 2012)

### Fundamento

Bajo conteo genuino a gran escala, el último dígito de los vote counts debe
distribuirse uniformemente (p=0.1 cada dígito). Manipulación manual introduce:
- Preferencia por dígitos "redondos" (0, 5).
- Aversión a dígitos consecutivos idénticos.
- Sesgos sistemáticos detectables con chi-cuadrado.

**Referencias:**
- Mebane, W. (2006). *Election Forensics: Vote Counts and Benford's Law*.
- Beber, B. & Scacco, A. (2012). *What the Numbers Say: A Digit-Based Test for
  Election Fraud*. Political Analysis, 20(2), 211-234.

### Aplicación

- **Granularidad:** 26 regiones × 5 candidatos = 130 observaciones.
- **Filtro:** counts ≥ 10 (requisito de 2+ dígitos).
- **Inferencia:** chi-cuadrado contra uniforme, alpha = 0.05, bilateral.

### Resultado

| Candidato | n | chi2 p | fracción 0/5 | p(round) | Veredicto |
|-----------|---|---------|--------------|----------|-----------|
| Fujimori | 26 | 0.403 | 0.154 | 0.556 | **CONFORME** |
| López Aliaga (RLA) | 26 | 0.550 | 0.115 | 0.281 | **CONFORME** |
| Nieto | 26 | 0.954 | 0.192 | 0.922 | **CONFORME** |
| Belmont | 26 | 0.231 | 0.192 | 0.922 | **CONFORME** |
| Sánchez | 26 | 0.338 | 0.231 | 0.695 | **CONFORME** |
| POOLED | 130 | 0.128 | — | — | **CONFORME** |

**Finding M1: INFO** — No se detecta adulteración manual a escala regional.

### Caveat honesto

Con n=26 por candidato, el poder estadístico es limitado. Un resultado
"CONFORME" **no descarta** manipulación a menor granularidad (acta, mesa).
Por eso solicitamos mesa-a-mesa en M3.

---

## M2 — Autocorrelación Espacial (Moran's I)

### Fundamento

Moran's I mide clustering espacial de una variable sobre una matriz de
vecindad. Un I > E[I] = −1/(n−1) con p<0.05 indica que valores altos
(o bajos) se agrupan geográficamente más de lo esperable bajo aleatoriedad.

**Referencias:**
- Moran, P. A. P. (1950). *Notes on continuous stochastic phenomena*.
  Biometrika, 37(1/2), 17-23.
- Anselin, L. (1995). *LISA: Local Indicators of Spatial Association*.
  Geographical Analysis, 27(2), 93-115.

### Aplicación

- **Matriz W:** queen contiguity binaria, fila-estandarizada, 25 regiones
  (Extranjero excluido por no tener adyacencia geográfica).
- **Inferencia:** permutación 999 iteraciones (seed 20260417).
- **Alpha:** 0.05 bilateral.

### Resultado

| Variable | Moran's I | p-valor | Veredicto |
|----------|-----------|---------|-----------|
| tasa_impugnacion | +0.261 | 0.051 | ALEATORIO (borderline) |
| **share_RLA** | **+0.317** | **0.011** | **CLUSTERING+** |
| share_Sánchez | +0.026 | 0.854 | ALEATORIO |
| pct_fuera | +0.229 | 0.088 | ALEATORIO |

**Bivariado RLA × impugnación:** I = −0.023, p = 0.837 → **ALEATORIO**.

### Interpretación honesta

1. **RLA tiene clustering geográfico fuerte (p=0.011).** Esto refleja su base
   electoral concentrada en zonas específicas (Lima metropolitana, costa
   norte). Es normal en cualquier partido con fuerza regional.
2. **Sánchez no clusteriza (p=0.854).** Su apoyo es disperso geográficamente.
   Políticamente revelador, no sospechoso.
3. **La tasa de impugnación NO co-clusteriza con el share de RLA** (p=0.837).
   Las regiones vecinas con alta impugnación no son las pro-RLA. Esto
   **debilita** la hipótesis de focalización geográfica dirigida contra RLA.

**Finding M2: MEDIA** — Clustering espacial propio de RLA (su base regional),
pero sin evidencia de clustering adverso dirigido.

### Caveat honesto

n=25 regiones. No significativo al nivel departamental **no descarta**
clustering a escala provincial o distrital. Requiere M3.

---

## M3 — Granularidad Mesa-a-Mesa (PENDIENTE)

### Fundamento

Replicar M1 y M2 a escala mesa (≈90,000 mesas en Perú) aumenta n por 3 órdenes
de magnitud y permite detectar manipulación localizada invisible a nivel
regional.

### Estado

**PENDIENTE: datos no accesibles vía API pública de ONPE.**

La interfaz `resultadoelectoral.onpe.gob.pe` es una SPA (Single Page
Application) que consume endpoints backend no documentados públicamente. El
detalle mesa-a-mesa existe internamente (se usa para generar la pantalla de
búsqueda por mesa) pero no se expone como dataset descargable.

### Pedido formal (memorial al Fiscal, variable #4)

Solicitar a ONPE bajo apercibimiento:
- Dump completo de resultados mesa-a-mesa en formato CSV/JSON.
- Incluir: estado de cada mesa (contabilizada / enviada JEE / pendiente /
  impugnada / observada / anulada), votos por candidato, motivo si
  corresponde.
- Cadena de custodia: hash SHA-256, timestamp, firma digital.

---

## M4 — Motivos de Rechazo/Impugnación de Actas (PENDIENTE)

### Fundamento

Si los errores que dejan fuera a actas favorables a RLA se concentran en
motivos específicos (cifras mal escritas, firmas faltantes, errores de
totalización), y esos motivos son más frecuentes en zonas pro-RLA que en
otras, es señal de sesgo operativo (involuntario o no).

### Estado

**PENDIENTE: ONPE no expone clasificación de motivos en resultados
electorales.**

El JEE (Jurado Nacional de Elecciones) procesa las impugnaciones y tiene
esta clasificación, pero la publica caso-por-caso en resoluciones individuales
(Res. 0180-2025, 0182-2025, etc.), no como dataset agregado.

### Pedido formal (memorial al Fiscal, variable #5)

Solicitar a JEE bajo apercibimiento:
- Base consolidada de todas las actas enviadas a JEE (5,555 según último
  corte), con:
  - Motivo de impugnación/observación.
  - Mesa, distrito, provincia, departamento.
  - Votos afectados por candidato.
  - Fecha de ingreso y fecha de resolución.
  - Sentido de resolución (aprobada, anulada, parcial).

---

## Síntesis

| Test | Resultado | Severidad | Requiere escalamiento |
|------|-----------|-----------|----------------------|
| M1 — Último dígito regional | CONFORME los 5 candidatos | INFO | Sí (M3) |
| M2 — Moran's I global | RLA clusteriza (base propia); RLA×impug no co-clusteriza | MEDIA | Sí (M3) |
| M3 — Mesa-a-mesa | Pendiente (data no pública) | N/A | Apercibimiento ONPE |
| M4 — Motivos de rechazo | Pendiente (data no pública consolidada) | N/A | Apercibimiento JEE |

### Honestidad estadística obligatoria

- **M1 no detecta manipulación.** Esto NO prueba que no exista a menor escala.
- **M2 confirma que RLA tiene base concentrada** (lo cual es normal), pero
  **no encuentra co-clustering con impugnación** (lo cual debilita la tesis
  de focalización geográfica adversa).
- **M3 y M4 son los que realmente pueden dar evidencia dura**, pero dependen
  de que el Fiscal compela a ONPE/JEE a entregar los datasets.

Esto es lo que aguanta peritaje contraparte: reportamos lo que encontramos,
incluyendo lo que no confirma la tesis del cliente. El memorial pide peritaje
y datos; no imputa dolo.

---

**Documento reproducible.** Código fuente:
- `src/analysis/last_digit_forensic.py`
- `src/analysis/spatial_cluster.py`

Outputs:
- `reports/last_digit.json`
- `reports/spatial_cluster.json`

CC-BY-4.0 · Neuracode · Aporte ciudadano sin retribución.
