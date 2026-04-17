# Auditoría Técnico-Estadística · Elecciones Generales 2026 — Perú

[![Licencia](https://img.shields.io/badge/código-MIT-blue)]() [![Docs](https://img.shields.io/badge/docs-CC--BY--4.0-green)]() [![Reproducible](https://img.shields.io/badge/reproducible-SHA256-orange)]()

> **Aporte ciudadano independiente.** Sin afiliación política ni institucional.
> Data pública · código abierto · hashes verificables · reproducible por terceros.

---

## TL;DR

Al corte **92.91%** del escrutinio oficial ONPE (2026-04-16 09:58 UTC):

- Sánchez: 1,881,625 votos · López Aliaga: 1,875,852 votos.
- Margen Sánchez − López Aliaga: **+5,773 votos** (+0.037 pp).
- Actas impugnadas (JEE): **4,959** · Actas pendientes: varían por región.
- **Conclusión**: la definición del pase a 2ª vuelta depende de la resolución del Jurado Electoral Especial (JEE) sobre actas en disputa. El universo de votos en actas fuera del conteo excede por ~2 órdenes de magnitud el margen actual.

Dashboard en vivo: `web/index.html` (auto-refresh 5 min).

**Este repositorio NO afirma fraude electoral**. Documenta patrones estadísticos anómalos que ameritan respuesta formal de las autoridades electorales.

---

## Hallazgos (resumen)

| ID | Severidad | Hallazgo |
|---|---|---|
| E1 | **CRÍTICO** | Definición del 2° lugar depende de resolución JEE |
| A1 | MEDIA | Extranjero: tasa impugnación 24.11% (z=+3.66) |
| A2 | MEDIA | Asimetría Lima+Callao vs resto (z=−17.17, p<0.01) |
| R1 | INFO | Reconciliación Σ regional vs nacional: OK |
| C1 | INFO | Benford primer dígito: conforme (p=0.168) |
| D1 | INFO | 72 artefactos de caché del proxy (NO de ONPE) |
| D2 | INFO | Sin saltos anómalos en serie temporal (116 cortes) |
| D3 | INFO | 1 cruce Sánchez↔RLA consistente con flujo geográfico |

---

## Qué hay en este repo

```
.
├── README.md                         Este archivo
├── METHODOLOGY.md                    Metodología detallada
├── CHAIN_OF_CUSTODY.md               Procedimiento de cadena de custodia
├── LICENSE                           MIT (código) + CC-BY-4.0 (docs)
├── captures/                         Snapshots atómicos con SHA-256
│   └── YYYYMMDDTHHMMSSZ/
│       ├── raw/*.json                Data tal como llegó de ONPE
│       ├── MANIFEST.jsonl            Hashes + metadata de captura
│       └── README.md                 Descripción humana
├── data/processed/                   Datasets procesados
│   ├── regiones.csv                  26 regiones × 16 columnas
│   ├── tracking.csv                  116 cortes temporales
│   └── meta.json
├── reports/
│   ├── Informe_Tecnico_RP_v2.pdf     Informe ejecutivo completo
│   ├── findings.json                 Hallazgos estructurados
│   ├── summary.txt                   Resumen técnico
│   └── figures/                      Figuras del informe
├── src/
│   ├── capture/fetch_onpe.py         Captura atómica
│   ├── capture/verify_manifest.py    Verificación SHA-256
│   ├── process/build_dataset.py      Construcción del dataset
│   └── analysis/run_all.py           Pipeline de análisis
└── scripts/
    ├── capture_loop.py               Bucle continuo
    └── build_pdf.py                  Generador del PDF
```

---

## Reproducir el análisis

### Requisitos

- Python 3.11+
- `pip install -r requirements.txt`

### Verificar integridad de capturas

```bash
py src/capture/verify_manifest.py captures/20260417T062711Z/
```

Cada archivo debe pasar el check SHA-256. Un MISMATCH indica modificación posterior a la captura.

### Re-ejecutar el pipeline completo

```bash
py src/capture/fetch_onpe.py           # captura fresca (atómica)
py src/process/build_dataset.py        # procesa a CSV
py src/analysis/run_all.py             # corre tests y genera reports/
py scripts/build_pdf.py                # genera el PDF ejecutivo
```

### Captura continua (cada 15 min)

```bash
py scripts/capture_loop.py --interval 15
```

---

## Metodología

Ver `METHODOLOGY.md` para el detalle. Resumen:

1. **Captura atómica** de endpoints públicos ONPE, con `User-Agent` identificado y hash SHA-256 inmediato.
2. **Cadena de custodia**: manifiesto con timestamp ISO-8601 UTC, IP pública, hostname, git commit.
3. **Tests aplicados**:
   - Reconciliación Σ regional ↔ nacional.
   - z-score de la tasa de impugnación por región.
   - z-test de dos proporciones Lima+Callao vs resto.
   - Ley de Benford (χ², gl=8) sobre primer dígito.
   - Serie temporal del conteo sobre 116 cortes.
   - Simulación contrafactual del resultado JEE.

---

## Limitaciones

El análisis tiene alcance acotado deliberadamente:

- Solo data pública agregada por región. No hay acceso al módulo de descarga masiva para organizaciones políticas.
- No se realizó OCR ni cotejo acta-por-acta de los PDFs digitalizados.
- No hay acceso a logs internos de ONPE (STAE, ODPE, centro de cómputo).
- Los tests estadísticos no son concluyentes por sí solos: un adversario sofisticado podría fabricar data que pase todos los tests.
- Sin línea base histórica: pendiente comparar contra EG2021, EG2016, EG2011.

---

## Cómo contribuir

Este trabajo se beneficia de réplica y crítica por terceros.

- **Encontraste un error**: abrí un issue con detalle y evidencia.
- **Mejoras de código**: pull request con tests.
- **Ampliación de análisis**: forkear, ampliar, citar.
- **Reportes regionales específicos**: abrir issue con la región de interés.

---

## FAQ

**¿Esto prueba fraude electoral?**
No. Ningún análisis estadístico sobre data agregada puede probar intención ni coordinación. Documenta patrones que requieren respuesta formal.

**¿Por qué no uso datos mesa-por-mesa?**
El módulo de descarga masiva para organizaciones políticas aún no está habilitado al momento del corte. Cuando lo habilite ONPE, la auditoría puede profundizarse.

**¿Quién financia este trabajo?**
Nadie. Es un aporte ciudadano en tiempo personal. Sin afiliación política ni retribución económica.

**¿Puedo usar el código y los datos?**
Sí. Código bajo MIT, documento bajo CC-BY-4.0. Solo preservá la atribución y el historial de modificaciones.

**¿Cómo verifico que los archivos no fueron alterados?**
Ejecuta `py src/capture/verify_manifest.py captures/<timestamp>/`. Cada hash SHA-256 debe coincidir con el registrado en el MANIFEST.

---

## Contacto

Issues del repositorio. Este trabajo se entrega sin afiliación política ni institucional.

---

## Licencia

- **Código**: MIT License. Ver `LICENSE`.
- **Documentos** (PDF, Markdown): Creative Commons BY 4.0.
