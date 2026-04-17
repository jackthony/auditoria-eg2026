# Comunicados Públicos — Vía B

Textos listos para publicar. Neutros, técnicos, sin calificativos.
Cada bloque está optimizado para su canal.

---

## Twitter/X — Hilo principal (8 tuits)

**1/8**
Publico análisis técnico-estadístico del escrutinio EG2026 al corte 93.12% ONPE.
Metodología reproducible. Data pública. Hashes SHA-256. Sin afiliación política.
Repo: [URL]
PDF: [URL]

**2/8**
Hallazgo central: el margen Sánchez−López Aliaga (+5,392 votos) es ~195× menor que los votos contenidos en actas impugnadas + pendientes (~1,152,069).
La definición del 2° lugar depende del proceso de resolución del JEE.

**3/8**
Bajo distribución proporcional regional, la proyección del margen final es +188 votos a favor de Sánchez.
Virtualmente un empate técnico que se resolverá acta por acta en las audiencias JEE de los próximos días.

**4/8**
Anomalía estadística: la circunscripción Extranjero presenta tasa de impugnación de 24.11% (z=+3.66), aprox. 4× el promedio nacional.
Merece respuesta formal de ONPE/JNE: ¿a qué se atribuye? ¿Existe desagregado por oficina consular?

**5/8**
Verificaciones negativas (igual de importantes):
• Reconciliación Σ regional vs nacional: OK (diferencias <0.01%)
• Ley de Benford primer dígito: conforme (p=0.168)
• Serie temporal 116 cortes: sin saltos >0.5pp
No hay evidencia estadística de manipulación agregada.

**6/8**
Sobre la tesis viral del "change-point" post-cruce Sánchez>RLA:
Testé los datos. Drop de velocidad real = −21% (no −62% como circula).
t-test: p=0.079 → NO significativo al 5%.
Explicación compatible más simple: agotamiento del stock de actas rurales.

**7/8**
Marco económico-procesal verificado:
• Tasa nulidad: S/1,375 por mesa (TUPA JNE 2026)
• Plazo audiencia JEE: 2 días hábiles (Res. 0180-2025-JNE)
• 2ª vuelta: 2026-06-07
• 98 solicitudes de nulidad al corte

**8/8**
La data es pública. El código es abierto. Cualquier perito puede reproducir el análisis en su propia máquina.
Si encuentran errores, por favor abran un issue en el repo.
El fin es contribuir a la transparencia del proceso, no a una posición política.

---

## LinkedIn — Post largo

**Título:** Auditoría técnico-estadística del escrutinio EG2026 — datos abiertos

Como ingeniero, he dedicado los últimos días al análisis de la data pública del escrutinio de las Elecciones Generales 2026 del Perú, con el objetivo de aportar rigor técnico a la discusión pública del proceso.

El informe completo (PDF) y el código reproducible están disponibles en:
- GitHub: [URL]
- Mirror IPFS: [URL]

**Hallazgo crítico:** el margen Sánchez−López Aliaga al corte 93.12% es de +5,392 votos, aproximadamente 195 veces menor que el universo de votos contenidos en actas impugnadas y pendientes (~1,152,069). Bajo distribución proporcional regional, la proyección del margen final es de apenas +188 votos a favor de Sánchez, un virtual empate técnico.

**Hallazgos medios:** la circunscripción Extranjero presenta una tasa de impugnación de 24.11% (z=+3.66), aproximadamente 4× el promedio nacional (5.99%). Lima+Callao registra una tasa de impugnación menor al resto del país (4.13% vs 6.94%, z=−17.17, p<0.01). Esta asimetría es estadísticamente significativa y merece explicación formal.

**Verificaciones exitosas:** reconciliación entre suma regional y total nacional (diferencias <0.01%), conformidad con la Ley de Benford (p=0.168), y ausencia de saltos anómalos en la serie temporal de 116 cortes.

**Lo que el análisis NO demuestra:** fraude electoral. El análisis estadístico de data agregada no puede probar intención ni coordinación. Lo que sí hace es identificar patrones anómalos que ameritan respuesta formal de las autoridades electorales.

Metodología, fuentes, hashes SHA-256 de cada archivo capturado, y pipeline completo de reproducibilidad están documentados en el repositorio.

Invito a peritos, estadísticos, periodistas y ciudadanía técnica a replicar, cuestionar, mejorar y reutilizar el trabajo.

#Elecciones2026 #Peru #DataAbierta #TransparenciaElectoral

---

## Comunicado de sitio web (800 palabras)

### Transparencia técnica del escrutinio EG2026 — un aporte ciudadano

**Fecha del corte:** 2026-04-17 06:27 UTC
**Escrutinio oficial ONPE:** 93.12%
**Documento técnico:** descargar PDF

#### Qué es este trabajo

Un análisis técnico-estadístico del escrutinio de las Elecciones Generales 2026 del Perú, elaborado a partir de data pública disponible en los endpoints oficiales de la ONPE. Es un insumo ciudadano para la fiscalización del proceso, no una posición política.

#### Qué NO es

No es una denuncia de fraude. El análisis estadístico sobre data agregada no puede probar intención ni coordinación. Lo que sí hace es identificar patrones anómalos que requieren respuesta formal de las autoridades.

#### Cómo se construyó

1. Captura atómica de los endpoints públicos de ONPE, con hash SHA-256 inmediato.
2. Procesamiento del dataset (116 cortes temporales, 26 regiones).
3. Batería de tests estadísticos: reconciliación agregada, outliers por z-score, Benford, serie temporal, z-test de proporciones, simulación contrafactual.
4. Publicación íntegra del código, la data y los hashes para reproducibilidad por terceros.

#### Resultados

**Críticos:**
- Margen del 2° lugar depende de resolución JEE (+5,392 vs 1.15M en disputa).

**Medios:**
- Tasa impugnación Extranjero: 24.11% (z=+3.66, outlier).
- Asimetría Lima+Callao vs resto: z=−17.17, p<0.01.

**Negativos (no se hallaron irregularidades):**
- Reconciliación regional-nacional: diferencias <0.01%.
- Benford primer dígito: conforme.
- Serie temporal 116 cortes: sin saltos >0.5pp.

#### Lo que está pendiente

Una auditoría completa requiere:
- Cotejo acta por acta mediante OCR de los PDF digitalizados (pendiente habilitación del módulo ONPE para organizaciones políticas).
- Acceso a logs del STAE/ODPE/centro de cómputo (no disponibles públicamente).
- Comparación con línea base histórica EG2021, EG2016, EG2011.

#### Cómo colaborar

- Clonar el repo: `git clone [URL]`
- Verificar los hashes: `py src/capture/verify_manifest.py captures/<timestamp>/`
- Correr el análisis: `py src/analysis/run_all.py`
- Reportar errores o propuestas de mejora como issues en el repositorio.

#### Licencia

Código: MIT. Documento: Creative Commons BY 4.0.
Uso libre con atribución y preservación del historial de modificaciones.

#### Contacto

Issues del repositorio. Este trabajo se entrega sin afiliación política ni institucional.

---

## Nota de prensa breve (400 palabras)

**Para redacciones — Disponible para entrevista técnica**

Un análisis técnico-estadístico independiente del escrutinio EG2026, elaborado a partir de la data pública de ONPE y con cadena de custodia verificable por SHA-256, está disponible en [URL].

El documento identifica como hallazgo crítico que el margen entre el 2° y 3° lugar (+5,392 votos a favor de Roberto Sánchez sobre Rafael López Aliaga al corte 93.12%) es aproximadamente 195 veces menor que el universo de votos contenidos en actas impugnadas y pendientes (~1,152,069). La definición del pase a 2ª vuelta depende del proceso de resolución del Jurado Electoral Especial.

Un segundo hallazgo de severidad media: la circunscripción Extranjero presenta una tasa de impugnación de 24.11%, aproximadamente cuatro veces el promedio nacional. El análisis no pretende explicar esta anomalía —requiere respuesta formal de ONPE/JNE—, pero la documenta con rigor estadístico (z=+3.66).

El análisis también descarta algunas hipótesis que han circulado en redes sociales. Por ejemplo, la tesis de un "change-point brusco" en la velocidad de Sánchez tras cruzar a López Aliaga no se sostiene con los datos: el drop real de velocidad es de 21%, no 62% como afirma una publicación viral, y el t-test arroja p=0.079, no significativo al 5%.

El informe incluye verificaciones negativas: la reconciliación entre la suma regional y el total nacional coincide dentro del margen de redondeo; la primera cifra del voto por candidato es conforme a la ley de Benford; y no hay saltos anómalos en la serie temporal de 116 cortes.

El trabajo se publica como aporte ciudadano, sin afiliación política. Código bajo licencia MIT, documento bajo Creative Commons BY 4.0. Disponible para réplica y validación por terceros.

Contacto: [issues del repositorio]
