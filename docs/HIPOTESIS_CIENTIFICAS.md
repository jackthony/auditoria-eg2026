# Hipótesis Científicas Testables — EG2026 Perú

Marco metodológico para investigación forense del proceso electoral EG2026.
Formulado siguiendo el estándar del **Election Forensics Toolkit**
(University of Michigan, Mebane & Hicken, USAID 2017) y adaptado al contexto
peruano 2026.

**Principio rector:** cada hipótesis se formula como afirmación **refutable**,
con variables observables, test estadístico, datos requeridos, criterio de
rechazo y evaluación explícita del riesgo de falsos positivos. **Ninguna
hipótesis presume culpables.** El que un test rechace H0 solo indica que el
dato es anómalo y requiere explicación formal por parte de la autoridad
electoral.

**Autoría:** Jack Aguilar (Neuracode) · Aporte ciudadano sin afiliación · 2026-04-17.

---

## Separación de Capas del Proceso Electoral

Toda hipótesis se ancla a una de las 5 capas donde puede introducirse sesgo:

| Capa | Qué ocurre | Actor responsable | Data disponible |
|------|------------|-------------------|-----------------|
| **L1 — Votación** | Elector marca papeleta | Mesa de sufragio | Acta de escrutinio |
| **L2 — Escrutinio en mesa** | Miembros de mesa cuentan votos | Presidente + 2 miembros | Acta firmada |
| **L3 — Transmisión** | Acta llega a ONPE (flash + física) | ODPE (personal ONPE) | Logs, hashes, timestamps |
| **L4 — Digitación** | Datos ingresan al sistema | Digitadores ONPE/proveedor | Logs de ingreso, operador ID |
| **L5 — Agregación/publicación** | Totales parciales y finales | ONPE central | Serie temporal, snapshots |
| **L6 — Calificación JEE** | JEE resuelve actas impugnadas/observadas | Jurados especiales | Resoluciones caso a caso |

Cada hipótesis abajo especifica **en qué capa aplicaría**.

---

## H1 — Sesgo operativo en distribución de material (Capa L0 pre-electoral)

### Enunciado

*"La distribución de material electoral 2026 presentó fallas concentradas
geográficamente en un patrón correlacionado con el perfil electoral esperado
de ciertos candidatos."*

### Motivación

**Hecho público documentado:** 55,000-63,000 electores en Lima no pudieron
votar el 12 de abril por fallas de Servicios Generales Galaga (proveedor
contratado vía mecanismo excepcional que eludió la Ley de Contrataciones).
211 mesas afectadas. Fuente: Gestión, Ojo Público.

### Variables observables

- `mesas_afectadas[distrito]`: número de mesas sin poder operar normalmente.
- `share_candidato[distrito, t-1]`: histórico distrital (2021 + encuestas).
- `electores_perdidos[distrito]`: estimado por el padrón de las mesas
  afectadas.

### Test estadístico

- **Prueba principal:** regresión lineal de `share_mesas_afectadas[distrito]`
  sobre `share_RLA_histórico[distrito]`, `share_Sánchez[distrito]`,
  `share_Fujimori[distrito]`, controles sociodemográficos (ingreso,
  urbanidad, densidad).
- **H0:** coeficientes de share candidato = 0 (las fallas fueron aleatorias).
- **H1:** algún coeficiente significativo ≠ 0 (fallas correlacionadas con
  perfil).
- **Robustez:** permutación de distritos (999 iteraciones), bootstrap CI95.

### Datos requeridos

- **ONPE:** lista oficial de las 211 mesas afectadas con distrito, padrón,
  causa registrada.
- **INEI:** capa sociodemográfica distrital.
- **Congreso:** minuta de Comisión de Fiscalización con Alarcón Gonzáles.

### Criterio de rechazo de H0

p-valor del test conjunto de coeficientes candidato < 0.01 con bootstrap
CI95 que excluya 0.

### Riesgo de falso positivo

**Alto si no se controlan confundidores.** Lima metropolitana tiene alta
densidad y alto share Fujimori/RLA histórico — una correlación sin controles
socioeconómicos puede ser espuria. **Por eso la regresión debe incluir al
menos 3 controles demográficos.**

### Severidad esperada

**Alta procesal, moderada estadística.** Incluso si H0 no se rechaza,
la elección del proveedor vía mecanismo excepcional es irregularidad
administrativa de competencia de Contraloría.

---

## H2 — Asimetría en tasa de actas fuera de conteo (Capa L6)

### Enunciado

*"La fracción de actas enviadas a JEE (impugnadas, observadas, pendientes)
no es homogénea entre regiones; su distribución se correlaciona con el
share esperado de algún candidato específico."*

### Motivación

Hallazgo A1 actual: Extranjero 24.11% impugnación (z=+3.66, p<1/2000).
Hallazgo G1: Pearson r=+0.477 entre tasa_impug y share_RLA regional, pero
Spearman no significativo (p=0.34) y bootstrap CI95 incluye 0 — hallazgo
MEDIA, no robusto a pequeños cambios.

### Variables observables

- `tasa_fuera[región] = actas_fuera / total_actas`.
- `share_candidato[región]`.
- Controles: `densidad_urbana`, `remoto_rural`, `tasa_ausentismo`.

### Test estadístico

- **Regresión con controles:** `tasa_fuera ~ share_RLA + share_Sánchez +
  share_Fujimori + densidad + ruralidad`.
- **Moran's I bivariado** (ya ejecutado en M2): **I=-0.023, p=0.837 → NO hay
  co-clustering.**
- **Replicar a nivel mesa** bajo M3 (pendiente por datos ONPE).

### Datos requeridos

- **ONPE:** dump mesa-a-mesa con estado actual de cada acta.
- **JEE:** base consolidada de actas impugnadas con motivo y estado de
  resolución.

### Criterio de rechazo

Coeficiente de share_RLA significativo (p<0.01) controlando confundidores,
y Moran's I bivariado a nivel mesa con p<0.01.

### Riesgo de falso positivo

**Moderado.** Los hallazgos actuales a nivel regional son borderline o no
significativos tras controles. El problema puede ser real pero invisible
a n=26.

### Estado

- Parcialmente refutada a nivel regional (ver hallazgos G1, M2 bivariado).
- Pendiente confirmación/refutación a nivel mesa (M3).

---

## H3 — Sesgo en digitación (Capa L4)

### Enunciado

*"Los errores de transcripción entre el acta física y el sistema ONPE
presentan asimetría por candidato: los errores que reducen votos a un
candidato específico no son balanceados por errores que los aumentan."*

### Motivación

En una digitación sin sesgo, los errores deben seguir distribución aleatoria:
tanto "de más" como "de menos" para cualquier candidato.

### Variables observables

- Por cada acta verificable (muestra aleatoria o 100%):
  `diferencia_votos[acta, candidato] = sistema - acta_fisica`.
- Distribución de diferencias por candidato.

### Test estadístico

- **Test de simetría de Wilcoxon** por candidato: H0 = distribución simétrica
  alrededor de 0.
- **Test de diferencia de medias** entre candidatos: ¿el error medio para
  RLA es distinto que para Sánchez/Fujimori?
- **Kolmogorov-Smirnov 2-sample** comparando distribuciones de error entre
  candidatos.
- **Último dígito de `diferencia_votos`** (Mebane 2006): manipulación manual
  tiende a dígitos redondos.

### Datos requeridos

- **JEE:** copia digital de actas físicas impugnadas para comparar con
  sistema ONPE.
- **Peritaje directo:** muestra aleatoria de 1,000 actas (validada
  estadísticamente con potencia 0.8, alpha 0.05, efecto mínimo 1 voto
  medio).

### Criterio de rechazo

Wilcoxon p<0.01 en alguna distribución, o diferencia de medias por candidato
con p<0.01 bajo bootstrap.

### Riesgo de falso positivo

Moderado. La digitación humana tiene errores naturales, pero deben ser
simétricos. Asimetría sistemática es el signo de interés.

### Estado

**Requiere peritaje documental.** Solo el Fiscal/JNE puede ordenar la
comparación acta-física vs sistema. Es la variable #7 del memorial
bajo apercibimiento.

---

## H4 — Anomalía en tiempos de digitación (Capa L4-L5)

### Enunciado

*"El tiempo de digitación por acta y su agrupamiento temporal reflejan
procesos operativos consistentes; desviaciones sostenidas de ese ritmo
coinciden temporalmente con eventos de interés político."*

### Motivación

Hallazgo H1 actual: velocidad de acumulación JEE cambió significativamente
±6h del cruce Sánchez>RLA (Mann-Whitney p=0.013).
Hallazgo H2 actual: **desaceleró 0.45× post-cruce** — contradice narrativa
viral de "aceleración post-cruce".

### Variables observables

- `timestamp[acta_digitada]` — registrable por el sistema ONPE.
- `operador_id[acta]` — qué digitador procesó qué acta.
- `duracion_digitacion[acta]` — tiempo entre `inicio` y `commit`.

### Test estadístico

- **Change-point detection** (PELT, Pruned Exact Linear Time) sobre serie
  temporal de velocidad.
- **Autocorrelación temporal** del flujo (ACF/PACF) — detecta ráfagas.
- **Distribución de duraciones por operador** — outliers extremos pueden
  indicar batch processing automatizado (script) vs digitación humana.

### Datos requeridos

- **ONPE:** log de timestamps + operador_id + acta_id completo.
- Actualmente solo tenemos snapshots agregados cada ~5 min via proxy.

### Criterio de rechazo

Change-point detectado con p<0.01 en ventana ±6h de evento político
relevante, Y ratio de velocidades >2× o <0.5×.

### Estado

**Parcialmente examinada** a nivel agregado (H1, H2 ya calculados).
**Requiere logs de digitación** para análisis por operador — variable #8
del memorial.

---

## H5 — Integridad de cadena proveedor-autoridad (Capa L0 y L3)

### Enunciado

*"Cuando un proveedor contratado por la autoridad electoral denuncia
públicamente a la autoridad, existe discrepancia documental que permite
contrastar dos fuentes independientes sobre los mismos hechos."*

### Motivación

**Hecho público documentado:** CALAG (Servicios Generales Galaga) desmintió
a ONPE y la denunció por atribución de negligencia. Es un conflicto entre
dos partes contractuales sobre los mismos hechos.

### Variables observables

- Declaraciones formales ONPE vs CALAG (públicas).
- Registros contractuales (obligación, cumplimiento, multas).
- Bitácoras internas de ambas partes.
- Trazabilidad de material electoral (entregas, firmas, fotos).

### Test estadístico

**Aquí el análisis NO es primariamente estadístico sino documental.**
Pero se puede cuantificar:
- **Consistencia temporal:** ¿los hitos declarados por ONPE coinciden con
  los declarados por CALAG en el tiempo? Desviación > 24h es alarma.
- **Consistencia cuantitativa:** ¿los números (mesas, material, costos)
  coinciden? Diferencia >5% en cifras reconciliables es alarma.

### Datos requeridos

- **Contraloría:** auditoría contractual ONPE-CALAG/Galaga.
- **Poder Judicial:** expediente de denuncia CALAG vs ONPE.
- **Fiscalía:** testimonios de ambas partes bajo juramento.

### Criterio de rechazo (de H0 = "hubo negligencia pura sin conflicto real")

Discrepancia documental > 5% en cifras cuantificables, y diferencia temporal
> 24h en al menos 3 hitos declarados.

### Severidad

**MÁXIMA procesal.** Esta es la evidencia **testimonial-documental** más
fuerte del caso. Supera en peso probatorio a cualquier estadística.

---

## Síntesis

| Hipótesis | Capa | Estado | Datos requeridos | Severidad potencial |
|-----------|------|--------|------------------|---------------------|
| **H1** Sesgo distribución material | L0 | Ejecutable ahora con data INEI | Lista 211 mesas + INEI | Alta procesal |
| **H2** Asimetría actas fuera | L6 | Parcial refutada regional; pdte mesa | Dump mesa-a-mesa ONPE | Moderada |
| **H3** Sesgo digitación | L4 | Pendiente peritaje | Muestra actas físicas vs sistema | Crítica |
| **H4** Anomalía tiempos | L4-L5 | Parcial (H1, H2 regionales listos) | Logs digitación ONPE | Alta |
| **H5** Cadena proveedor-autoridad | L0, L3 | Ejecutable ahora | Contratos, denuncia CALAG | **MÁXIMA** |

---

## Principio de honestidad

Este marco hipotético:
1. **NO presume fraude.** Cada H0 es "no hay anomalía"; el test solo puede
   rechazar con evidencia dura.
2. **Reporta resultados adversos.** Si H3 sale simétrica, se publica. Si H2
   sigue no significativa con mesa-a-mesa, se publica. Si H1 no muestra sesgo
   al controlar confundidores, se publica.
3. **Distingue capas.** Una anomalía en L1 (votación) implica cosas muy
   distintas que una en L4 (digitación). No se mezclan.
4. **Respeta la presunción de inocencia.** El único que puede determinar
   intención (dolo) es el juez. Nosotros entregamos evidencia y dejamos
   que el sistema decida.

## Lo que NO va en el memorial (sin fuente documental)

- Afirmar que Corvetto trabajó en Venezuela. **Falso, ya desmentido por
  Ojo Público** (fact-check público).
- Afirmar que ONPE contrató "digitadores venezolanos" sin nombres, contratos
  ni fuente pública verificable.
- Referencias a "Operación Morrocoy" como modus operandi atribuido a
  inteligencia cubana — el término existe (Venezuela 2012) pero no tiene
  peer-review que lo tipifique como operación de inteligencia.
- "Robo a Keiko 2021" — OEA y UE descartaron fraude. Incluirlo debilita
  todo el memorial.

---

**Documento reproducible.** Cuando se obtengan los datos bajo apercibimiento,
cada hipótesis será contrastable con el código open-source del repositorio.

**Repositorio:** `github.com/jackthony/auditoria-eg2026`
**Licencia:** CC-BY-4.0
**Autoría:** Neuracode · Jack Aguilar (aporte ciudadano, sin retribución,
sin afiliación política)
