# Resumen Ejecutivo — Auditoría Estadística EG2026 1ra vuelta

**Destinatario:** Perito estadístico acreditado (por definir colegiatura).
**Emisor:** Jack Aguilar, Neuracode — Aporte ciudadano sin afiliación.
**Fecha:** 2026-04-17
**Corte ONPE analizado:** 93.17% de actas contabilizadas.

---

## Contexto

Elecciones Generales Perú 2026, 1ra vuelta, 12 de abril. Margen
Sánchez−RLA: **+13,624 votos al corte 93.474% (2026-04-18)** — oscila con cada corte
(valor histórico al 93.17%: +5,898). Tercer vs cuarto puesto separados por ~0.086 pp.
El resultado final decide el pase a segunda vuelta. *Valor vivo: `data/processed/meta.json → margen_sanch_rla_votos`.*

---

## Hallazgos principales (15 en total, priorizados por severidad)

### CRÍTICO

| ID | Descripción | Fuente |
|----|-------------|--------|
| E1 | Pase a 2ª vuelta depende de resolución JEE (5,555 actas en JEE afectan margen) | Pipeline |
| F1 | Modelo bayesiano Dirichlet-Multinomial: **P(RLA supera Sánchez) = 42.6%** central, 42.2% mixto (n=10,000 simulaciones) | Linzer 2013 |

### ALTA

| ID | Descripción | Fuente |
|----|-------------|--------|
| A-AUS-3 | Ratio 4.64× entre electores afectados por CALAG/Galaga en Lima (63,300) y margen vigente al corte 93.474% (13,624). Abre Art. 363 Ley 26859 | Comparación ausentismo |

### MEDIA

| ID | Descripción | Fuente |
|----|-------------|--------|
| A0 | Inconsistencia agregación ONPE: 21 actas movidas (max\|diff\|) nacional vs suma regional. ~4,582 votos potenciales (ratio 0.78× margen — por debajo). Requiere explicación formal de ONPE aunque no alcanza el margen | Reconcile interno |

### MEDIA

| ID | Descripción | Fuente |
|----|-------------|--------|
| A1 | Extranjero tasa impugnación 24.11%, z=+3.66 (p<1/2000) | Impugnation rates |
| A-AUS-1 | Ausentismo 2026 (26.16%) supera 2016 pre-pandemia (18.21%) en +7.95 pp, ~3.0M electores adicionales no votaron | Ausentismo |
| G1 | Correlación impug × share_RLA regional: Pearson r=0.477 p=0.014 (borderline); Spearman NS; bootstrap CI95 incluye 0 | Impugnation bias |
| H1 | Cambio velocidad JEE ±6h alrededor del cruce Sánchez>RLA (Mann-Whitney p=0.013) | Impugnation velocity |
| H2 | **Desaceleración** post-cruce 0.45× (contradice narrativa viral de "aceleración") | Impugnation velocity |
| M2 | Clustering espacial propio de RLA (Moran's I=+0.317 p=0.011); bivariado RLA×impug aleatorio (p=0.837) — NO hay co-clustering adverso | Spatial cluster |

### INFO (reportados por honestidad)

| ID | Descripción | Fuente |
|----|-------------|--------|
| R1 | Reconciliación Σ regional vs nacional: coincide dentro redondeo | Reconcile |
| C1 | Benford primer dígito conforme | Benford |
| D1-D3 | Sin anomalías temporales en captura | Temporal |
| M1 | Último dígito regional conforme (Mebane/Beber-Scacco) | Last digit |
| A-AUS-2 | Ausentismo 2026 está **debajo** de 2021 (pandemia) | Ausentismo |

---

## Lo que esta auditoría NO afirma (honestidad estadística obligatoria)

1. **No imputa fraude ni dolo.** Ninguno de los 15 findings constituye
   prueba de dolo. Son anomalías estadísticas que requieren explicación
   formal de ONPE/JEE.
2. **No descarta fraude.** Varios tests fueron hechos con n pequeño
   (n=26 regiones) o data agregada. El peritaje profundo requiere data
   mesa-a-mesa bajo apercibimiento.
3. **No confirma narrativa de "Operación Morrocoy" ni "digitadores
   venezolanos".** Sin fuente verificable, se excluyen.
4. **Hallazgos adversos reportados.** 2026 tiene menor ausentismo que
   2021 (pandemia); M2 bivariado no confirma focalización contra RLA;
   G1 es borderline no robusto.

---

## Preguntas concretas que requieren peritaje

1. **¿Por qué 42 actas no reconcilian nacional vs regional?** (A0)
2. **¿Quién definió el contrato excepcional con CALAG/Galaga y bajo qué
   criterio?** (A-AUS-3)
3. **¿La desaceleración JEE post-cruce es política o natural?** (H2)
4. **¿El clustering espacial de RLA es geografía natural o selección
   adversa?** (M2)
5. **¿El 42.6% P(RLA>Sánchez) se confirma al integrar las 5,555 actas
   pendientes?** (F1)

---

## Estructura del dossier

- `00_RESUMEN_EJECUTIVO.md` (este doc)
- `01_METODOLOGIA.md` — métodos con citas peer-review
- `02_HALLAZGOS.md` — finding-by-finding con severidad
- `03_HIPOTESIS_PREREGISTRADAS.md` — H1–H5 con hash git
- `04_CADENA_CUSTODIA.md` — SHA-256 de snapshots y data
- `05_LIMITACIONES.md` — lo que NO se puede afirmar
- `code/` — scripts reproducibles (Python, MIT licensed)
- `data/` — snapshots ONPE con hash
- `reports/` — outputs JSON y findings.json

---

**Licencia:** CC-BY-4.0 (documentos), MIT (código).
**Repositorio público:** `github.com/jackthony/auditoria-eg2026`
