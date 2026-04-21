# Spec-First — SDD obligatorio

> Ningún finding publicado sin spec. Ninguna feature forense sin diseño previo.

## Regla

**Código/análisis nuevo → spec primero** en `docs/specs/H<N>.md` (finding) o `docs/specs/FEAT-<slug>.md` (infra).

Excepciones (NO requieren spec):
- Bug fix <10 líneas
- Cleanup/refactor sin cambio de comportamiento
- Exploración libre antes de definir pregunta

## Flujo 4 pasos

```
1. humano        → docs/specs/H<N>.md          (H0, H1, método, anti-ataque)
2. data-forensic → reports/raw_findings/raw_h<N>_<ts>.json
3. stats-expert  → reports/stat_findings/stat_h<N>_<ts>.json
4. challenger    → reports/challenges/H<N>_<ts>.md  (intenta refutar)
5. audit-narrator → reports/narratives/HALL-*/H<N>/{technical,scientific,citizen}.md
6. humano aprueba → sync + IPFS pin
```

## Spec obligatoria contiene

- H0 y H1 numéricos
- Dato esperado (métrica + universo + filtros)
- Método del paper registry
- Umbral publicable
- ≥2 limitaciones previsibles
- ≥2 anti-ataques con respuesta
- Criterio publicación (checklist)

Usar `docs/specs/_TEMPLATE.md` como base. Ejemplo completo: `docs/specs/H12.md`.

## Si resultado contradice spec

NO ajustar resultado. Actualizar spec + anotar "iteración N". La spec es contrato.

## Agente verificador

`forensic-challenger` debe rechazar finding si:
- No existe `docs/specs/H<N>.md` correspondiente
- Spec no declara limitaciones
- Spec no cita paper del registry
- raw/stat JSON no coinciden con spec

## Métricas de cumplimiento

Todo finding en `HALLAZGOS_VIGENTES.md` tiene fila con link a su spec. Si la spec no existe → finding no publicable.
