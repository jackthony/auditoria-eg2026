# PLAN — Integrar evidencia Prime Institute / APIs filtradas ONPE

**Fecha registro:** 2026-04-18
**Owner:** Jack Aguilar (Tony)
**Estado:** PENDIENTE DE EJECUCION — guardado, no ejecutado.

## Contexto
Prime Institute publico un portal usando APIs oficiales de ONPE que quedaron
accesibles publicamente por error operativo. Urls referencia:

- https://primeinstitute.com/onpe/
- https://primeinstitute.com/onpe/mesas-atipicas.html
- https://primeinstitute.com/onpe/mesas-900k.html

**Dato 2021:** Las mismas APIs estuvieron privadas en 2021, por eso
entonces no se pudo hacer este analisis. Ahora si.

## Preguntas pendientes a ONPE (marco del analisis)
1. Por que la suma mesa-a-mesa da Lopez Aliaga 2do y el total nacional da Sanchez 2do?
2. Donde estan las 4,343 mesas que no figuran en la API?
3. Por que el 44% del desfase va a un candidato con 11% del voto?
4. Por que hay 2,317 pendientes en el sistema pero ONPE reporta 583?

## Observaciones tecnicas iniciales
- La UI de Prime Institute parece construida con Claude (similitud visual).
- Si sus APIs ONPE son accesibles publicamente, podemos jalar la misma data
  directo de `*.onpe.gob.pe` en vez de scrapear su portal. Mas rapido y sin
  intermediario.

## Sub-tickets propuestos (para /ecc:plan)

### MESA-02 — Descubrir endpoints ONPE filtrados
- Auditar red del portal prime (DevTools → Network) para mapear endpoints reales.
- Documentar en `docs/ONPE_API_ENDPOINTS.md` (base URL, query params, rate limit observado).
- **Bloqueo ethical/legal:** confirmar que consumirlos no viola ToS ni implica
  acceso no autorizado. Si la ONPE retira el acceso, registrar timestamp del ultimo jalado.

### MESA-03 — Jalador mesa-a-mesa
- `src/capture/fetch_onpe_mesas.py` — descarga paginada con SHA-256 por respuesta.
- Output: `captures/{tsUTC}/raw/mesas/*.json` inmutable.

### MESA-04 — Reconciliacion mesa vs nacional
- `src/analysis/reconcile_mesa_vs_nacional.py`.
- Suma independiente por candidato y compara con totales publicados.
- Finding: discrepancia, 4,343 mesas faltantes, 44% desfase a candidato minoritario.
- Severidad CRITICO si los numeros se confirman.

### MESA-05 — Dashboard mesa-a-mesa
- Tab nueva "Mesa" con buscador por numero/local/distrito.
- Mapa de mesas 900k (atipicas) y mesas faltantes.
- Integrar con PERITO-01: ZIP pericial incluye dump mesa.

### MESA-06 — Comparar metodologia vs Prime Institute
- No copiar: reproducir independientemente y citar a Prime como referencia cruzada.
- Si los numeros coinciden = dos pipelines independientes llegaron al mismo hallazgo = mas fuerte.
- Si discrepan = investigar por que.

## Restricciones forenses obligatorias
- Cualquier jalado nuevo = carpeta `captures/{ts}/` nueva + MANIFEST.jsonl + commit inmediato.
- **NO borrar** capturas actuales aunque los numeros cambien.
- Citar a Prime Institute en el memorial si replicamos sus hallazgos.
- **No afirmar fraude sin que los numeros cuadren despues de reconciliar.**
  Usar lenguaje: "discrepancia entre suma desagregada y total publicado".

## Ejecucion
Disparar `/ecc:plan` sobre este documento cuando se decida arrancar.
Orden recomendado: MESA-02 → MESA-03 → MESA-04 → MESA-05 → MESA-06.
