# Auditoría Técnica EG2026 — Escrutinio ONPE

[![Dashboard live](https://img.shields.io/badge/dashboard-live-2E6B3F?style=for-the-badge)](https://jackthony.github.io/auditoria-eg2026/)
[![Memorial Fiscal](https://img.shields.io/badge/memorial-fiscal_de_la_naci%C3%B3n-B4332B?style=for-the-badge)](docs/MEMORIAL_TECNICO_FISCAL.md)
[![Licencia MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**Análisis técnico-estadístico reproducible del conteo oficial de la Oficina Nacional de Procesos Electorales (ONPE) para las Elecciones Generales 2026 de Perú.**

> Este repositorio NO es un informe pericial con validez probatoria. Es un análisis técnico reproducible que cualquier tercero puede re-ejecutar contra fuentes oficiales de ONPE para verificar los cálculos. La palabra "forense" se reserva para el enfoque metodológico (cadena de custodia, hashes, trazabilidad), no implica calidad pericial-judicial.

---

## Estado actual (al último snapshot publicado)

- **Dashboard público:** https://jackthony.github.io/auditoria-eg2026/
- **Corte:** 93.23 % de actas contabilizadas (117 snapshots de la serie temporal).
- **Definición 2° lugar:** disputa entre **Phillip Butters Sánchez (PB Sánchez)** y **Rafael López Aliaga (RLA)** — margen vivo +13,624 votos (+0.086 pp) a favor de Sánchez.
- **Memorial técnico ciudadano** entregado al Fiscal de la Nación: [`docs/MEMORIAL_TECNICO_FISCAL.md`](docs/MEMORIAL_TECNICO_FISCAL.md) — **11 hechos verificables** + 18 variables solicitadas bajo apercibimiento. Incluye:
  - Hecho 9 (CALAG): 63,300 electores impedidos / margen actual = **ratio 10.73×**.
  - Hecho 11 (Surquillo + denuncia penal JNE→ONPE de 2026-04-17).
- **Loop de captura+publicación** automatizado: `scripts/capture_loop.py --interval 15 --publish`.

Los números cambian con cada snapshot. La fuente única de verdad es `web/data.json` + `reports/findings.json`.

---

## Índice
- [1. Qué hace este proyecto](#1-qué-hace-este-proyecto)
- [2. Requisitos](#2-requisitos)
- [3. Instalación (Windows)](#3-instalación-windows)
- [4. Uso](#4-uso)
- [5. Cadena de custodia](#5-cadena-de-custodia)
- [6. Cómo verifica un tercero](#6-cómo-verifica-un-tercero)
- [7. Estructura del repositorio](#7-estructura-del-repositorio)
- [8. Licencia y autoría](#8-licencia-y-autoría)

---

## 1. Qué hace este proyecto

Descarga los datos públicos del escrutinio desde el backend oficial de ONPE
(`resultadoelectoral.onpe.gob.pe/presentacion-backend`, vía proxy CORS de respaldo),
los hashea para cadena de custodia, ejecuta pruebas estadísticas estándar de
integridad electoral y genera tres salidas: dashboard público (HTML/JSON),
memorial técnico (Markdown/PDF) e informe Word.

**Análisis incluidos:**
- Reconciliación de totales nacional ↔ regional (finding A0).
- Tasa de impugnación por región (z-score, detección de outliers).
- Estratificación geográfica (Lima+Callao vs resto vs sur andino vs Extranjero).
- Ley de Benford (primer dígito, χ² gl=8) sobre votos por candidato — **señal complementaria, NO evidencia única**.
- Análisis de serie temporal (detección de saltos, velocidad de procesamiento).
- Forecast bayesiano P(2° lugar = RLA) — método NYT Election Needle / Linzer 2013.
- Sesgo direccional de impugnación (Lima+Callao vs resto).
- Comparación histórica de ausentismo 2016/2021/2026.
- Simulación de impacto de actas JEE sobre el margen del 2º lugar.
- Cluster espacial (Moran-I) y forense de último dígito.

**Lo que NO hace (todavía):**
- Cotejo acta por acta de PDFs digitalizados (requiere acceso al módulo para
  organizaciones políticas, pendiente de habilitación por ONPE).
- Reconstrucción del pipeline STAE interno (requiere code review autorizado).
- Verificación física de las 1,200 cédulas de Surquillo (atribución exclusiva del Ministerio Público).

---

## 2. Requisitos

| Software | Versión mínima | Comando para verificar |
|---|---|---|
| Windows / macOS / Linux | — | — |
| Python | 3.11+ | `py --version` |
| Git | 2.40+ | `git --version` |
| (Opcional) GPG | 2.4+ | `gpg --version` |
| (Opcional) GitHub CLI | 2.40+ | `gh --version` |

Instala Python desde https://python.org si no lo tienes. **Importante:** en el
instalador marca la casilla *"Add Python to PATH"*.

---

## 3. Instalación (Windows)

Abre **PowerShell** y ejecuta:

```powershell
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026

py -m venv .venv
# Si PowerShell te bloquea por política de ejecución, corre esto una vez:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

py -m pytest tests/ -q
```

Si los tests pasan, ya puedes usar el proyecto.

---

## 4. Uso

Todos los comandos asumen venv activado (`.\.venv\Scripts\Activate.ps1`).

### 4.1 Captura puntual desde ONPE

```powershell
py src\capture\fetch_onpe.py
```

Genera `captures\{timestamp_UTC}\` con `raw/*.json`, `MANIFEST.jsonl` (SHA-256 + IP + commit) y `README.md` humano. **Ejecutar desde IP peruana — ONPE bloquea datacenters extranjeros (403).**

### 4.2 Pipeline completo (captura → análisis → reporte)

```powershell
py src\process\build_dataset.py        # Consolida CSVs desde la última captura
py -m src.analysis.run_all             # Ejecuta todos los análisis estadísticos
py src\report\figures.py               # Genera las figuras PNG
py src\report\build_report.py          # Arma el informe .docx
py scripts\build_dashboard_json.py     # Refresca web/data.json (dashboard público)
```

Output final: `reports\Informe_Tecnico_v{N}.docx` + `web\data.json`.

### 4.3 Loop automático con auto-publicación

```powershell
py scripts\capture_loop.py --interval 15 --publish
```

Cada 15 min: captura → si cambió el snapshot → re-procesa todo → commit a `main` → `subtree push` a `gh-pages` → dashboard se actualiza solo. Para correrlo en background persistente, usar Task Scheduler de Windows o un servicio nssm.

### 4.4 Exploración interactiva

```powershell
jupyter lab
```

Abrir `notebooks\01_exploratory.ipynb`. Útil durante audiencia o conferencia.

---

## 5. Cadena de custodia

Cada captura genera estos archivos en `captures\{timestamp_UTC}\`:

| Archivo | Contenido |
|---|---|
| `MANIFEST.jsonl` | Una línea por archivo: ruta, tamaño, SHA-256, timestamp ISO-8601, URL origen, User-Agent, IP pública del capturante, hostname, commit git vigente, `cf-cache-status` y `age` del proxy |
| `raw\*.json` | Contenido exacto devuelto por ONPE, sin modificar |
| `README.md` | Condiciones de la captura: hora, lugar, dispositivo |

Tras cada captura, commit inmediato:

```powershell
git add captures\20260417T*
git commit -S -m "capture: ONPE presentacion-backend at 06:27 UTC"
git push
```

El commit queda inmutable en GitHub con timestamp verificable. Ningún byte puede alterarse retroactivamente sin romper la cadena.

> Detalles del fix de cache-busting al proxy CORS (Cloudflare Workers) en `src/capture/fetch_onpe.py` (commit `e6ffe80`).

---

## 6. Cómo verifica un tercero

Cualquiera que quiera auditar la auditoría hace esto:

```powershell
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Verifica que los hashes del manifiesto coinciden con los archivos
py src\capture\verify_manifest.py captures\<TIMESTAMP_UTC>\

# 2) Re-ejecuta todo el análisis sobre la misma captura
py src\process\build_dataset.py
py -m src.analysis.run_all

# 3) Compara los outputs contra los publicados en reports/ y web/
fc reports\findings.json reports\findings_publicado.json
```

Si cualquier byte cambió, `verify_manifest.py` falla con código ≠ 0 y reporta el archivo afectado.

---

## 7. Estructura del repositorio

```
auditoria-eg2026/
├── README.md                          ← este archivo
├── METHODOLOGY.md                     ← tests aplicados, referencias académicas
├── CHAIN_OF_CUSTODY.md                ← protocolo formal de captura
├── CLAUDE.md                          ← guía para colaboradores con Claude Code
├── LICENSE                            ← MIT
├── requirements.txt                   ← dependencias Python pinneadas
├── .gitignore  ·  .gitattributes
│
├── captures/                          ← snapshots con timestamp UTC, NUNCA se editan
│   └── 20260417T062711Z/
│       ├── MANIFEST.jsonl
│       ├── README.md
│       └── raw/
│
├── src/
│   ├── capture/                       ← fetch_onpe, hash_manifest, verify_manifest
│   ├── process/                       ← build_dataset, reconcile
│   ├── analysis/                      ← reconcile, impugnation_rates, benford, temporal,
│   │                                    jee_simulation, forecast_bayesian, impugnation_bias,
│   │                                    impugnation_velocity, last_digit_forensic,
│   │                                    spatial_cluster, reconcile_internal
│   └── report/                        ← figures, build_report
│
├── scripts/                           ← capture_loop, build_dashboard_json, docx_to_txt
│
├── web/                               ← dashboard público (servido por GitHub Pages → branch gh-pages)
│   ├── index.html
│   ├── data.json                      ← regenerado en cada loop
│   └── README.md
│
├── docs/
│   ├── MEMORIAL_TECNICO_FISCAL.md     ← memorial al Fiscal de la Nación (11 hechos)
│   ├── PRE_REGISTRO_H1_H5.md          ← pre-registro de hipótesis (anti-p-hacking)
│   ├── FALLAS_TECNICAS_VERIFICADAS.md ← cada falla con fuente pública
│   ├── EVIDENCIA_CIUDADANA.md         ← versión pública de testimonios
│   ├── HIPOTESIS_CIENTIFICAS.md       ← H1-H5 con metodología
│   ├── TESTS_FORENSES_EXTENDIDOS.md
│   └── SESION_2026-04-17.md           ← bitácora del corte 92.91%
│
├── data/
│   ├── processed/                     ← CSVs derivados, regenerables
│   └── external/                      ← referencias (ubigeos, padrón agregado)
│
├── reports/
│   ├── figures/                       ← PNGs de las figuras del informe
│   ├── findings.json                  ← hallazgos consolidados con severidad
│   ├── forecast.json                  ← P(2° lugar) bayesiano
│   ├── impugnation_bias.json
│   ├── impugnation_velocity.json
│   ├── reconcile_internal.json        ← finding A0 (consistencia agregador ONPE)
│   ├── ausentismo_comparacion.json
│   ├── last_digit.json
│   ├── spatial_cluster.json
│   ├── summary.txt
│   └── Informe_Tecnico_v1.docx
│
├── evidence/
│   ├── legal_references/              ← Resoluciones JNE, LOE, jurisprudencia
│   ├── public_documents/              ← oficios Congreso, notas oficiales, denuncias
│   └── personero_copies/              ← copias físicas de actas (privado por defecto)
│
├── tests/                             ← pruebas unitarias del pipeline
└── notebooks/
    └── 01_exploratory.ipynb           ← análisis en vivo
```

---

## 8. Licencia y autoría

Código bajo licencia **MIT** (ver `LICENSE`). Los datos capturados de ONPE son
públicos por su propia naturaleza electoral.

**Autor del análisis:** **Jack Aguilar** — Ingeniero de software, fundador de **Neuracode**. La firma del autor implica responsabilidad técnica por los cálculos, no vocería política. Las herramientas de IA generativa pueden haber asistido en la redacción del código y del informe; la revisión, ejecución y validación son responsabilidad humana.

**Canales públicos:**

- TikTok: [`@JackDeNeuracode`](https://www.tiktok.com/@JackDeNeuracode)
- Facebook / Instagram: [`@neuracode`](https://www.instagram.com/neuracode)
- GitHub: [`@jackthony`](https://github.com/jackthony)
- Repositorio: https://github.com/jackthony/auditoria-eg2026
- Dashboard: https://jackthony.github.io/auditoria-eg2026/

**Fuente primaria:** Oficina Nacional de Procesos Electorales (ONPE) —
`resultadoelectoral.onpe.gob.pe/main/resumen` y backend asociado.

**Sin afiliación oficial** con ONPE, JNE, Reniec, ni con ninguna organización
política. Para vocería partidaria, contactar al partido directamente.

---

## Cómo contribuir

PRs bienvenidas en: tests adicionales, mejoras de visualización, cobertura de nuevos endpoints ONPE, traducción del dashboard al inglés, port a otros países (Bolivia 2025, Ecuador 2025, Colombia 2027). Lineamientos en `CLAUDE.md`.

Issues con bugs, hallazgos nuevos, o discrepancias con ONPE/JNE: usar el tracker de GitHub.
