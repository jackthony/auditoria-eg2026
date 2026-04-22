---
description: Corre challenger adversarial contra un finding ya publicado (re-test de robustez)
argument-hint: H<N>
---

# /refute $ARGUMENTS

Re-examina finding $ARGUMENTS con ataques adversariales. Útil ante:
- Crítica pública nueva
- Cambio de data (re-captura)
- Verificación pre-entrega Fiscalía

## Pasos

1. Leer `docs/specs/$ARGUMENTS.md`
2. Leer último `reports/raw_findings/raw_${ARGUMENTS,,}_*.json`
3. Leer último `reports/stat_findings/stat_${ARGUMENTS,,}_*.json`
4. Invocar `forensic-challenger` con los 3 archivos.
5. Output: `reports/challenges/$ARGUMENTS_<tsUTC>.md`

## Reportar

- Veredicto (SOBREVIVE / DEBIL / CAE)
- Si CAE → acciones correctivas sugeridas
- Si DEBIL → campos de spec a actualizar
- Si SOBREVIVE → ok, no acción
