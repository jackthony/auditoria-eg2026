# Auditoría Técnica EG2026 — Escrutinio ONPE

[![Dashboard](https://img.shields.io/badge/dashboard-public-2E6B3F?style=for-the-badge)](https://jackthony.github.io/auditoria-eg2026/)
[![Licencia MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**Verificación independiente y reproducible del conteo oficial ONPE para las Elecciones Generales 2026 de Perú.**

> ⚠ **Esto NO es un informe pericial.** Es un análisis técnico reproducible: captura con SHA-256, código abierto, cualquier tercero puede re-ejecutarlo contra las APIs públicas de ONPE. La palabra "forense" refiere a la **cadena de custodia** de los datos, no a calidad pericial-judicial.

---

## Qué hace

1. **Captura atómica** el backend público ONPE (`resultadoelectoral.onpe.gob.pe/presentacion-backend`) con hash SHA-256 por archivo.
2. **Reconcilia** la suma mesa-a-mesa contra los totales oficiales (4 checks contables determinísticos).
3. **Publica** dashboard estático (GitHub Pages) actualizado cada 15 min.

## Findings públicos (conservadores)

Sólo publicamos findings defendibles sin corrección estadística adicional:

| ID | Severidad | Qué dice |
|----|-----------|----------|
| `GAP-F1-RANKING` | CRÍTICO | La suma mesa-a-mesa produce un top-10 distinto al total oficial. |
| `GAP-F2-MESAS-FALTANTES` | CRÍTICO | 4.703 mesas del universo oficial no devuelven data en la API pública. |
| `GAP-F3-DESFASE-AGRUPACION` | CRÍTICO | 566.233 votos válidos faltan al sumar mesa-a-mesa. |
| `E1` | CRÍTICO | Margen del 2° puesto entre **Roberto Helbert Sánchez Palomino** (Juntos por el Perú) y **Rafael Bernardo López Aliaga Cazorla** (Renovación Popular) es de +13.624 votos — aproximadamente 81× menor que el universo de actas pendientes del Jurado Electoral Especial. |
| `R1` · `A0` · `F1` | INFO / MEDIA | Reconciliación agregada regional vs nacional: OK. Forecast bayesiano: P(López Aliaga supera a Sánchez Palomino en el 2° puesto) = 26,9%. |

**Señales exploratorias** (Benford, Moran's I, ML-anom, correlaciones): movidas a [`docs/EXPLORATORIO.md`](docs/EXPLORATORIO.md). Requieren corrección de múltiples tests y peer-review antes de ascenso.

## Metodología

Ver [`METHODOLOGY.md`](METHODOLOGY.md). Inspirada en *election forensics* (Mebane, Linzer). Este proyecto aporta **verificación independiente**, no autoría metodológica.

## Requisitos

| Software | Mínimo |
|----------|--------|
| Python | 3.11+ |
| Git | 2.40+ |

Ejecutar desde **IP peruana** — ONPE bloquea datacenters extranjeros (403).

## Instalación

```powershell
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -m pytest tests/ -q
```

## Uso

```powershell
# Pipeline completo
py src\capture\fetch_onpe.py                     # captura agregada
py src\capture\fetch_onpe_mesas_async.py         # walker mesa-a-mesa
py -m src.analysis.run_all                       # análisis
py src\analysis\reconcile_gap.py <ts>            # findings mesa-a-mesa
py scripts\build_dashboard_json.py               # refresca web/data.json

# Loop automático con publicación a gh-pages
py scripts\capture_loop.py --interval 15 --publish
```

## Verificación por terceros

```powershell
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
py -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Verificar hashes
py src\capture\verify_manifest.py captures\<TIMESTAMP_UTC>\

# 2) Re-ejecutar análisis
py -m src.analysis.run_all

# 3) Comparar con publicados
fc reports\findings.json <tu_copia_publicada>
```

Si cualquier byte cambió, `verify_manifest.py` falla con código ≠ 0.

## Estructura

```
captures/{tsUTC}/         snapshots inmutables + MANIFEST.jsonl
src/capture/              fetch + verify + hash
src/analysis/             run_all, reconcile_gap, forecast_bayesian, …
scripts/                  capture_loop, build_dashboard_json, build_og_image
web/                      dashboard estático (gh-pages)
docs/EXPLORATORIO.md      señales estadísticas con limitaciones
docs/archive/             documentos históricos (no publicables)
METHODOLOGY.md            tests, referencias, limitaciones
CHAIN_OF_CUSTODY.md       protocolo de captura
```

## Cadena de custodia

Cada captura → `captures/{ts}/MANIFEST.jsonl` con: ruta, tamaño, SHA-256, timestamp ISO-8601, URL origen, User-Agent, IP pública, commit git. Commit inmediato a GitHub → timestamp criptográfico inmutable.

## Licencia y autoría

Código bajo **MIT**. Datos ONPE son públicos por naturaleza electoral.

**Autor:** Jack Aguilar — ingeniero de software, fundador de [Neuracode](https://neuracode.com). La firma implica responsabilidad técnica por los cálculos, no vocería política. La revisión, ejecución y validación son responsabilidad humana.

**Sin afiliación** con ONPE, JNE, Reniec ni partido político.

**Contacto:** [`@JackDeNeuracode`](https://www.tiktok.com/@JackDeNeuracode) · [`github.com/jackthony`](https://github.com/jackthony)

## Contribuir

PRs bienvenidas en: tests, cobertura de endpoints, i18n dashboard, port a otros países. Issues para bugs o discrepancias con ONPE/JNE.
