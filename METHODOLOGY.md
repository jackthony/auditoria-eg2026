# METHODOLOGY.md — Metodología y referencias

Este documento justifica las pruebas estadísticas aplicadas y sus
limitaciones conocidas. Todo análisis forense electoral debe ser explícito
sobre qué test responde qué pregunta, y qué NO puede concluir.

> **Nota de independencia.** La metodología mesa-a-mesa (reconstruir la suma
> desde la API pública ONPE y contrastarla con los totales oficiales) se
> inspira en análisis públicos previos sobre el mismo dataset. Este proyecto
> aporta una **verificación independiente y reproducible**: captura propia con
> SHA-256, código abierto, y pipeline replicable por cualquier tercero.

## 1. Marco general

Se sigue el enfoque de **election forensics** propuesto por Walter Mebane y
popularizado por la literatura de ciencias políticas computacionales, adaptado
al contexto de transparencia activa: el objetivo NO es "probar fraude", sino
identificar desviaciones estadísticas respecto a las distribuciones esperadas
bajo procesos electorales limpios, y reportarlas con su nivel de confianza.

La estructura metodológica es:

1. **Definir hipótesis nula (H0):** el proceso se ejecutó dentro de parámetros
   normales. H1: existen desviaciones incompatibles con un proceso limpio.
2. **Seleccionar tests:** cada test responde una pregunta específica y tiene
   limitaciones conocidas que se documentan.
3. **Controlar el error tipo I:** se reporta p-valor, no se concluye "fraude"
   por p < 0.05 aislado.
4. **Contextualizar:** una desviación estadística sin explicación narrativa ni
   evidencia material corroborante es una bandera, no una conclusión.

## 2. Tests aplicados

### 2.1 Reconciliación agregada

**Pregunta:** ¿los totales regionales suman el total nacional publicado?

**Método:** suma de `votos_candidato_i` por región vs. `votos_candidato_i`
nacional, para los 5 candidatos con más votación. Se acepta diferencia de
redondeo < 0.1%.

**Interpretación:** una divergencia sistemática > 1% indicaría manipulación
entre niveles de publicación. El resultado esperado en cualquier proceso
limpio es coincidencia casi exacta.

### 2.2 Tasa de impugnación por región

**Pregunta:** ¿hay regiones con tasas de observación de actas anómalamente
altas respecto a la media nacional?

**Método:** z-score de la tasa regional de actas enviadas al JEE contra la
media y desviación estándar de las 26 regiones.

**Criterio de alerta:** |z| > 2 se reporta como outlier.

**Limitación:** las diferencias pueden explicarse por factores logísticos
(experiencia de personeros, condiciones de transporte, dispersión geográfica).
Un outlier es un trigger de investigación, no una prueba de irregularidad.

### 2.3 Estratificación geográfica (z-test de dos proporciones)

**Pregunta:** ¿existe diferencia estadísticamente significativa en la tasa de
impugnación entre Lima+Callao (zona fuerte de algunos candidatos) y el resto
del país?

**Método:** test z de dos proporciones sobre `enviadasJee / totalActas`.

**Referencia:** Agresti, A. (2002). *Categorical Data Analysis*, 2nd ed., Wiley.

### 2.4 Ley de Benford (primer dígito)

**Pregunta:** ¿los votos por candidato × región siguen la distribución de
primer dígito esperada (log₁₀(1 + 1/d))?

**Método:** test χ² con 8 grados de libertad, α = 0.05.

**Distribución esperada:**

| d | P(primer dígito = d) |
|---|---|
| 1 | 30.10% |
| 2 | 17.61% |
| 3 | 12.49% |
| 4 | 9.69% |
| 5 | 7.92% |
| 6 | 6.69% |
| 7 | 5.80% |
| 8 | 5.12% |
| 9 | 4.58% |

**Limitaciones críticas** (citar estas si alguien objeta el test):

> **Deckert, Myagkov & Ordeshook (2011),** "Benford's Law and the Detection
> of Election Fraud", *Political Analysis* 19(3): 245–268.
>
> Los autores demuestran que la Ley de Benford-1 produce *falsos positivos y
> falsos negativos* en datos electorales legítimos, especialmente cuando:
> (a) el número de actas por jurisdicción es pequeño y de magnitud similar;
> (b) existen candidatos con ventajas regionales muy marcadas; (c) la media
> del número de votos por mesa/acta está lejos de una potencia de 10.

Por esta razón, **un test Benford conforme NO prueba limpieza, y un test
Benford con desviación NO prueba fraude**. Se reporta como señal
complementaria, nunca como evidencia única.

### 2.5 Último dígito uniforme (recomendado, pendiente)

**Referencia:** Beber & Scacco (2012), "What the Numbers Say: A Digit-Based
Test for Election Fraud", *Political Analysis* 20(2): 211–234.

Bajo la hipótesis de digitación natural por miembros de mesa, el último
dígito de los conteos por acta debe ser uniforme sobre {0,...,9}. Un exceso
de dígitos "limpios" (0 y 5) es señal asociada con digitación humana
ajustada a una suma objetivo.

*Este test requiere datos acta-por-acta, no disponibles al corte actual.
Se implementará cuando se obtenga acceso al módulo de descarga masiva.*

### 2.6 Análisis de serie temporal

**Pregunta:** ¿hay saltos anómalos en el porcentaje de cada candidato entre
cortes consecutivos del conteo?

**Método:** deltas consecutivos sobre la serie temporal de snapshots. Se
reporta cualquier delta > 0.5 puntos porcentuales.

**Importante:** saltos súbitos se esperan normalmente cuando entran lotes
grandes de una región geográficamente homogénea (e.g., voto del extranjero
procesado de una sola vez). El análisis debe contextualizar cada salto
contra la composición regional de ese lote.

### 2.7 Simulación de impacto de actas en JEE

**Pregunta:** dado el margen actual entre los 2º y 3º lugares, ¿puede la
resolución de las actas impugnadas cambiar el orden?

**Método:** estimación por distribución proporcional al promedio nacional,
con cálculo del *break-even* (qué porcentaje de votos en disputa debería
ir a un candidato para empatar).

## 3. Referencias bibliográficas

- Agresti, A. (2002). *Categorical Data Analysis* (2nd ed.). Wiley.
- Beber, B. & Scacco, A. (2012). "What the Numbers Say: A Digit-Based Test
  for Election Fraud". *Political Analysis* 20(2): 211–234.
- Deckert, J., Myagkov, M. & Ordeshook, P. C. (2011). "Benford's Law and the
  Detection of Election Fraud". *Political Analysis* 19(3): 245–268.
- Levin, I., Cohn, G. A., Ordeshook, P. C. & Alvarez, R. M. (2009). "Detecting
  Voter Fraud in an Electronic Voting Context: An Analysis of the Unlimited
  Reelection Referendum in Venezuela". *EVT/WOTE Proceedings.*
- Mebane, W. R. (2006). "Election Forensics: Vote Counts and Benford's Law".
  *Society for Political Methodology working paper.*
- Nigrini, M. J. (2012). *Benford's Law: Applications for Forensic Accounting,
  Auditing, and Fraud Detection*. Wiley.
- OAS Electoral Observation Mission (2019). *Manual para las Misiones de
  Observación Electoral de la OEA*. Organización de Estados Americanos.
- The Carter Center (2020). *Election Observation Handbook*. The Carter Center.

## 4. Limitaciones globales del presente análisis

1. **Nivel de agregación:** sólo data pública a nivel regional. No se analiza
   acta-por-acta ni mesa-por-mesa. Muchas anomalías solo se manifiestan en
   niveles más granulares.
2. **Ausencia de logs de infraestructura:** no se tiene acceso a logs del
   STAE, ODPE ni centro de cómputo. No puede evaluarse la integridad del
   pipeline desde mesa hasta publicación.
3. **No-adversarial:** los tests asumen que el eventual manipulador no
   conoce los tests aplicados. Un adversario sofisticado puede fabricar
   datos que pasen todos los tests estadísticos.
4. **No hay línea base histórica:** idealmente se compararía cada indicador
   contra elecciones peruanas previas (2021, 2016, 2011) para contextualizar
   lo "normal". Eso requiere reconstruir datasets comparables y no se ha
   hecho en esta iteración.

## 5. Política de hallazgos

Cada hallazgo se etiqueta con:

| Severidad | Criterio |
|---|---|
| **CRÍTICO** | Requiere acción inmediata; p-valor muy significativo o impacto directo en resultado |
| **MEDIA** | Amerita seguimiento; desviación estadísticamente significativa con impacto potencial |
| **BAJA** | Bandera metodológica; desviación observable pero de impacto limitado |
| **INFO** | Información contextual; sin carácter de anomalía |

No se reportan hallazgos por debajo de "INFO". La ausencia de hallazgos en un
test no es noticia; la presencia, sí.
