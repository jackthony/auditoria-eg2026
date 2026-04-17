# Agenda — Reunión de Handoff con Perito Forense

**Duración:** 60 min
**Participantes:** Perito forense · Jefe técnico estadístico · Representante legal · Jefe seguridad
**Material pre-lectura obligatoria:**
1. `reports/Informe_Tecnico_RP_v2.pdf`
2. `docs/BRIEFING_FORENSE.md`

---

## 0–5 min · Apertura y firma de NDA

- Confirmación de alcance y confidencialidad.
- Firma NDA.
- Presentación del equipo.

## 5–15 min · Estado técnico actual

- Margen actual y tendencia (30k → 5.4k).
- Corte ONPE 93.12%, actas en disputa.
- Demo rápida: `py src/capture/verify_manifest.py captures/20260417T062711Z/`

## 15–30 min · Hallazgos y proyecciones

- Caminar por §3.3 y §3.4 del PDF v2.
- Tabla de priorización geográfica P0/P1/P2.
- Palancas reales (Lima, Extranjero) vs riesgos (Cusco 275 pend).

## 30–45 min · Gaps que el perito debe cerrar

- OCR acta por acta (módulo ONPE pendiente).
- Tráfico de red y endpoints reales (proxy cacheado).
- Testimonios STAE con formato normalizado.
- Desagregado de 98 nulidades.

## 45–55 min · Plan de los próximos 10 días

- Día 1: acreditación JNE como personero técnico.
- Día 1–3: cobertura física JEE Lima + Extranjero.
- Día 3–5: primera tanda OCR.
- Día 5–7: informe técnico complementario con data nueva.
- Día 7–10: presentación ante JEE.

## 55–60 min · Acuerdos y handoff formal

- Confirmación de credenciales y accesos.
- Entrega del repo (pendrive cifrado + hash).
- Próxima reunión: 48h, misma hora.

---

## Anexo — Preguntas control para validar comprensión del perito

1. ¿Cuál es el margen actual Sánchez−RLA?
2. ¿Cuántas actas están en disputa y en qué región se concentran?
3. ¿Por qué la proyección regional es más favorable que la nacional?
4. ¿Qué regiones son P0 y por qué?
5. ¿Qué diferencia hay entre acta observada, impugnada y nulidad?
6. ¿Cuál es el plazo legal JEE para convocar audiencia pública?
7. ¿Cuánto cuesta una solicitud de nulidad?
8. ¿Qué dice el análisis real del "change-point" Apolo 55?

Si no responde con solvencia las 8, **no entra al equipo.**
