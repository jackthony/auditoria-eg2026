# evals/ — Regression tests findings

Detecta drift si cambias prompts de `data-forensic` o `stats-expert`.

## Estructura

```
golden/
  stat_h{1,2,3,4,9,12}.json   # snapshots 2026-04-21
test_regression.py            # pytest parametrizado
```

## Ejecutar

```bash
py -m pytest evals/test_regression.py -v
```

## Qué valida

| Test | Tolerancia |
|---|---|
| p_value mismo orden magnitud | log10 diff < 1 |
| severity sin cambios | exacto |
| effect_size cercano | diff abs < 0.05 |
| method_citation en registry | papers de `memory/reference_papers_forenses.md` |

## Cuándo re-generar goldens

Solo si:
1. Cambia la data real (re-captura ONPE)
2. Humano aprueba drift explícitamente
3. Spec H<N>.md se actualiza con nueva iteración

```bash
# regenerar golden tras aprobación
cp reports/stat_findings/stat_h4_<ts>.json evals/golden/stat_h4.json
```

Commitear con mensaje `test(evals): regenerate golden H<N>` + razón en body.
