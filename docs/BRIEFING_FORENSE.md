# Briefing Forense — Handoff

**Destinatario:** Perito forense digital designado por Renovación Popular
**Emisor:** Equipo técnico auditoría EG2026
**Fecha:** 2026-04-17
**Clasificación:** Confidencial — uso del cliente

---

## 1. Objetivo del handoff

Transferir al perito forense el estado actual de la auditoría técnico-estadística del escrutinio, con:

- Evidencia con cadena de custodia (hashes SHA-256).
- Hallazgos verificados y proyecciones contrafactuales.
- Preguntas abiertas que requieren herramientas forenses (OCR, análisis de tráfico, etc.) que nuestro equipo no puede ejecutar.

---

## 2. Estado al corte 2026-04-17 08:41 UTC

| Indicador | Valor |
|---|---|
| Escrutinio oficial ONPE | ~93.12% |
| Margen Sánchez − RLA | +5,392 (era +5,898 en corte 92.91%) |
| Actas impugnadas (JEE) | 5,554 (5.99%) |
| Actas pendientes | 780 |
| Solicitudes de nulidad | 98 |
| Runoff programado | 2026-06-07 |

**Tendencia:** margen cayendo (30k → 7k → 5.4k). RLA recortando.

---

## 3. Evidencia entregada (todo en el repo)

### 3.1 Capturas con hash SHA-256

```
captures/20260417T062711Z/   (primera captura, MANIFEST firmado)
captures/20260417T084114Z/   (segunda captura, idéntica — proxy cacheado)
```

Verificación: `py src/capture/verify_manifest.py captures/<timestamp>/`

### 3.2 Datasets procesados

```
data/processed/regiones.csv    (26 regiones × 16 columnas)
data/processed/tracking.csv    (116 cortes temporales)
data/processed/meta.json       (metadata del corte)
```

### 3.3 Análisis ejecutado

```
reports/findings.json               (hallazgos en formato JSON)
reports/summary.txt                 (resumen técnico)
reports/Informe_Tecnico_RP_v2.pdf   (informe ejecutivo — LEER PRIMERO)
reports/figures/fig1..3_*.png       (figuras)
```

### 3.4 Scripts reproducibles

```
src/capture/fetch_onpe.py        Captura atómica
src/capture/verify_manifest.py   Verificación SHA-256
src/process/build_dataset.py     Construcción del dataset
src/analysis/run_all.py          Pipeline de análisis
scripts/capture_loop.py          Bucle continuo de captura
scripts/build_pdf.py             Generador del informe
scripts/docx_to_txt.py           Extractor de texto del Word
```

---

## 4. Hallazgos clave (prioridad para el forense)

### [CRÍTICO] Margen Sánchez−RLA es 195× menor que votos en disputa
- Proyección contrafactual nacional: +6,336 Sánchez
- Proyección contrafactual regional: +188 Sánchez (virtual empate)
- **Palanca**: Lima (+50,362) + Extranjero (+23,201) + Callao (+3,210) = ~77k votos si se defienden bien
- **Riesgo**: Cusco (275 pendientes) + Cajamarca + Huánuco = ~32k más a Sánchez si entran primero

### [MEDIA] Extranjero: 24.11% impugnación (z=+3.66, 4× el nacional)
- RLA ganó 25.96% en Extranjero, Sánchez 2.50%
- 613 actas impugnadas + 191 pendientes (804 en disputa)
- **Pregunta forense**: ¿patrón por oficina consular? ¿qué ODPE?

### [MEDIA] Asimetría Lima+Callao vs resto
- Lima+Callao 4.13% impugnación, resto 6.94% (z=−17.17)
- **No perjudica a RLA** — aclarar al cliente

### [INFO] Serie temporal sin saltos anómalos >0.5pp
- 116 cortes, ningún delta sospechoso
- 72 artefactos de caché del proxy (NO de ONPE)

### [INFO] Benford conforme (p=0.168)
- Limitación conocida en datos electorales (Deckert et al. 2011)

---

## 5. Preguntas abiertas que requieren capacidades forenses

El equipo estadístico NO puede responder sin herramientas específicas. Son los deliverables esperados del perito:

### 5.1 OCR acta por acta
- Bajar los PDF de actas digitalizadas desde el módulo ONPE (cuando esté abierto).
- OCR + extracción de campos: votos por candidato, firmas, observaciones del presidente de mesa.
- Cotejo contra los totales publicados por ONPE.
- **Producto**: lista de mesas con divergencia copia personero vs versión publicada.

### 5.2 Análisis de tráfico de red ONPE
- Captura de paquetes HTTP(S) hacia `resultadoelectoral.onpe.gob.pe/presentacion-backend`.
- Identificar el endpoint real de tracking (la SPA lo consume client-side; nuestro proxy está cacheado).
- Frecuencia de actualización, patrones de entrega de datos.
- **Producto**: documentar si hay "ventanas de silencio" en la entrega de datos.

### 5.3 Análisis de velocidad temporal (hipótesis Apolo 55)
- Ya corrimos el análisis: cruce Sánchez>RLA en 89.509% (2026-04-15 10:31 UTC).
- Drop de velocidad Sánchez −21% post-cruce (**no −62% como circula en redes**).
- t-test: p=0.079 (NO significativo al 5%).
- **Pregunta forense**: ¿hay firmas de software throttling en los timestamps internos de ONPE? Requiere logs que no tenemos.

### 5.4 Fallos del STAE en Cusco (testimonial)
- Se reportan 3-5 reintentos para ingresar actas en Cusco.
- **Recoger**: planilla testimonial estándar (operador, ODPE, hora, mesa, screenshot error).
- **Determinar**: ¿es bloqueo selectivo por mesa (pro-RLA) o general (afecta a todos)?
- **Acción inmediata**: formato normalizado para personeros (ver §6).

### 5.5 98 solicitudes de nulidad
- Solicitar al JEE el desagregado: ¿quién las presenta? ¿contra qué mesas?
- Cruzar con regiones P0 (Lima + Extranjero).
- **Producto**: inventario de nulidades adversas que RLA debe contrarrestar.

---

## 6. Formato de testimonio STAE (para personeros)

| Campo | Ejemplo |
|---|---|
| ODPE | Cusco - Wanchaq |
| Mesa | 03-1234-A |
| Operador (nombre, DNI) | Juan Pérez, 12345678 |
| Fecha/hora del intento | 2026-04-14 15:23 UTC-5 |
| Error mostrado | "Error conexión: timeout en validación" |
| N° de reintentos | 4 |
| Candidato que lidera la mesa | RLA (según copia personero) |
| Screenshot adjunto | sí/no |
| Firma personero | [nombre, DNI, firma, huella] |

**Cadena de custodia:** cada testimonio debe entregarse al equipo legal en sobre sellado con numeración correlativa.

---

## 7. Accesos y credenciales

| Recurso | URL / ubicación | Estado |
|---|---|---|
| Backend ONPE oficial | resultadoelectoral.onpe.gob.pe/presentacion-backend | Retorna HTML (SPA Angular) |
| Proxy CORS | onpe-proxy.renzonunez-af.workers.dev | **Cacheado** — contactar owner |
| Módulo descarga masiva actas OP | Pendiente habilitación ONPE | **BLOQUEANTE para OCR** |
| Repo del proyecto | `C:\Users\jaaguilar\Documents\elecciones2026\auditoria-eg2026` | Git local |

---

## 8. Pendientes de acción (orden de prioridad)

1. **Hoy**: acreditar al perito ante JNE como personero técnico de RP. Sin eso, no entra a audiencias JEE.
2. **Hoy**: firmar NDA entre perito y cliente.
3. **Hoy**: designar personeros en JEE Lima Centro (Extranjero) + JEE Lima Metropolitana. 3 equipos mínimo.
4. **Mañana AM**: reunión de handoff (60 min). Walk-through de este briefing.
5. **Mañana AM**: activar `capture_loop.py` en máquina 24/7.
6. **Mañana PM**: primera tanda de testimonios STAE con formato normalizado.
7. **+48h**: gestionar habilitación del módulo de descarga masiva ante ONPE. Sin eso, no hay OCR.

---

## 9. Contacto

Dejar rellenar:

- Jefe de equipo técnico estadístico: _____________________
- Jefe de seguridad: _____________________
- Vocero técnico único: _____________________
- Perito forense designado: _____________________
- Representante legal cliente: _____________________
