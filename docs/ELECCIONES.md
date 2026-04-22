# ELECCIONES — Contrato multi-elección EG2026

> Schema + endpoints por tipo de elección. Leer antes de capturar / analizar elección ≠ presidencial.

## Tipos ONPE

| Código | Nombre | Schema especial |
|---|---|---|
| `P` | Presidencial | 1 voto por partido/mesa |
| `S` | Senadores | voto partido + preferencial 1 + preferencial 2 |
| `D` | Diputados | voto partido + preferencial 1 + preferencial 2 |
| `PA` | Parlamento Andino | voto partido + preferencial |
| `REF` | Referéndum | SI / NO / blanco / nulo |

## Endpoint base

```
https://resultadoelectoral.onpe.gob.pe/presentacion-backend/
```

Path varía por elección. Verificar en DevTools ONPE web eligiendo tipo:
- Presidencial: `/presidencial/...`
- Congresal: `/congresal/senadores/...` y `/congresal/diputados/...`

**Pendiente:** documentar paths exactos al re-capturar. Ver `docs/ONPE_API_ENDPOINTS.md` (presidencial).

## Universo por elección

Asumir **92,766 mesas** para las 4 principales (mismas mesas físicas). Verificar con boundary probe al capturar.

## Schema parquet — presidencial (actual)

```
codigo_mesa | estado_acta | n_validos | n_blancos | n_nulos |
partido_codigo | partido_nombre | votos | departamento | provincia |
distrito | local_votacion
```

## Schema parquet — congresal (propuesto)

Rompe invariante N×1 → ahora N×(1 partido + 2 preferenciales).

Opción A (wide):
```
codigo_mesa | partido | votos_partido |
voto_pref_1_codigo | voto_pref_1_votos |
voto_pref_2_codigo | voto_pref_2_votos
```

Opción B (long, preferida):
```
codigo_mesa | tipo_voto {PARTIDO|PREF_1|PREF_2} | codigo | votos
```

**Decisión:** Opción B. Más flexible para split-ticket analysis cross-elección.

## Split-ticket analysis (H13+ candidato)

Requiere JOIN por `codigo_mesa`:

```sql
SELECT m.codigo_mesa, p.partido,
       p.votos AS pres_votos,
       d.votos AS dip_votos,
       d.votos - p.votos AS delta
FROM mesa_presidencial p
JOIN mesa_diputados d USING (codigo_mesa, partido)
WHERE p.votos = 0 AND d.votos > 10
```

Anomalía candidata: partido con `pres_votos=0` pero `dip_votos>>0` en misma mesa.

## Captura nueva elección — checklist

- [ ] Endpoint real verificado en DevTools
- [ ] Spec elección en `docs/specs/FEAT-eleccion-<tipo>.md`
- [ ] Worktree nuevo (`git worktree add ../auditoria-eg2026-senadores feat/senadores`)
- [ ] Fetcher parametrizado con `--eleccion {P|S|D|PA|REF}`
- [ ] Walker async respeta rate limits (ONPE bloquea >N req/s)
- [ ] Captures en `captures/{tsUTC}_<eleccion>/`
- [ ] MANIFEST SHA-256 verificado
- [ ] `build_dataset.py` adaptado a schema long
- [ ] DB tabla nueva: `mesa_<eleccion>` en eg2026.duckdb
- [ ] Boundary probe = 92,766 mesas
- [ ] Re-pin HF + IPFS

## Invariantes cross-elección

1. Mismo `codigo_mesa` identifica misma mesa física entre elecciones.
2. `n_validos` puede diferir entre elecciones (votante marca P pero no D).
3. Universo estable = 92,766 mesas.
4. Prefix→depto mapping = ONPE alfabético + Callao=24 (idéntico a presidencial).

## Regla de oro escalamiento

Cada nueva elección arranca con:
1. Spec `docs/specs/FEAT-eleccion-<tipo>.md` (infra)
2. Worktree separado
3. Schema validado antes de correr pipeline forense
4. 1 finding canónico (equivalente H4 multi-elección) antes de ampliar
