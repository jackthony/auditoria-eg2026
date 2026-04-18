# Auditoría Técnica EG2026 — Escrutinio ONPE

**Análisis técnico-estadístico reproducible del conteo oficial de la Oficina Nacional de Procesos Electorales (ONPE) para las Elecciones Generales 2026 de Perú.**

> Este repositorio NO es un informe pericial con validez probatoria. Es un análisis técnico reproducible que cualquier tercero puede re-ejecutar contra fuentes oficiales de ONPE para verificar los cálculos. La palabra "forense" se reserva para el enfoque metodológico (cadena de custodia, hashes, trazabilidad), no implica calidad pericial-judicial.

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
(`resultadoelectoral.onpe.gob.pe/presentacion-backend`), los hashea para cadena
de custodia, ejecuta pruebas estadísticas estándar de integridad electoral y
genera un informe Word/PDF reproducible.

**Análisis incluidos:**
- Reconciliación de totales regionales vs nacional.
- Tasa de impugnación por región (z-score, detección de outliers).
- Estratificación geográfica (Lima+Callao vs resto vs sur andino).
- Ley de Benford (primer dígito, χ² gl=8) sobre votos por candidato.
- Análisis de serie temporal del conteo (detección de saltos).
- Simulación de impacto de actas JEE sobre el margen del 2º lugar.

**Lo que NO hace (todavía):**
- Cotejo acta por acta de PDFs digitalizados (requiere acceso al módulo para
  organizaciones políticas).
- Análisis espacial (Moran-I) a nivel ODPE.
- Reconstrucción del pipeline STAE interno.

---

## 2. Requisitos

| Software | Versión mínima | Comando para verificar |
|---|---|---|
| Windows | 10+ | `winver` |
| Python | 3.11+ | `py --version` |
| Git | 2.40+ | `git --version` |
| (Opcional) GPG | 2.4+ | `gpg --version` |
| (Opcional) VSCode | — | — |

Instala Python desde https://python.org si no lo tienes. **Importante:** en el
instalador marca la casilla *"Add Python to PATH"*.

---

## 3. Instalación (Windows)

Abre **PowerShell** (clic derecho al menú de Windows → "Terminal" o
"Windows PowerShell") y ejecuta:

```powershell
# 1. Clonar o descomprimir el proyecto en una carpeta
cd $HOME\Documents
# Si lo descargaste como zip, descomprímelo aquí. Si es git:
# git clone <url-de-tu-repo> auditoria-eg2026
cd auditoria-eg2026

# 2. Crear entorno virtual
py -m venv .venv

# 3. Activar el entorno virtual
# Si PowerShell te bloquea por política de ejecución, corre esto una sola vez:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 5. Verificar que todo está OK
py -m pytest tests/ -q
```

Si los tests pasan, ya puedes usar el proyecto.

---

## 4. Uso

Hay tres flujos principales. Todos asumen que tienes el venv activado
(`.\.venv\Scripts\Activate.ps1`).

### 4.1 Captura desde ONPE

```powershell
py src\capture\fetch_onpe.py
```

Esto:
1. Descarga los endpoints oficiales de ONPE a `captures\{timestamp_UTC}\raw\`.
2. Calcula SHA-256 de cada archivo.
3. Registra la captura en `captures\{timestamp_UTC}\MANIFEST.jsonl`.
4. Imprime en pantalla el resumen con los hashes.

**Importante:** ejecutalo desde tu IP peruana. ONPE bloquea datacenters extranjeros.

### 4.2 Análisis estadístico completo

```powershell
py src\process\build_dataset.py      # Consolida CSVs desde la última captura
py src\analysis\run_all.py           # Ejecuta todos los análisis
py src\report\figures.py             # Genera las figuras PNG
py src\report\build_report.py        # Arma el informe .docx
```

Output final en `reports\Informe_Tecnico_v{N}.docx`.

### 4.3 Exploración interactiva (notebooks)

```powershell
jupyter lab
```

Abrir `notebooks\01_exploratory.ipynb`. Ideal para explorar datos en vivo
durante una audiencia.

---

## 5. Cadena de custodia

Cada captura genera estos archivos en `captures\{timestamp_UTC}\`:

| Archivo | Contenido |
|---|---|
| `MANIFEST.jsonl` | Una línea por archivo: ruta, tamaño, SHA-256, timestamp ISO-8601, URL origen, User-Agent, IP pública del capturante |
| `raw\*.json` | Contenido exacto devuelto por ONPE, sin modificar |
| `README.md` | Condiciones del capture: hora, lugar, dispositivo |

Tras cada captura, commit inmediato:

```powershell
git add captures\20260417T*
git commit -S -m "capture: ONPE presentacion-backend at 06:27 UTC"
#                   ↑ -S firma con GPG (opcional pero recomendado)
git push
```

El commit queda inmutable en GitHub con timestamp verificable. Nadie puede
alterar retroactivamente el contenido sin romper la cadena.

---

## 6. Cómo verifica un tercero

Cualquiera que quiera auditar la auditoría hace esto:

```powershell
git clone <url-del-repo>
cd auditoria-eg2026
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verifica que los hashes del manifiesto coinciden con los archivos
py src\capture\verify_manifest.py captures\20260417T062711Z\

# Re-ejecuta todo el análisis
py src\process\build_dataset.py
py src\analysis\run_all.py

# Compara los outputs contra lo que está en reports/
```

Si cualquier byte cambió, `verify_manifest.py` lo detecta y falla con código ≠ 0.

---

## 7. Estructura del repositorio

```
auditoria-eg2026/
├── README.md                   ← este archivo
├── METHODOLOGY.md              ← tests aplicados, referencias académicas
├── CHAIN_OF_CUSTODY.md         ← protocolo formal de captura
├── LICENSE                     ← MIT
├── requirements.txt            ← dependencias Python pinneadas
├── .gitignore
├── .gitattributes
│
├── captures/                   ← snapshots con timestamp UTC, NUNCA se editan
│   └── 20260417T062711Z/
│       ├── MANIFEST.jsonl
│       ├── README.md
│       └── raw/
│
├── src/
│   ├── capture/                ← fetch_onpe.py, hash_manifest.py, verify_manifest.py
│   ├── process/                ← build_dataset.py, reconcile.py
│   ├── analysis/               ← benford, impugnation_rates, temporal, jee_simulation, stratification
│   └── report/                 ← figures.py, build_report.py
│
├── notebooks/
│   └── 01_exploratory.ipynb    ← análisis en vivo
│
├── data/
│   ├── processed/              ← CSVs derivados, regenerables
│   └── external/               ← referencias (ubigeos, padrón agregado)
│
├── reports/
│   ├── figures/                ← PNGs de las figuras del informe
│   ├── impugnadas_por_region.csv
│   ├── findings.json
│   ├── serie_temporal.csv
│   └── Informe_Tecnico_v1.docx
│
├── evidence/
│   ├── legal_references/       ← Reglamento JNE 0182-2025, LOE, etc.
│   ├── public_documents/       ← oficios Congreso, notas oficiales
│   └── personero_copies/       ← copias físicas de actas del partido (cuando las tengas)
│
├── tests/                      ← pruebas unitarias del pipeline
└── docs/
    └── forensic_methodology.md
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

**Fuente primaria:** Oficina Nacional de Procesos Electorales (ONPE) —
`resultadoelectoral.onpe.gob.pe/main/resumen` y backend asociado.

**Sin afiliación oficial** con ONPE, JNE, Reniec, ni con ninguna organización
política. Para la vocería partidaria, contactar al partido directamente.
