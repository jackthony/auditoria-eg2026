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
- forensic-statistics
pretty_name: ONPE EG2026 — Resultados mesa a mesa (primera vuelta)
size_categories:
- 1M<n<10M
---

# ONPE EG2026 — Resultados electorales mesa a mesa

**Fuente:** API pública ONPE (`resultadoelectoral.onpe.gob.pe`)
**Captura:** `20260420T074202Z` UTC — SHA-256 en [MANIFEST.jsonl](https://github.com/jackthony/auditoria-eg2026)
**Licencia:** CC-BY-4.0 — datos electorales públicos por naturaleza (Ley 26859)
**Proyecto:** [auditoria-eg2026](https://github.com/jackthony/auditoria-eg2026) · Jack de Neuracode

## Descripción

Dataset long-format con los resultados presidenciales (idEleccion=10) de la primera vuelta
de las Elecciones Generales del Perú 2026 (12 abril 2026), extraídos mesa a mesa desde
la API oficial de la ONPE.

- **92,766 mesas** (88,063 normales + 4,703 especiales 900k+) | **3,793,246 filas** (1 fila = mesa × partido)
- Universo verificado por barrido de bordes (`reports/universe_check.json`)
- Captura validada al **100% vs totales oficiales ONPE** en los 26 departamentos
- `estadoActa`: D=Contabilizada, I=Impugnada, P=Pendiente, O=Observada

## Universo de mesas (verificación)

| Grupo | Rango | N | Nota |
|-------|-------|---|------|
| Normales | 000001-088064 | 88,063 | Gap conocido en 087704 |
| Especiales 900k+ | 900001-904703 | 4,703 | Centros excepcionales (universidades, ESSALUD, IE distribuidas) |
| **TOTAL** | — | **92,766** | Confirmado vs oficial 100% por depto |

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
| `partido_codigo` | str | Código agrupación política ONPE (`80`=BLANCOS, `81`=NULOS, `82`=IMPUGNADOS) |
| `partido` | str | Nombre del partido |
| `candidato` | str | Apellidos, Nombres del candidato presidencial |
| `votos` | Int64 | Votos obtenidos (null si acta impugnada) |
| `pct_votos_validos` | float32 | % sobre votos válidos |
| `es_voto_especial` | bool | True = NULOS o BLANCOS (flag de fila, no de mesa) |

## Uso rápido (Polars + DuckDB recomendado)

```python
import polars as pl

df = pl.read_parquet("onpe_eg2026_mesas_20260420T074202Z.parquet")

# Resultados presidenciales nacionales (excluye blanco/nulo/impugnado)
nacional = (
    df.filter(~pl.col("partido_codigo").is_in(["80", "81", "82"]))
      .group_by("partido")
      .agg(pl.col("votos").sum())
      .sort("votos", descending=True)
)

# Mesas impugnadas por departamento
imp = (df.filter(pl.col("estado_acta") == "I")
         .group_by("departamento")
         .agg(pl.col("codigo_mesa").n_unique()))
```

```python
import duckdb

# SQL sobre parquet directo (sin cargar a memoria)
duckdb.sql("""
  SELECT departamento,
         COUNT(DISTINCT codigo_mesa) AS mesas,
         SUM(votos) FILTER (WHERE partido_codigo NOT IN ('80','81','82')) AS validos
  FROM 'onpe_eg2026_mesas_20260420T074202Z.parquet'
  GROUP BY 1 ORDER BY 2 DESC
""").pl()
```

> Nota: pandas funciona pero se cuelga con datasets así de grandes en máquinas modestas.
> Recomendado polars (Rust-backed) o duckdb (SQL columnar in-process).

## Hallazgos del proyecto de auditoría (versión 0420-v2-92k)

| ID | Severidad | Hallazgo | Métrica |
|----|-----------|----------|---------|
| HALL-0420-H1 | CRÍTICO | Sesgo geográfico impugnadas | Extranjero 26.27% (z=42.2) · Loreto 14.87% · Ucayali 12.02% · global 6.16% |
| HALL-0420-H2 | MEDIA | Partidos concentran en locales alta-imp | FP +2.07pp · JPP +0.88pp · BUEN GOBIERNO -1.62pp |
| HALL-0420-H3 | MEDIA | Outliers nulos/blancos | 5,304 mesas (5.72%) · San Martín 19.62% blancos #1 · Loreto mesas 900k+ >90% blancos |
| HALL-0420-H4 | CRÍTICO | JPP concentra en mesas 900k+ | JPP **41.65% en 4,700 mesas especiales** vs 10.91% en normales · ratio **3.82x** · z=698 · Cohen h=0.73 (grande) · IC95 [0.295, 0.308] |

Detalles completos: [findings.json](https://github.com/jackthony/auditoria-eg2026/blob/main/reports/findings.json) ·
[HALLAZGOS_VIGENTES.md](https://github.com/jackthony/auditoria-eg2026/blob/main/HALLAZGOS_VIGENTES.md)

**Metodología:** z-test 2-prop (Newcombe 1998), Cohen's h (1988), Bootstrap percentil IC95
(Efron-Tibshirani 1993, B=10,000), Mann-Whitney U. Benford-1 NO usado (criticado para datos
electorales por Deckert/Myagkov/Ordeshook 2011).

## Cadena de custodia (4 niveles)

| Nivel | Ubicación | Prueba inmutable |
|-------|-----------|------------------|
| 1 · Local | `captures/20260420T074202Z/MESAS_MANIFEST.jsonl` | SHA-256 por archivo + UA + IP |
| 2 · GitHub | [jackthony/auditoria-eg2026](https://github.com/jackthony/auditoria-eg2026) | Commit `916e77d` · tag `v2-92k` |
| 3 · HuggingFace | Este dataset (parquet) | Revisión inmutable HF |
| 4 · IPFS Filebase | Content-addressed (ver abajo) | CID = hash del contenido |

Verificar SHA-256 local: `python src/capture/verify_manifest.py captures/20260420T074202Z/`

## Verificación IPFS (content-addressed)

Los 3 artefactos críticos están pineados en IPFS via Filebase. Cualquier gateway IPFS los sirve:

| Archivo | CID | URL pública |
|---------|-----|-------------|
| MESAS_MANIFEST.jsonl | `QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS` | [ipfs.filebase.io](https://ipfs.filebase.io/ipfs/QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS) |
| parquet 3.79M actas | `QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L` | [ipfs.filebase.io](https://ipfs.filebase.io/ipfs/QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L) |
| findings H1-H4 | `QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp` | [ipfs.filebase.io](https://ipfs.filebase.io/ipfs/QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp) |

Gateways alternativos (mismo CID, distinta ruta): `ipfs.io/ipfs/<CID>` · `dweb.link/ipfs/<CID>`.
El CID **es** el hash del archivo: si alguien altera 1 byte, el CID cambia. No hay forma de falsificar.

## Seguridad de datos

**Principio:** datos públicos electorales (Ley 26859) + código open-source + metodología reproducible.

| Qué | Política |
|-----|----------|
| Datos ONPE | Públicos. CC-BY-4.0. Fuente: `resultadoelectoral.onpe.gob.pe` |
| Tokens HF / Filebase / Pinata | En `.env` local (gitignored). **Nunca** commiteados. Rotados ante cualquier exposición |
| `.claude/settings.local.json` | Gitignored. Solo `.claude/settings.json` + `agents/` + `rules/` son públicos |
| MANIFEST SHA-256 | Commit firmado en GitHub. Inmutable por convención + content-addressing IPFS |
| Capturas `captures/{ts}/` | Inmutables. Re-captura = carpeta nueva UTC + commit inmediato |

Si detectas una credencial en este repo, abre un issue privado. El proyecto tiene política de rotación inmediata.

## Reproducibilidad

```bash
# 1. Clonar y preparar entorno
git clone https://github.com/jackthony/auditoria-eg2026 && cd auditoria-eg2026
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt

# 2. Descargar parquet desde HuggingFace o IPFS
huggingface-cli download Neuracode/onpe-eg2026-mesa-a-mesa --repo-type dataset
# o: curl -L -o dataset.parquet https://ipfs.filebase.io/ipfs/QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L

# 3. Rebuild DuckDB autoritativa
python scripts/build_duckdb_and_fix.py

# 4. Re-ejecutar análisis (genera findings_consolidado_0420.json)
python scripts/analyze_hallazgos_0420_v2.py
python scripts/stats_h4_especiales_900k.py

# 5. Pinear a IPFS (requiere FILEBASE_* en .env)
python scripts/pin_to_filebase.py
```

## Cita

```bibtex
@dataset{neuracode2026onpe,
  author    = {Aguilar, Jack},
  title     = {ONPE EG2026 — Resultados mesa a mesa (primera vuelta)},
  year      = {2026},
  publisher = {HuggingFace},
  url       = {https://huggingface.co/datasets/Neuracode/onpe-eg2026-mesa-a-mesa},
  note      = {Captura 20260420T074202Z UTC. 92,766 mesas. Datos públicos ONPE. CC-BY-4.0.}
}
```
