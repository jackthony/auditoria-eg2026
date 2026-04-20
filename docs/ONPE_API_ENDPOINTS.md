# ONPE API Endpoints — capturados 2026-04-18 vía DevTools

**Base:** `https://resultadoelectoral.onpe.gob.pe/presentacion-backend/`
**Método:** GET (todos 200 OK, sin autenticación aparente).
**Referer lock:** `strict-origin-when-cross-origin` — probar con User-Agent de navegador real y Referer `https://resultadoelectoral.onpe.gob.pe/`.

## Endpoints conocidos

| # | Path | Uso |
|---|------|-----|
| 1 | `proceso/proceso-electoral-activo` | Metadatos del proceso vigente |
| 2 | `proceso/2/elecciones` | Lista de elecciones del proceso 2 |
| 3 | `resumen-general/totales?idEleccion=10&tipoFiltro=eleccion` | Totales nacionales |
| 4 | `eleccion-presidencial/participantes-ubicacion-geografica-nombre?idEleccion=10&tipoFiltro=eleccion` | Resultados por candidato + ubicación |
| 5 | `mesa/totales?tipoFiltro=eleccion` | **Totales mesa-a-mesa** ← MESA-02 target |
| 6 | `resumen-general/mapa-calor?idEleccion=10&tipoFiltro=total` | Heatmap por ubigeo |

## Observaciones
- `idEleccion=10` = presidencial 2026 2da vuelta (confirmar contra endpoint 2).
- Endpoint 5 (`mesa/totales`) permite reconstruir el universo mesa-a-mesa desde la API pública.
- Verificar: existe paginación (`?page=` / `?limit=`)? Tamaño de respuesta?

## Endpoints mesa-a-mesa (confirmados 2026-04-19 vía DevTools — MESA-04)

### A. Lista actas por distrito
```
GET /presentacion-backend/actas?pagina={P}&tamanio={T}&idAmbitoGeografico=1&idUbigeo={u}
```
- `P` desde 0, `T` recomendado 100 (UI usa 5).
- Response: `{data: {totalRegistros, totalPaginas, content: [{id, codigoMesa, numeroCopia, idEleccion, idUbigeo, estadoActa, ...}]}}`
- `detalle` y `lineaTiempo` vienen `null` aquí → hay que llamar al detalle por id.

### B. Detalle acta (VOTOS POR CANDIDATO) ← **ORO**
```
GET /presentacion-backend/actas/{id}
```
- `id` = 13 dígitos. Estructura observada: `{codigoMesa:6}{?:2}{idUbigeo:4}{idEleccion:2}` (falta validar más casos).
- Response.data incluye: `totalElectoresHabiles`, `totalVotosEmitidos`, `totalVotosValidos`, `porcentajeParticipacionCiudadana`, `estadoActa`, `nombreLocalVotacion`, `ubigeoNivel01/02/03`, y `detalle[]` con:
  - `descripcion` (partido), `nvotos`, `nporcentajeVotosValidos`, `nporcentajeVotosEmitidos`
  - `candidato[]` con `apellidoPaterno`, `apellidoMaterno`, `nombres`, `cdocumentoIdentidad`
  - Incluye filas especiales: `VOTOS NULOS` (ccodigo=81), `VOTOS BLANCOS` (esperado).

### C. Imagen del acta física
```
GET /presentacion-backend/actas/file?id={mongoIdHex24}
```
- Devuelve `{data: "<S3-presigned-URL>"}` con expiración **11 min** (`X-Amz-Expires=660`).
- Fetch directo a S3 después (no pasa por Worker).

### Observaciones
- Una mesa física ≈ 5 actas (distintos `idEleccion`: 10 presidencial, 12/13/14/15 otras).
- `idEleccion=10` filtra sólo presidencial 2026 2da vuelta.
- `numeroCopia` permite copias múltiples del mismo acta.
- 1275 actas / distrito (ej. Magdalena del Mar) → universo nacional gigante pero factible async.

### Allowlist Worker a añadir
```
/presentacion-backend/actas
/presentacion-backend/actas/*   (cualquier id numérico)
```
(`/actas/file` no requiere proxy: S3 firmado no bloquea IP.)

## Siguiente paso (MESA-02)
Probar endpoint 5 con curl autenticado-navegador:
```
curl -H "User-Agent: Mozilla/5.0 ..." \
     -H "Referer: https://resultadoelectoral.onpe.gob.pe/" \
     "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/mesa/totales?tipoFiltro=eleccion" \
     -o captures/{tsUTC}/raw/mesa_totales.json
```
Registrar SHA-256 en MANIFEST.jsonl. Commit inmediato.
