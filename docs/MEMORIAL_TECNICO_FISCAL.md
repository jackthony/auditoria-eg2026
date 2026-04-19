# MEMORIAL TÉCNICO CIUDADANO

## Solicitud de peritaje forense y medidas cautelares técnicas sobre el escrutinio de las Elecciones Generales 2026 — Perú

**Aporte ciudadano técnico-estadístico. Documento público reproducible.**

---

**SUMILLA:** Solicita se disponga peritaje forense informático y medidas cautelares técnicas sobre el proceso de escrutinio de la ONPE, en mérito de patrones estadísticos anómalos documentados y reproducibles que ameritan verificación formal.

**Señor Fiscal de la Nación:**

Se presenta a Ud. este memorial técnico como aporte ciudadano, elaborado a partir de **data pública exclusivamente** disponible en los endpoints oficiales de la ONPE, con cadena de custodia por hashes SHA-256 y código fuente abierto, en los términos que siguen:

---

## I. IDENTIFICACIÓN DEL APORTANTE

- **Razón social:** Neuracode — Jack Aguilar (Ingeniero responsable).
- **Naturaleza:** Aporte ciudadano independiente. Sin afiliación política ni institucional. Sin retribución económica.
- **Canal público:** `https://github.com/jackthony/auditoria-eg2026` · Dashboard en vivo.
- **Licencia:** Código MIT · Documentos Creative Commons BY 4.0. Uso libre con atribución.

---

## II. OBJETO Y ALCANCE

Este documento **NO afirma la comisión de delito electoral ni imputa dolo** a funcionario alguno. Lo que expone son **hechos estadísticos reproducibles** que, en opinión técnica del aportante, ameritan:

1. Peritaje forense informático sobre el pipeline de escrutinio de la ONPE.
2. Oficio de entrega obligatoria (bajo apercibimiento) de las variables/data de trazabilidad que se detallan en la sección VI.
3. Medidas cautelares técnicas que preserven la integridad probatoria hasta el pronunciamiento del Jurado Electoral Especial (JEE) y, eventualmente, del Jurado Nacional de Elecciones (JNE).

El estándar probatorio aplicable es el de **indicios suficientes de relevancia investigativa**, no el de condena. La estadística por sí sola **no prueba** intención criminal. Prueba **asimetrías que requieren explicación formal**.

---

## III. FUNDAMENTOS DE HECHO

### Hecho 1 — Definición del 2° lugar depende de la resolución JEE

Al corte **92.91%** del escrutinio oficial (2026-04-16 09:58 UTC):

| Candidato | Votos contabilizados | % |
|-----------|----------------------|---|
| Keiko Fujimori | — | 17.06% |
| Roberto Sánchez | 1,881,625 | 11.99% |
| Rafael López Aliaga | 1,875,852 | 11.92% |
| Luis Nieto | — | 11.08% |
| Ricardo Belmont | — | 10.16% |

- **Margen Sánchez − López Aliaga: +5,773 votos (+0.037 pp).**
- **Actas fuera del conteo: 6,338** (4,959 en JEE + 1,379 pendientes regionales).
- **Universo de votos en disputa: ~1,073,620 votos** (≈186× el margen).

La proyección contrafactual muestra que si el total de actas fuera del conteo se resolviera al ratio de voto regional actual, el margen final proyectado sería de **+64 votos a favor de Sánchez** — empate estadístico absoluto.

### Hecho 2 — Anomalía en la circunscripción Extranjero

| Métrica | Extranjero | Promedio nacional |
|---------|------------|-------------------|
| Tasa de impugnación | **24.11%** | 5.99% |
| z-score | **+3.66** | 0 |
| Share RLA | 25.96% | 11.92% |

La probabilidad de observar una tasa de 24.11% bajo la hipótesis de distribución homogénea es inferior a **1 en 2,000** (prueba de dos colas, |z|>3.66). Requiere explicación formal por oficio consular.

### Hecho 3 — Asimetría Lima+Callao vs resto del país

Prueba z de dos proporciones (tasa de impugnación, Lima+Callao = 4.13% vs resto = 6.94%):
- **z = −17.17**, **p < 0.001**.

La tasa de impugnación en Lima+Callao es **significativamente menor** que en el resto del país, lo cual es contraintuitivo dado el volumen absoluto de actas y votantes en dichas circunscripciones.

### Hecho 4 — Concentración de actas fuera del conteo en zonas pro-RLA

Cruzando la tasa regional de impugnación con el share regional de López Aliaga:

- **Pearson r = +0.477, p = 0.014** (significativo al 5%).
- Spearman r = +0.20, p = 0.34 (NO significativo — la asociación está dominada por Lima y Extranjero).

Regiones donde predomina RLA (Lima, Callao, Extranjero): **2,387 actas fuera del conteo**, que representan el **37.7% del universo** siendo el **11.5% de las circunscripciones**. Tasa media de impugnación: **8.76%** vs **6.65%** en circunscripciones pro-Sánchez.

**Advertencia estadística honesta:** la correlación Pearson es significativa pero **no robusta** (bootstrap CI95 incluye 0, Spearman no significativo). La asociación es real en media pero sensible a 2-3 outliers. Se reporta como **hallazgo indiciario**, no concluyente.

### Hecho 5 — Cambio estructural en velocidad de impugnación alrededor del cruce Sánchez > López Aliaga

Cruce identificado: **2026-04-15 10:31 UTC** (escrutinio 89.51%).

Velocidad de acumulación de actas JEE (robust rate, Δjee_total / Δhoras_span):

| Ventana | Antes del cruce | Después del cruce | Ratio | Mann-Whitney p |
|---------|------------------|---------------------|-------|----------------|
| ±6h | +182.6/h | +92.4/h | 0.51× | 0.013 |
| ±12h | +169.0/h | +76.4/h | 0.45× | 0.0015 |
| ±24h | +147.6/h | +38.4/h | 0.26× | 0.0002 |

La velocidad de acumulación **DISMINUYÓ significativamente** tras el cruce, **NO aumentó**. Este hallazgo contradice narrativas virales de "aceleración estratégica post-cruce". El patrón observado es compatible con explicación no dolosa (agotamiento progresivo de actas de rápida resolución), pero la magnitud del cambio estructural amerita verificación con logs internos.

### Hecho 6 — Modelo bayesiano jerárquico (Linzer 2013 JASA / NYT Election Needle)

Aplicación del modelo estándar de election-night forecasting (Dirichlet-Multinomial por región + prior Beta sobre tasa de integración JEE, n = 10,000 simulaciones Monte Carlo, seed reproducible):

| Escenario | Tasa integración JEE | P(RLA supera Sánchez) | Margen p50 |
|-----------|----------------------|-------------------------|------------|
| Pesimista (anti-Sánchez) | 29% | **37.0%** | +5,338 |
| Central | 50% | **42.6%** | +2,737 |
| Optimista (pro-Sánchez) | 71% | **49.2%** | +300 |
| Mixto (máx. incertidumbre) | — | **42.2%** | — |

Conclusión técnica: **empate estadístico**. La resolución del JEE no es un detalle administrativo — **es la variable que define el resultado**.

### Hecho 7 — Discrepancia institucional ONPE ↔ CALAG

A la fecha de este memorial, se reporta públicamente que la empresa **CALAG — Servicios Generales Galaga S.A.C.** (proveedor tecnológico) ha desmentido a la ONPE y la ha denunciado por atribución indebida de negligencia. Esta discrepancia entre dos actores institucionales del proceso constituye **evidencia directa** (declaración testimonial con interés) que supera por sí sola la fortaleza probatoria de cualquier análisis estadístico sobre data agregada.

El contenido específico de esta discrepancia no pertenece al alcance de este memorial técnico. Se solicita al Ministerio Público documentarla y contrastarla.

### Hecho 8 — Inconsistencia de agregación en el propio sitio público ONPE (finding A0)

Al snapshot **2026-04-17T08:41:14Z (corte 93.17%)**, el endpoint público de ONPE reporta cifras nacionales que **no reconcilian** con la suma de las 26 circunscripciones desagregadas:

| Métrica | Nacional publicado | Σ de las 26 regiones | Diferencia |
|---------|--------------------|-----------------------|------------|
| totalActas | 92,766 | 92,766 | 0 ✓ |
| contabilizadas | 86,438 | 86,434 | −4 |
| enviadasJee | 5,555 | 5,538 | −17 |
| pendientesJee | 773 | 794 | +21 |

**Métrica consolidada (post red-team metodológico):** `actas_movidas = max(|diff|) = 21`. Es el mínimo número de actas que deben reclasificarse entre categorías para que la vista nacional reconcilie con la vista regional. Con votos promedio por acta ≈ 218, el **universo de votos en zona gris ≈ 4,582 (ratio 0.78× el margen Sánchez−RLA de 5,875)**.

**Interpretación honesta:** este hecho **NO prueba error en el conteo de votos**. Prueba que la **agregación del agregador público de ONPE** (UI/API) no es internamente consistente al mismo timestamp. El autor ciudadano que reportó originalmente el hecho hizo el salto lógico "vista incoherente = conteo incorrecto"; ese salto no se sostiene técnicamente. Pero la inconsistencia del agregador oficial sí requiere **explicación formal** (timestamp desalineado entre endpoints, categoría no reflejada en desagregado, o actas migrando de estado durante el cálculo del snapshot). El **test es reproducible** por cualquier tercero contra cualquier snapshot horario en `captures/`.

### Hecho 9 — Ratio electores afectados (CALAG) / margen final

Datos **oficiales de ONPE** sobre las fallas del proveedor CALAG / Servicios Generales Galaga S.A.C. en Lima el día de la jornada electoral (12-abril-2026):

- **Locales de votación afectados:** 15.
- **Mesas no instaladas o instaladas tardíamente:** 211.
- **Electores oficialmente impedidos de votar:** **63,300**.
- **Margen final Sánchez − López Aliaga (corte 93.474% al 2026-04-18):** 13,624. *(Valor vivo: `data/processed/meta.json` → `margen_sanch_rla_votos`.)*

**Ratio: 63,300 / 13,624 ≈ 4.64×** al corte vigente. El universo de electores afectados por una falla operativa contratada bajo mecanismo excepcional (fuera del régimen ordinario de la Ley de Contrataciones) supera en **4.64 veces** el margen que define el pase a segunda vuelta.

**Marco jurídico directamente aplicable:** **Artículo 363° de la Ley 26859** (Ley Orgánica de Elecciones) — nulidad parcial cuando concurra un evento que *podría* haber alterado el resultado. El estándar del Art. 363 **no exige probar alteración**, sino acreditar que el evento **tuvo magnitud suficiente** para haberla causado. Un ratio ≥ 1× ya satisface ese umbral; 4.64× lo supera por varios múltiplos.

Este hecho, combinado con la discrepancia institucional del Hecho 7 (CALAG ↔ ONPE), configura el núcleo de materia que debe conocer el JEE / JNE para resolver la validez del resultado en Lima.

### Hecho 10 — Brecha de ausentismo post-pandemia vs pre-pandemia

Serie histórica de ausentismo nacional ONPE en elecciones generales peruanas:

| Elección | Contexto | Ausentismo nacional |
|----------|----------|---------------------|
| 2016 | Pre-pandemia | 18.21% |
| 2021 | Durante pandemia | 29.15% |
| **2026** | Post-pandemia (proyección a 100% escrutinio) | **26.16%** |

**Comparación válida (pre/post-pandemia):** 2026 vs 2016 → **+7.95 puntos porcentuales** = **≈ 3,000,000 electores adicionales que no acudieron a votar** respecto al baseline pre-pandemia.

**Honestidad estadística obligatoria:** la narrativa viral "el ausentismo subió post-pandemia vs pandemia" **NO se sostiene**. El ausentismo 2026 está *por debajo* de 2021 (efecto reversión pandémica). La comparación honesta es 2026 vs 2016, y ahí sí hay una brecha material.

**Relevancia para la investigación:** la brecha de 3M electores es multifactorial (desconfianza institucional, fallas logísticas, clima, movilidad). Ninguna causa única la explica. Pero **la fracción atribuible a las fallas operativas documentadas (CALAG, STAE, cédulas Callao, personeros ausentes, locales con cierre prematuro en 13% de Lima)** es materia propia de peritaje. Se solicita que ese peritaje determine el **componente del ausentismo atribuible a fallas del proceso**, separable del componente atribuible a decisión libre del elector.

### Hecho 11 — Cuatro cajas selladas con material electoral en basurero de Surquillo + denuncia penal JNE → ONPE (2026-04-17)

**Hechos verificables (fuente: comunicado oficial JNE, declaraciones del Presidente Roberto Burneo ante la Comisión de Fiscalización del Congreso, 2026-04-17; cobertura concurrente Infobae · El Comercio · Radio Nacional · Canal N):**

1. **Hallazgo material:** cuatro cajas selladas conteniendo aproximadamente **1,200 sobres con cédulas de votación** de la jornada del 12-abril-2026 fueron encontradas en un basurero del distrito de **Surquillo (Lima)** el 17-abril-2026.
2. **Denuncia penal formalizada:** el Procurador Público del JNE, Ronald Johanne Angulo Zavaleta, presentó denuncia penal ante el Ministerio Público contra **Piero Corvetto Salinas** (Jefe de la ONPE) y demás funcionarios responsables, por los presuntos delitos de **Atentado contra el Derecho de Sufragio (Art. 354 CP)**, **Omisión de Actos Funcionales (Art. 377 CP)** y **Estorbo del Acto Electoral**.
3. **Discrepancia institucional documentada (Hecho 7 ratificado):** el Presidente del JNE Roberto Burneo declaró ante el Congreso que, contrario a la versión pública de ONPE, **no había inspector ni efectivo policial acompañando el traslado** del material; las cajas fueron transportadas en **vehículos privados sin registro y sin presencia de fedatario JNE**. Esto contradice frontalmente el protocolo de cadena de custodia electoral.
4. **Allanamiento fiscal:** el Ministerio Público (Fiscalía de Prevención del Delito de Lima Sur), con participación de funcionarios JNE, allanó el **almacén principal de la ONPE en Lurín** para verificar existencia y condición del material electoral del 12-abril.
5. **Audiencia en Congreso:** el Presidente del JNE expuso ante la Comisión de Fiscalización del Congreso el 17-abril-2026 el detalle de las irregularidades detectadas que **impidieron la instalación de 211 mesas de sufragio** (consistente con el universo de 63,300 electores afectados del Hecho 9).

**Relevancia técnico-procesal:**

- Este hecho constituye **evidencia material directa** de ruptura de cadena de custodia, no inferencia estadística.
- Refuerza el Hecho 7 (discrepancia ONPE↔CALAG) y el Hecho 9 (63,300 electores afectados) con un eslabón documentado que ya está bajo investigación fiscal autónoma.
- La denuncia del JNE es **acción institucional de un órgano electoral autónomo contra otro**, no de un actor político, y por ello **goza de presunción de seriedad procesal**.
- El presente memorial **no duplica** la denuncia del JNE: la complementa aportando el marco estadístico-forense (Hechos 1-10) que permite dimensionar el impacto de las fallas operativas sobre el resultado.

**Honestidad técnica:** se desconoce, al cierre de este memorial, el **destino electoral concreto** de las 1,200 cédulas (mesa de origen, candidato afectado, si fueron contabilizadas o no en el escrutinio). Esa determinación requiere peritaje sobre el material físico recuperado (números de serie de sobres, mesas correlacionadas en SIRE-DMS), lo cual es atribución exclusiva del Ministerio Público y se solicita formalmente como variable adicional (ver §V, ítem 16).

---

## IV. FUNDAMENTOS DE DERECHO

La investigación solicitada se subsume potencialmente en los siguientes tipos penales del Código Penal peruano:

| Artículo | Delito | Relevancia |
|----------|--------|------------|
| Art. 354 CP | Atentados contra el derecho de sufragio | Si se acredita impedimento doloso |
| Art. 355 CP | Fraude electoral | Si hay alteración de resultados |
| Art. 361 CP | Abuso de autoridad | Funcionario omite o actúa fuera de atribuciones |
| Art. 377 CP | Omisión, rechazo o demora de acto funcional | Si no se entregan actas/logs en plazo |

Normativa electoral aplicable:
- **Ley 26859** — Ley Orgánica de Elecciones (Art. 285 y ss. — escrutinio).
- **Ley 26486** — Ley Orgánica del Jurado Nacional de Elecciones.
- **Resolución 0180-2025-JNE** — procedimiento de actas impugnadas, plazo audiencia 2 días hábiles.
- **Resolución 0182-2025-JNE** — recuento.
- **TUPA JNE 2026** — tasa nulidad S/1,375 por mesa.

La Constitución Política del Perú (Art. 176°) otorga autonomía a ONPE y JNE pero **no inmunidad penal** a sus funcionarios frente a conductas tipificadas.

---

## V. VARIABLES Y DATA QUE SE SOLICITA OFICIAR A LA ONPE BAJO APERCIBIMIENTO

Para permitir verificación forense independiente, se solicita se requiera formalmente a la ONPE la entrega, con cadena de custodia y firma digital, de:

| # | Variable / documento | Finalidad técnica |
|---|------------------------|---------------------|
| 1 | Logs SIRE-DMS acto-por-acto (timestamps con precisión de milisegundo, usuario, IP, operación) desde 2026-04-13T00:00 hasta la fecha | Trazabilidad de cambios de status de cada acta (ingresada → observada → impugnada → resuelta → contabilizada/anulada) |
| 2 | Código fuente completo del pipeline de escrutinio, con hashes firmados por repositorio oficial | Reproducibilidad de algoritmos de agregación, detección de código no documentado |
| 3 | Contrato ONPE ↔ CALAG (y cualquier otro proveedor técnico) con todas sus adendas, anexos técnicos y clausulas de SLA | Delimitación de responsabilidades ante la discrepancia pública |
| 4 | Detalle estructurado por acta (JSON/CSV) de las 4,959 actas en JEE: causal codificada, ODPE, mesa, número de electores, candidato afectado (si aplica), fecha de impugnación, funcionario responsable | Verificar validez de causales, detectar patrones por causal |
| 5 | Comunicaciones internas ONPE ↔ CALAG (correo, Slack, tickets de incidentes) sobre errores reportados en ingreso de actas en los últimos 15 días | Los reportes de 3-5 intentos por acta en Cuzco deben generar ticket formal |
| 6 | Logs del proxy CORS / CDN que sirve los endpoints públicos `resultados.eleccionesgenerales2026.pe` | Validar si el caché observado es configuración por defecto o intencional |
| 7 | Bitácora de accesos al centro de cómputo, con usuarios autenticados y horarios, entre 2026-04-14 y la fecha | Control dual y segregación de funciones |
| 8 | Manual técnico del módulo de descarga masiva para organizaciones políticas y razón de su no habilitación al corte actual | El no-acceso al detalle mesa-por-mesa imposibilita auditoría partidaria |
| 9 | Base de datos de resolución de impugnaciones JEE histórica (EG2021, EG2016, EG2011) | Línea base para calibrar qué tasa de integración es "normal" |
| 10 | Especificación técnica del algoritmo de asignación aleatoria de miembros de mesa y coordinadores de local | Detectar sesgos en la cadena operativa |
| 11 | **Dump estructurado mesa-a-mesa** (≈90,000 registros) en formato CSV/JSON: mesa_id, ODPE, distrito, candidato, votos, estado, timestamp digitación, operador | Habilitar auditoría granular independiente por cualquier organización política o ciudadano (tests M3 a escala mesa) |
| 12 | **Desagregado oficial de electores emitidos por región** al cierre del escrutinio (no solo proyección nacional) | Permitir cálculo honesto de ausentismo por circunscripción, que actualmente se reporta solo a nivel nacional |
| 13 | **Expediente íntegro CALAG / Servicios Generales Galaga S.A.C.**: acto administrativo de contratación excepcional, términos de referencia, SLA, pólizas de fidelidad/incumplimiento, informes técnicos de conformidad y los 63,300 electores afectados con ODPE y mesa | Acreditar la magnitud oficial del evento del Hecho 9 y la cadena de responsabilidad administrativa |
| 14 | **Motivos codificados de rechazo/impugnación** de las 5,555 actas actualmente en JEE: causal, fecha, funcionario ONPE que derivó, partido afectado en la mesa | Verificar si la tasa 24.11% en Extranjero (Hecho 2) tiene patrón operativo o sesgo |
| 15 | **Actas físicas digitalizadas** (muestra aleatoria ≥1% del universo) para contraste contra el sistema SIRE-DMS | Contrastar el dato físico con el dato digital, principio de doble-fuente |
| 16 | **Trazabilidad completa del material electoral hallado en basurero de Surquillo (2026-04-17):** números de serie de las 4 cajas y de los ~1,200 sobres; mesa(s) de origen; cadena de custodia documental desde la mesa hasta el punto de hallazgo; identificación de vehículos, conductores, custodios y fedatarios designados vs efectivos; correlación con registros SIRE-DMS de las mesas afectadas | Determinar el impacto electoral concreto del material extraviado y reconstruir la ruptura de cadena de custodia (Hecho 11) |
| 17 | **Acta(s) y video del allanamiento fiscal al almacén ONPE en Lurín (2026-04-17)** + inventario certificado del material remanente vs el material que debió retornar tras la jornada | Verificar discrepancia entre material despachado y material retornado a almacén |
| 18 | **Bitácora oficial JNE de fedatarios designados** para acompañar el traslado de material el 12-abril-2026, vs los efectivamente presentes (firma + huella) | Acreditar el hecho central de la denuncia penal JNE→ONPE: ausencia de fedatario en el traslado |

---

## VI. MEDIDAS CAUTELARES TÉCNICAS SOLICITADAS

1. **Preservación probatoria de logs y base de datos del escrutinio** — prohibición de depuración, backup en custodia notarial/fiscal con hash SHA-256, hasta el pronunciamiento firme del JNE sobre actas impugnadas.
2. **Prohibición de modificación del código fuente del pipeline de escrutinio** hasta peritaje independiente concluido.
3. **Designación de perito forense informático** con acceso total a la infraestructura, bajo convenio de confidencialidad pero con entrega de informe público (resumen no-sensible).
4. **Observación presencial permanente** de un fiscal en el centro de cómputo hasta el cierre del escrutinio.
5. **Custodia notarial** de los snapshots horarios del sitio público (www2.ONPE.gob.pe/resultados), independientemente de los logs internos.

---

## VII. PRUEBA OFRECIDA

Toda la evidencia estadística descrita es **replicable por cualquier tercero** siguiendo estos pasos:

```bash
git clone https://github.com/jackthony/auditoria-eg2026
cd auditoria-eg2026
pip install -r requirements.txt
py src/capture/verify_manifest.py captures/<timestamp>/
py src/analysis/run_all.py
py scripts/build_dashboard_json.py
```

Los archivos ofrecidos como anexos técnicos:

| Anexo | Ruta en repositorio | Hash SHA-256 |
|-------|---------------------|---------------|
| A. Capturas atómicas ONPE con manifiesto | `captures/*/MANIFEST.jsonl` | Individual por archivo |
| B. Dataset procesado | `data/processed/regiones.csv` · `tracking.csv` | (ver manifest) |
| C. Reports técnicos estructurados | `reports/findings.json` · `forecast.json` · `impugnation_bias.json` · `impugnation_velocity.json` · `ausentismo_comparacion.json` · `reconcile_internal` (incluido en findings.json) | — |
| D. Código fuente del pipeline | `src/` · `scripts/` | — |
| E. Metodología completa | `METHODOLOGY.md` | — |
| F. Dossier para perito acreditado | `dossier-perito/00_RESUMEN_EJECUTIVO.md` a `05_LIMITACIONES.md` | — |
| G. Pre-registro de hipótesis (commit frozen) | `docs/PRE_REGISTRO_H1_H5.md` + hashes | Commit `413d6a1` |
| H. Fallas técnicas verificadas con fuente pública | `docs/FALLAS_TECNICAS_VERIFICADAS.md` | — |
| I. Evidencia ciudadana (versión pública) | `docs/EVIDENCIA_CIUDADANA.md` | — |

**Cadena de custodia:** cada snapshot incluye timestamp ISO-8601 UTC, IP pública del capturador, hostname, commit git vigente, y hash SHA-256 de cada archivo. Cualquier modificación posterior es detectable por `py src/capture/verify_manifest.py`.

---

## VIII. OTROSÍ DIGO

1. **Sobre la ausencia de imputación:** este memorial NO imputa delito a persona natural ni jurídica. Solicita investigación formal en mérito de evidencia indiciaria. Su finalidad es **preservar la integridad del proceso electoral**, no favorecer a candidato alguno.

2. **Sobre la publicidad del documento:** el presente memorial es público por decisión del aportante. Se difunde en el repositorio mencionado y en medios digitales. El Ministerio Público puede conservarlo como reservado a efectos de la investigación si así lo dispone.

3. **Sobre la contradicción con narrativas virales:** el aportante hace constar expresamente que varios patrones virales atribuidos al proceso **no se sostienen con los datos disponibles**:
   - La tesis de "aceleración estratégica post-cruce" es contradicha por los propios datos — la velocidad DESACELERÓ 0.26× a 0.51× según ventana (Hecho 5).
   - La narrativa "ausentismo aumentó post-pandemia vs pandemia" tampoco se sostiene: 2026 (26.16%) está por debajo de 2021 (29.15%). La comparación honesta es 2026 vs 2016 (Hecho 10).
   - La lectura "agregador inconsistente = conteo incorrecto" (Hecho 8, finding A0) tampoco se sostiene lógicamente; lo que sí se sostiene es que la UI/API de ONPE no reconcilia consigo misma al mismo timestamp, y eso requiere explicación formal.
   
   El rigor técnico obliga a reportar tanto los indicios a favor como los contra de cualquier hipótesis. Este memorial lo hace.

4. **Sobre el peritaje contradictorio:** el aportante se ofrece a sostener técnicamente las conclusiones ante cualquier perito designado por la contraparte. El código es abierto; los datos son públicos; los hashes son verificables; el método es estándar (Linzer 2013, Gelman & Hill 2007, NYT Election Needle).

5. **Sobre la independencia:** Neuracode y el aportante no reciben retribución de ningún partido político, organización, ni institución pública o privada por el presente trabajo.

---

**POR TANTO:**

A Ud., Señor Fiscal de la Nación, pido se sirva admitir el presente memorial técnico, disponer lo pertinente para la entrega de los ítems de la sección V bajo apercibimiento, y dictar las medidas cautelares de la sección VI, en cautela de la integridad del proceso electoral y del derecho ciudadano a un escrutinio verificable.

**Lima, 2026-04-17.**

---

**Neuracode — Jack Aguilar**
Aporte ciudadano independiente

GitHub: `github.com/jackthony/auditoria-eg2026`
Canales: TikTok `@JackDeNeuracode` · FB/IG `@neuracode`

---

> Documento reproducible · Data pública · Hashes SHA-256 verificables · Sin afiliación política
> Licencia: Código MIT · Documento CC-BY-4.0
