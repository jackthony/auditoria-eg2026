# Pre-registro de Hipótesis — EG2026 Perú

Pre-registro formal de hipótesis H1–H5 **antes** de contar con toda la data
ONPE/JEE bajo apercibimiento. Previene acusación contraparte de que los
métodos se ajustaron ex-post ("p-hacking", "cherry-picking").

**Fecha pre-registro:** 2026-04-17 · Hora sistema ONPE: 93.17% corte.
**Autor:** Jack Aguilar (Neuracode). Aporte ciudadano, sin afiliación.

---

## Cadena de custodia del pre-registro

| Documento | SHA-256 |
|-----------|---------|
| `docs/HIPOTESIS_CIENTIFICAS.md` | `0aa1e92f7acad561941b52d33eb7ca98ad3057a86676be183cb93ab946c7f121` |
| `docs/TESTS_FORENSES_EXTENDIDOS.md` | `70d9bc91b4a96e93cbde739362427bb404ce683b7e1b14eb906bac60b9d475e0` |

**Commit git inmediato previo:** `413d6a1971aace257328b7b88b0647ac73185aa9`
(branch `main`, remoto `jackthony/auditoria-eg2026`).

Cualquier modificación posterior a este documento deja trazabilidad en
`git log`. Verificación por terceros: clonar repo, reproducir hashes.

---

## Hipótesis pre-registradas (resumen)

| ID | Enunciado | Test | Alpha | Criterio rechazo |
|----|-----------|------|-------|------------------|
| **H1** | Distribución material electoral presenta fallas concentradas geográficamente correlacionadas con perfil electoral | Regresión lineal con controles sociodemográficos + bootstrap CI95 + permutación 999 | 0.01 | p<0.01 Y CI95 excluye 0 |
| **H2** | Tasa de actas fuera de conteo (JEE) no es homogénea entre regiones y correlaciona con share de candidato | Regresión con controles + Moran's I bivariado | 0.01 | Coef p<0.01 controlando confundidores Y Moran's I bivariado p<0.01 a nivel mesa |
| **H3** | Errores de transcripción acta-sistema presentan asimetría por candidato | Wilcoxon simetría + KS 2-sample + test de media | 0.01 | p<0.01 en ≥1 distribución |
| **H4** | Tiempos de digitación reflejan procesos consistentes; desviaciones coinciden con eventos políticos | Change-point detection (PELT) + autocorrelación temporal | 0.01 | Change-point detectado p<0.01 en ventana ±6h de evento, ratio velocidad >2× o <0.5× |
| **H5** | Conflicto documental proveedor-autoridad permite contrastar dos fuentes independientes | Análisis documental + consistencia temporal + consistencia cuantitativa | N/A (cualitativo) | Discrepancia >5% cifras reconciliables Y diferencia >24h en ≥3 hitos |

---

## Compromiso de honestidad

Al firmar este pre-registro, el autor se compromete a:

1. **Ejecutar los tests con los métodos exactos descritos**, sin cambio de
   variables, umbrales, ni controles después de ver resultados.
2. **Reportar resultados adversos**. Si una hipótesis H0 no se rechaza,
   se publica; si contradice la narrativa del cliente (RLA), se publica.
3. **No modificar criterios de rechazo post-hoc**. Alpha 0.01 fijo,
   criterios conjuntos fijos.
4. **No añadir hipótesis ad-hoc** cuando lleguen los datos para "rescatar"
   resultados. Toda H posterior será marcada claramente como exploratoria.
5. **Publicar código y seed usado**. Reproducibilidad bit-a-bit obligatoria.

---

## Seeds de aleatoriedad

- Permutation tests: `20260417` (YYYYMMDD fecha pre-registro).
- Bootstrap: `20260417`.
- Simulaciones Monte Carlo: `20260417`.

Cualquier desviación de estos seeds exige nota explícita en el reporte.

---

## Hallazgos ya obtenidos (antes del pre-registro, exploratorios)

Los siguientes hallazgos ya fueron ejecutados con data parcial (ONPE 93.17%):

| ID | Resultado | Status |
|----|-----------|--------|
| R1 | Reconciliación Σ regional vs nacional: coincide dentro redondeo | INFO |
| A0 | Discrepancia interna ONPE: 42 actas no reconcilian (1.6× margen) | **ALTA** |
| A1 | Extranjero tasa impugnación 24.11%, z=+3.66 | MEDIA |
| C1 | Benford primer dígito conforme | INFO |
| F1 | Modelo bayesiano: P(RLA>Sánchez) = 42.6% central | CRÍTICO |
| G1 | Correlación impug × share_RLA: borderline (Pearson sí, Spearman no) | MEDIA |
| H1 | Cambio velocidad JEE ±6h cruce (Mann-Whitney p=0.013) | MEDIA |
| H2 | Desaceleración post-cruce 0.45× | MEDIA |
| M1 | Último dígito regional conforme | INFO |
| M2 | RLA clusteriza (p=0.011); bivariado RLA×impug aleatorio | MEDIA |

**Declaración explícita:** estos hallazgos son *exploratorios* (data incompleta,
método refinado iterativamente durante el corte). Los tests H1–H5 bajo el
pre-registro son *confirmatorios* y se ejecutarán con data completa cuando
ONPE/JEE la entreguen bajo apercibimiento.

---

## Verificación independiente

Cualquier tercero puede verificar este pre-registro:

```bash
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
git checkout 413d6a1
sha256sum docs/HIPOTESIS_CIENTIFICAS.md docs/TESTS_FORENSES_EXTENDIDOS.md
# debe coincidir con los hashes de este documento
```

---

**Documento reproducible.** Licencia CC-BY-4.0. Autoría Neuracode ·
Jack Aguilar (aporte ciudadano, sin retribución, sin afiliación política).
