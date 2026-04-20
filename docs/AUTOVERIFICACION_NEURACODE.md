# Auto-verificación Neuracode — 2026-04-19

Captura referencia: `20260420T000714Z` (presidencial/totales con data nacional completa)
Walker referencia: `20260419T035056Z` (88,063 mesas — base de findings_gap)
Walker nuevo: `20260420T003627Z` (87,903 archivos — captura paralela, sin re-análisis)

---

| # | Claim | Valor publicado | Valor actual | Status | Nota |
|---|---|---|---|---|---|
| 1 | Gap mesas API | 4,703 | 4,703 | **PASS** | findings_gap.json GAP-F2; captura 035056Z |
| 2 | Margen Sánchez−RLA | 13,624 votos | 13,620 votos | **PASS\*** | Δ=4 votos; captura 000714Z presidencial.json |
| 3 | r=0.506 p=0.008 corr. imp−RLA | r=0.506, p=0.0083 | r=0.506, p=0.0083 | **PASS** | impugnation_bias.json sin cambio |
| 4 | P(RLA supera)=26.9% | 26.9% central | 26.87% central | **PASS** | forecast.json escenario central |
| 5 | Proyección 13,624→5,883 | 5,883 votos | 5,883 votos | **PASS** | impugnation_bias.json margen_proyectado_100pct |
| 6 | 211 mesas CALAG + 63,300 electores | 211 / 63,300 | Solo en docs | **STALE** | Sin CSV/JSON oficial trazable; solo MEMORIAL + JNE oral |
| 7 | Walker cambia 2° puesto (RLA>JPP) | RLA #2 mesa-a-mesa | RLA #2 (1,863,643 vs JPP 1,656,517) | **PASS** | findings_gap.json GAP-F1-RANKING |
| 8 | SHA-256 web/data.json vigente | Client-side calc | data.json ts=2026-04-17; captura base=20260418T | **STALE** | data.json no se regeneró con captura 20260420T |

---

## Detalle por claim

### 1. Gap 4,703 mesas
- Fuente: `reports/findings_gap.json` GAP-F2-MESAS-FALTANTES
- Walker 20260419T035056Z obtuvo 88,063 mesas; oficial totalActas=92,766
- Delta universo: 92,766 − 88,063 = **4,703** ✓
- Walker nuevo 20260420T003627Z: 87,903 archivos → gap=4,863 (captura incompleta, no re-analizar)
- Veredicto: **PASS** — número publicado basado en captura 035056Z es correcto

### 2. Margen Sánchez−RLA = 13,624 votos
- Fuente: `data/processed/meta.json` campo `margen_sanch_rla_votos`
- Captura 20260420T000714Z presidencial.json: Sánchez=1,893,319 | RLA=1,879,699
- Margen calculado: **13,620** (Δ=4 vs publicado 13,624)
- Meta.json y web/data.json usan captura 20260418T203307Z: Sánchez=1,891,836 | RLA=1,878,212 → 13,624
- Veredicto: **PASS*** — Δ=4 votos por captura más reciente (+0.03%); claim válido con su timestamp

### 3. r=0.506 p=0.008 correlación impugnación−share RLA
- Fuente: `reports/impugnation_bias.json`
- Pearson r=0.5061, p=0.00834 ✓
- Spearman r=0.142, p=0.489 (NO significativo) — debe publicarse junto
- CI95 bootstrap incluye 0 (−0.32, +0.87) — debe publicarse junto
- Veredicto: **PASS** — valores exactos confirmados; caveats vigentes

### 4. P(RLA supera) = 26.9%
- Fuente: `reports/forecast.json` escenario central
- p_rla_supera_sanchez=0.2687 = **26.87%** ✓ (≈26.9% redondeado)
- n=10,000 simulaciones, seed=20260417+2
- Veredicto: **PASS** — reproducible, sin captura nueva requerida

### 5. Proyección 13,624 → 5,883 votos
- Fuente: `reports/impugnation_bias.json` campo `margen_proyectado_100pct`
- Fórmula: margen_actual(13,624) − neto_rla_menos_sanchez(7,740) = **5,883** ✓
- Asume integración 100% actas impugnadas al ratio regional actual
- Nota: no incluye incertidumbre JEE; escenario determinístico
- `web/historia/index.html` scene 6 muestra exactamente "13.624 → 5.883 votos" ✓
- Veredicto: **PASS**

### 6. 211 mesas CALAG + 63,300 electores
- Fuente citada: `docs/MEMORIAL_TECNICO_FISCAL.md` + JNE Congreso 17-apr-2026
- No existe CSV/JSON con listado de las 211 mesas
- Fuente primaria: declaración oral JNE ante Congreso + comunicado CALAG (no capturado en repo)
- `evidence/` contiene solo README.md
- Veredicto: **STALE** — claim trazable a fuente pública oficial (JNE/Congreso) pero sin archivo digitalizado en repo; riesgo de impugnación por falta de evidencia estructurada

### 7. Suma mesa-a-mesa cambia 2° puesto
- Fuente: `reports/findings_gap.json` GAP-F1-RANKING
- Oficial: JPP #2 (1,891,906) | RLA #3 (1,878,493)
- Mesa-a-mesa: RLA #2 (1,863,643) | JPP #4 (1,656,517)
- Delta JPP: −235,389 votos en mesa-a-mesa (ratio_desfase 3.46× vs pct oficial) ✓
- Veredicto: **PASS** — hallazgo estructural confirmado

### 8. SHA-256 web/data.json
- `web/index.html` calcula hash client-side sobre `data.json`
- `web/data.json` meta.generated_at=2026-04-19T22:36:20Z pero state.ts=2026-04-17T10:00Z
- data.json basado en captura 20260418T203307Z (state contiene margen=13,624 de esa captura)
- Captura más nueva (20260420T000714Z) no está integrada en data.json
- Veredicto: **STALE** — hash es reproducible y correcto para la data que contiene, pero data.json no refleja capturas 20260420T; actualizar con `py make.py build`

---

## Resumen ejecutivo

| Status | Claims |
|---|---|
| PASS | #1, #2\*, #3, #4, #5, #7 |
| STALE | #6 (sin evidencia estructurada), #8 (data.json desactualizado) |
| FAIL | ninguno |

**Sin FAIL.** Dos STALE accionables:
- **#6**: Digitalizar las 211 mesas CALAG en CSV con fuente JNE/Congreso.
- **#8**: `py make.py build` + `py make.py report` para sincronizar data.json con captura 20260420T.

Responsable: Tony Aguilar (jaaguilar@acity.com.pe)
Fecha verificación: 2026-04-19T22:36 UTC
