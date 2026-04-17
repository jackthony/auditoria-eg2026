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
- **Canal público:** `https://github.com/neuracode/auditoria-eg2026` · Dashboard en vivo.
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

A la fecha de este memorial, se reporta públicamente que la empresa **CALAG** (tecnología proveedora) ha desmentido a la ONPE y la ha denunciado por atribución indebida de negligencia. Esta discrepancia entre dos actores institucionales del proceso constituye **evidencia directa** (declaración testimonial con interés) que supera por sí sola la fortaleza probatoria de cualquier análisis estadístico sobre data agregada.

El contenido específico de esta discrepancia no pertenece al alcance de este memorial técnico. Se solicita al Ministerio Público documentarla y contrastarla.

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
git clone https://github.com/neuracode/auditoria-eg2026
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
| C. Reports técnicos estructurados | `reports/findings.json` · `forecast.json` · `impugnation_bias.json` · `impugnation_velocity.json` | — |
| D. Código fuente del pipeline | `src/` · `scripts/` | — |
| E. Metodología completa | `METHODOLOGY.md` | — |

**Cadena de custodia:** cada snapshot incluye timestamp ISO-8601 UTC, IP pública del capturador, hostname, commit git vigente, y hash SHA-256 de cada archivo. Cualquier modificación posterior es detectable por `py src/capture/verify_manifest.py`.

---

## VIII. OTROSÍ DIGO

1. **Sobre la ausencia de imputación:** este memorial NO imputa delito a persona natural ni jurídica. Solicita investigación formal en mérito de evidencia indiciaria. Su finalidad es **preservar la integridad del proceso electoral**, no favorecer a candidato alguno.

2. **Sobre la publicidad del documento:** el presente memorial es público por decisión del aportante. Se difunde en el repositorio mencionado y en medios digitales. El Ministerio Público puede conservarlo como reservado a efectos de la investigación si así lo dispone.

3. **Sobre la contradicción con narrativas virales:** el aportante hace constar expresamente que varios patrones virales atribuidos al proceso **no se sostienen con los datos disponibles** (ejemplo: la tesis de "aceleración estratégica post-cruce" es contradicha por los propios datos — la velocidad DESACELERÓ 0.26× a 0.51× según ventana). El rigor técnico obliga a reportar tanto los indicios a favor como los contra de cualquier hipótesis.

4. **Sobre el peritaje contradictorio:** el aportante se ofrece a sostener técnicamente las conclusiones ante cualquier perito designado por la contraparte. El código es abierto; los datos son públicos; los hashes son verificables; el método es estándar (Linzer 2013, Gelman & Hill 2007, NYT Election Needle).

5. **Sobre la independencia:** Neuracode y el aportante no reciben retribución de ningún partido político, organización, ni institución pública o privada por el presente trabajo.

---

**POR TANTO:**

A Ud., Señor Fiscal de la Nación, pido se sirva admitir el presente memorial técnico, disponer lo pertinente para la entrega de los ítems de la sección V bajo apercibimiento, y dictar las medidas cautelares de la sección VI, en cautela de la integridad del proceso electoral y del derecho ciudadano a un escrutinio verificable.

**Lima, 2026-04-17.**

---

**Neuracode — Jack Aguilar**
Aporte ciudadano independiente

GitHub: `github.com/neuracode/auditoria-eg2026`
Canales: TikTok `@JackDeNeuracode` · FB/IG `@neuracode`

---

> Documento reproducible · Data pública · Hashes SHA-256 verificables · Sin afiliación política
> Licencia: Código MIT · Documento CC-BY-4.0
