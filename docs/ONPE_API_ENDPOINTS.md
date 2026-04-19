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
- Endpoint 5 (`mesa/totales`) es probablemente el leak que Prime Institute usó.
- Verificar: existe paginación (`?page=` / `?limit=`)? Tamaño de respuesta?

## Siguiente paso (MESA-02)
Probar endpoint 5 con curl autenticado-navegador:
```
curl -H "User-Agent: Mozilla/5.0 ..." \
     -H "Referer: https://resultadoelectoral.onpe.gob.pe/" \
     "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/mesa/totales?tipoFiltro=eleccion" \
     -o captures/{tsUTC}/raw/mesa_totales.json
```
Registrar SHA-256 en MANIFEST.jsonl. Commit inmediato.
