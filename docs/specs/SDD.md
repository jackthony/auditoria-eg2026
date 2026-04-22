# Spec-Driven Development — auditoria-eg2026

## Principio

Toda pregunta cuantificable nueva (finding candidato, métrica, verificación) arranca como **spec en texto**. Ningún finding se publica sin spec.

## Flujo (4 pasos)

```
1. humano  → docs/specs/<ID>.md       (spec: H0, H1, dato esperado, método)
2. data-forensic → raw_<id>.json       (SQL puro)
3. stats-expert → stat_<id>.json       (test + paper + limitaciones)
4. audit-narrator → narratives/<id>/   (3 formatos)
5. humano aprueba → sync JSONs + IPFS pin
```

## Archivos

- `_TEMPLATE.md` — plantilla, copiar para cada nuevo spec
- `<ID>.md` — un archivo por finding/feature (ej. `H12.md`, `H15.md`)

## Reglas

1. ID = `H<N>` para findings, `FEAT-<slug>` para features no-forenses.
2. Spec escrita ANTES de correr agentes.
3. Si resultado contradice spec → actualizar spec + anotar "iteración".
4. Spec aprobada es contrato: agentes no se salen de ella.
5. Métodos SOLO del paper registry (`memory/reference_papers_forenses.md`).
6. Universo SIEMPRE 92,766 mesas.

## Naming artefactos por spec

```
docs/specs/H<N>.md
reports/raw_findings/raw_h<N>_<ts>.json
reports/stat_findings/stat_h<N>_<ts>.json
reports/narratives/HALL-0420-H<N>/{technical,scientific,citizen}.md
```

## Cuándo NO usar SDD

- Bug fix < 10 líneas de código.
- Cleanup/refactor sin cambio de comportamiento.
- Exploración libre antes de definir pregunta.
