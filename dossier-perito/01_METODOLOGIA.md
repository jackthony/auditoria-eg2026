# Metodología — Auditoría EG2026

Marco metodológico siguiendo el **Election Forensics Toolkit**
(Mebane & Hicken, University of Michigan, USAID 2017). Solo métodos
peer-reviewed. Seeds fijos. Código reproducible.

---

## Fuentes de datos

### Primaria

- **ONPE API / web oficial** `resultadoelectoral.onpe.gob.pe`.
- Captura automatizada cada ~5 min desde 2026-04-13.
- Snapshots JSON crudos con timestamp UTC.
- Hash SHA-256 por snapshot (cadena custodia).

### Secundaria (contexto, no análisis estadístico)

- JNE resoluciones públicas.
- INEI capa sociodemográfica 2024.
- Reportajes verificados: Ojo Público, La República Verificador,
  Gestión, El Comercio.

---

## Métodos estadísticos aplicados

### 1. Reconciliación interna (A0, R1)

- **Método:** igualdad matemática. Σ(regional) = nacional para cada métrica
  publicada (totalActas, contabilizadas, enviadasJee, pendientesJee).
- **Criterio:** cualquier diff ≠ 0 es inconsistencia.
- **Severidad:** ALTA si |diff| × votos_promedio_acta > margen final.

### 2. Tasa de impugnación (A1, A2)

- **Método:** z-test sobre proporciones, z = (p_region − p_nacional) /
  sqrt(p(1−p)/n). Significancia bilateral α=0.05.
- **Corrección múltiple:** Bonferroni para n=26 regiones (α'=0.0019).

### 3. Benford 1er dígito (C1)

- **Método:** Chi-cuadrado contra distribución log(1 + 1/d).
- **Cita:** Benford (1938); Mebane (2006) para election forensics.
- **Limitación:** requiere counts >> 10 para ser válido; agregados
  nacionales sí lo cumplen.

### 4. Último dígito Mebane/Beber-Scacco (M1)

- **Método:** Chi-cuadrado contra uniforme (p=0.1 cada dígito).
  Test adicional: fracción 0/5 (sesgo a dígitos redondos).
- **Citas:**
  - Mebane, W. (2006). *Election Forensics: Vote Counts and Benford's Law*.
  - Beber, B. & Scacco, A. (2012). *What the Numbers Say: A Digit-Based
    Test for Election Fraud*. Political Analysis 20(2): 211–234.

### 5. Correlación y bootstrap (G1)

- **Método:** Pearson + Spearman (robusto a outliers).
- **Inferencia:** bootstrap 1,000 iteraciones para CI95.
- **Seed:** 20260417.

### 6. Mann-Whitney U (H1, H2)

- **Método:** test no paramétrico para comparar velocidades pre/post
  cruce Sánchez>RLA. Ventanas ±6h y ±12h.
- **Cita:** Mann & Whitney (1947).

### 7. Change-point detection (H4 pre-registro)

- **Método:** PELT (Pruned Exact Linear Time, Killick et al. 2012).
- **Cita:** Killick, R. et al. (2012). *Optimal Detection of Changepoints
  with a Linear Computational Cost*. JASA 107(500): 1590-1598.

### 8. Moran's I espacial (M2)

- **Método:** Moran's I global con permutación 999 iteraciones. Matriz W:
  queen contiguity binaria, fila-estandarizada. 25 regiones (Extranjero
  excluido por no adyacencia). Bivariado: Moran's I bi(X, Y) con la misma W.
- **Citas:**
  - Moran, P. A. P. (1950). *Notes on continuous stochastic phenomena*.
    Biometrika 37(1/2): 17-23.
  - Anselin, L. (1995). *LISA: Local Indicators of Spatial Association*.
    Geographical Analysis 27(2): 93-115.
- **Seed permutación:** 20260417.

### 9. Modelo bayesiano (F1)

- **Método:** Dirichlet-Multinomial jerárquico con prior Beta para el
  proceso JEE. n=10,000 simulaciones Monte Carlo.
- **Escenarios:** central (ratio histórico JEE), mixto (escenario
  adversarial con ratio 1.5× pro-RLA).
- **Citas:**
  - Linzer, D. (2013). *Dynamic Bayesian Forecasting of Presidential Elections*.
    JASA 108(501): 124-134.
  - NYT Needle methodology (2016+).
- **Seed:** 20260417.

### 10. Regresión con controles (H1, H2 pre-registro)

- **Método:** OLS con controles sociodemográficos INEI (ingreso, urbanidad,
  densidad). Bootstrap CI95 + permutación 999 para validar.
- **Cita:** White (1980) robust SE.

---

## Niveles de significancia

- **α por defecto:** 0.05 bilateral.
- **α pre-registrado H1-H5:** 0.01 (más estricto para evitar falsos positivos).
- **Corrección multiplicidad:** Bonferroni cuando se testea múltiples
  regiones o candidatos.

---

## Seeds de aleatoriedad

Fijo: **20260417** (YYYYMMDD, fecha pre-registro).

Aplica a:
- `random.seed(20260417)` en simulaciones Monte Carlo.
- `numpy.random.seed(20260417)` en permutaciones.
- `pandas.DataFrame.sample(random_state=20260417)` en bootstrap.

---

## Software y versiones

- Python 3.11.x
- numpy 1.26+
- scipy 1.11+
- pandas 2.0+
- sin dependencias propietarias.

Código: `src/analysis/*.py` en repositorio público.

---

## Reproducibilidad

Cualquier tercero reproduce bit-a-bit:

```bash
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
pip install -r requirements.txt
py src/process/build_dataset.py
py -m src.analysis.run_all
# Outputs esperados idénticos a dossier-perito/reports/
```

---

## Limitaciones metodológicas

Ver `05_LIMITACIONES.md`.
