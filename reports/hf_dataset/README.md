---
license: cc-by-4.0
language:
- es
tags:
- elections
- peru
- onpe
- electoral-audit
- mesa-a-mesa
pretty_name: ONPE EG2026 — Resultados mesa a mesa (primera vuelta)
size_categories:
- 1M<n<10M
---

# ONPE EG2026 — Resultados electorales mesa a mesa

**Fuente:** API pública ONPE (`resultadoelectoral.onpe.gob.pe`)
**Captura:** `20260419T035056Z` UTC — SHA-256 en [MANIFEST.jsonl](https://github.com/jackthony/auditoria-eg2026)
**Licencia:** CC-BY-4.0 — datos electorales públicos por naturaleza (Ley 26859)
**Proyecto:** [auditoria-eg2026](https://github.com/jackthony/auditoria-eg2026) · Jack de Neuracode

## Descripción

Dataset long-format con los resultados presidenciales (idEleccion=10) de la primera vuelta
de las Elecciones Generales del Perú 2026 (12 abril 2026), extraídos mesa a mesa desde
la API oficial de la ONPE.

- **88,063 mesas** | **3,597,343 filas** (1 fila = mesa × partido)
- Incluye: votos por partido, candidato presidencial, estado del acta, electores hábiles
- `estadoActa`: D=Contabilizada, I=Impugnada, P=Pendiente, O=Observada

## Schema

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_mesa` | str | Código ONPE de 6 dígitos |
| `ubigeo` | str | Ubigeo 6 dígitos (depto+prov+dist) |
| `departamento` | str | Nombre del departamento |
| `estado_acta` | str | D/I/P/O |
| `electores_habiles` | Int64 | Padrón habilitado en la mesa |
| `votos_emitidos` | Int64 | Total votos emitidos |
| `votos_validos` | Int64 | Votos válidos (excluye nulos/blancos) |
| `pct_participacion` | float32 | % participación ciudadana |
| `local_votacion` | str | Nombre del local de votación |
| `partido_codigo` | str | Código agrupación política ONPE |
| `partido` | str | Nombre del partido |
| `candidato` | str | Apellidos, Nombres del candidato presidencial |
| `votos` | Int64 | Votos obtenidos (null si acta impugnada) |
| `pct_votos_validos` | float32 | % sobre votos válidos |
| `es_voto_especial` | bool | True = NULOS o BLANCOS |

## Uso rápido

```python
import pandas as pd

df = pd.read_parquet("onpe_eg2026_mesas_20260419T035056Z.parquet")

# Resultados presidenciales nacionales
nacional = (
    df[~df.es_voto_especial]
    .groupby("partido")["votos"]
    .sum()
    .sort_values(ascending=False)
)

# Mesas impugnadas por departamento
imp = df[df.estado_acta == "I"].groupby("departamento")["codigo_mesa"].nunique()
```

## Hallazgos del proyecto de auditoría

Ver [reports/findings.json](https://github.com/jackthony/auditoria-eg2026/blob/main/reports/findings.json)
y el [dashboard público](https://jackthony.github.io/auditoria-eg2026/).

## Cadena de custodia

Cada captura incluye MANIFEST.jsonl con SHA-256 por archivo, timestamp UTC y URL de origen.
Verificar con: `python src/capture/verify_manifest.py captures/20260419T035056Z/`

## Cita

```bibtex
@dataset{neuracode2026onpe,
  author    = {Aguilar, Jack},
  title     = {ONPE EG2026 — Resultados mesa a mesa (primera vuelta)},
  year      = {2026},
  publisher = {HuggingFace},
  url       = {https://huggingface.co/datasets/neuracode/onpe-eg2026-mesa-a-mesa},
  note      = {Captura 20260419T035056Z UTC. Datos públicos ONPE. CC-BY-4.0.}
}
```
