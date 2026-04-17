# Limitaciones — Lo que esta auditoría NO puede afirmar

Documento de honestidad estadística obligatoria. El peritaje contraparte
detectará cualquier exageración. Mejor autodeclarar que ser desenmascarado.

---

## L1. No se prueba fraude ni dolo

Ninguno de los 15 findings constituye prueba jurídica de dolo. Los tests
estadísticos detectan **anomalías** (data que se comporta distinto a lo
esperable bajo modelo). La **intención detrás** de la anomalía solo puede
ser determinada por autoridad judicial con evidencia adicional (testimonial,
documental, peritaje específico).

---

## L2. No se descarta fraude

La ausencia de resultado significativo en un test no es prueba de
integridad. Específicamente:

- **M1 (último dígito) CONFORME** con n=26 por candidato: poder estadístico
  bajo. No descarta manipulación a escala mesa.
- **M2 (bivariado RLA×impug) ALEATORIO** a nivel regional: no descarta
  clustering a escala provincial/distrital.
- **C1 (Benford) CONFORME**: Benford es robusto contra manipulación
  grande, no pequeña.

**Los tests M3 (mesa-a-mesa) y M4 (motivos rechazo JEE) son los únicos
que pueden dar evidencia dura** — requieren data bajo apercibimiento.

---

## L3. Data ONPE incompleta al momento del análisis

- **Snapshots disponibles:** agregado nacional + desagregado regional (26 filas).
- **No disponibles:**
  - Mesa-a-mesa (≈90,000 registros).
  - Motivos de rechazo/impugnación clasificados.
  - Logs de digitación con operador ID y timestamp.
  - Acta física digitalizada para comparar con sistema.

El peritaje **profundo** (donde está la verdad si existe) requiere estos
datasets. Esta auditoría provee el marco para solicitarlos formalmente.

---

## L4. n pequeño en varios tests

- 26 regiones es pequeño para tests paramétricos.
- 5 candidatos limita tests de diferencia de medias entre candidatos.
- Correlaciones con n=26 son sensibles a outliers (caso G1).

Mitigación aplicada: bootstrap CI95 + permutación 999 donde corresponde.
Reportar resultados de Spearman junto con Pearson cuando difieren.

---

## L5. Capa temporal limitada

Captura ONPE comenzó 2026-04-13. No hay data del 12-abril durante el día.
Por tanto:

- No se pueden verificar velocidades durante el 12.
- No se pueden comparar curvas temporales con 2021 (snapshot inexistente).

---

## L6. Métodos aplicables a agregados, no a votos individuales

Tests Benford, último dígito, Moran's I operan sobre totales agregados.
**No detectan** manipulación individual voto-por-voto. Esa granularidad
requiere peritaje forense físico del acta.

---

## L7. Controles sociodemográficos no aplicados en todos los findings

Varios findings regionales (G1, A2) no tienen controles INEI aplicados.
Correlación **no es causalidad**. Específicamente:

- Lima metropolitana confunde urbanidad × densidad × share histórico.
- Sin controles, una correlación puede ser espuria.

Bajo H1-H5 pre-registrados, los controles se aplicarán formalmente.

---

## L8. Sesgo potencial del equipo

El autor (Jack Aguilar, Neuracode) es **ciudadano sin afiliación política
declarada**, pero:

- Inició el proyecto tras conocer las denuncias de RLA.
- Publica código abierto para verificación independiente.
- Reporta findings adversos al cliente (2026<2021, M2 bivariado NS,
  G1 no robusto).

Esta transparencia no elimina el sesgo; lo mitiga. **El perito acreditado
debe validar independientemente** antes de firmar.

---

## L9. No se incluyen (por falta de evidencia documental)

Excluido explícitamente por el principio de admisibilidad:

- **"Corvetto trabajó en Venezuela"** — falso, desmentido por Ojo Público
  (fact-check).
- **"Digitadores venezolanos contratados por ONPE"** — sin contratos
  públicos verificables.
- **"Operación Morrocoy como inteligencia cubana en Perú"** — el término
  existe (Venezuela 2012) pero no tiene peer-review que lo tipifique como
  operación de inteligencia.
- **"Robo a Keiko 2021 por 44 votos"** — OEA y UE descartaron fraude.
  Incluirlo debilita todo el dossier.
- **Rumores de redes sociales sin fuente periodística verificable.**

---

## L10. Modelo bayesiano F1: sensibilidad a priors

El 42.6% P(RLA>Sánchez) depende de:

- **Prior JEE:** ratio histórico de aprobación vs anulación. Asumido
  Beta(α=ratio_observado_hist).
- **Dirichlet regional:** concentración de incertidumbre por región
  pendiente.
- **Asunción clave:** comportamiento de actas pendientes ~ comportamiento
  de actas contabilizadas en la misma región.

Si esta asunción se viola (por ejemplo, actas pendientes son
sistemáticamente distintas), el 42.6% sesga. El escenario **mixto**
(42.2%) testa robustez parcial.

---

## L11. Cadena de custodia limitada al repositorio

La cadena de custodia se basa en:
- SHA-256 de snapshots ONPE.
- Commits git con timestamp.
- Hash de documentos metodológicos.

**No se tiene:** certificación notarial, time-stamping RFC3161, firma
digital acreditada. Para peritaje oficial con valor judicial, el perito
acreditado debe incorporar cadena de custodia formal adicional.

---

## Conclusión de honestidad

Esta auditoría es **evidencia técnica ciudadana reproducible**. Para
convertirse en **peritaje oficial admisible judicialmente**, requiere:

1. Perito acreditado colegiado que firme.
2. Cadena de custodia notarial/RFC3161.
3. Data ONPE/JEE bajo apercibimiento (M3, M4, logs).
4. Segunda opinión independiente (perito contraparte o OEA/UE).

Sin estos, el peso probatorio es de **indicios + pedido de apercibimiento**,
no de prueba plena. Eso es honestidad, no debilidad — el sistema judicial
decide a qué nivel elevarse.
