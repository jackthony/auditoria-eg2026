# Storytelling brief — input para `storytelling-pe`

**Fecha:** 2026-04-20 · **Universo:** v2-92k · **Hero finding:** H4

> Este archivo es el input canónico para el agente `storytelling-pe`.
> Reemplaza `reports/findings_prime.json` (viejo) y contexto Prime Institute (stale).
> El agente produce `reports/storytelling_pack.md` con 8 secciones (ver su spec).

---

## 1. Qué producir

Ver `.claude/agents/storytelling-pe.md` §"Estructura de entrega":

1. Hook maestro (1 frase, 12 palabras máx)
2. Pitch 30s TV
3. Hilo X 8-12 tweets
4. Script TikTok/Reel 60s
5. Titulares prensa (3 versiones: sobrio / directo / popular)
6. Pitch panelistas TV
7. 10 componentes Claude Design (prompts GOAL·LAYOUT·CONTENT·AUDIENCE)
8. Flujo aprobación iterativo

**Foco:** H4 es el hero. H1 soporte. H2/H3 bullets secundarios.

---

## 2. Hero finding: H4 (JPP mesas 900k+)

| Métrica | Valor |
|---------|-------|
| JPP en mesas normales (88,063) | 10.91% |
| JPP en mesas especiales 900k+ (4,703) | **41.65%** |
| Ratio | **3.82×** |
| z-stat 2-prop (Newcombe 1998) | 698 |
| p-valor | ≈ 0 |
| Cohen h | 0.73 (efecto grande) |
| Bootstrap IC95 diff | [29.46%, 30.79%] |
| Método | z-test + Cohen h + bootstrap Efron-Tibshirani |

**Metáfora aprobada (1 línea):**
> "En 4,703 mesas especiales (5% del país) un partido sacó 4× más votos que en el resto. Probabilidad por azar: 1 entre billones."

**Fuente datos:** `reports/hallazgos_20260420/findings_consolidado_0420.json` bloque `HALL-0420-H4`.

---

## 3. Findings soporte (secundarios)

**H1 · CRÍTICO · Sesgo geográfico impugnadas**
- Global: 6.16% mesas impugnadas
- Extranjero: 26.27% (z=42) · Loreto: 14.87% · Ucayali: 12.02%
- Piso: Arequipa 1.83%

**H2 · MEDIA · Partidos en locales alta-imp**
- FUERZA POPULAR: +2.07pp · JPP: +0.88pp
- Bajan: BUEN GOBIERNO -1.62pp

**H3 · MEDIA · Outliers nulos/blancos**
- 5,304 mesas (5.72%) outliers
- 4 mesas Loreto 900k+ con >90% blancos (903472-903475)

---

## 4. Cadena de custodia (4 niveles)

| Nivel | Ubicación | Prueba |
|-------|-----------|--------|
| 1 | `captures/20260420T074202Z/` local | MANIFEST.jsonl SHA-256 |
| 2 | GitHub `jackthony/auditoria-eg2026` | Commit `26b4cde`, tag `v2-mesas-900k` |
| 3 | HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` | parquet inmutable |
| 4 | **IPFS Filebase** | 3 CIDs públicos |

**CIDs IPFS (verificables en navegador):**

| Archivo | CID | URL |
|---------|-----|-----|
| MESAS_MANIFEST.jsonl | `QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS` | https://ipfs.filebase.io/ipfs/QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS |
| parquet 3.79M actas | `QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L` | https://ipfs.filebase.io/ipfs/QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L |
| findings H1-H4 | `QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp` | https://ipfs.filebase.io/ipfs/QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp |

**Usar en piezas públicas como sello "imposible de negar".**

---

## 5. Regla de oro (no negociable)

**Jamás decir "fraude". Siempre "anomalía estadística que ONPE debe explicar".**

- Sin regla → hallazgo se descalifica como ataque político
- Con regla → demanda razonable de transparencia forense
- Si una pieza dice "fraude" → cortar y reescribir
- Si una pieza no tiene número con fuente → cortar

---

## 6. Anti-ataque cheat-sheet (H4)

| Ataque predecible | Respuesta (con número) |
|-------------------|------------------------|
| "Es Benford, ya refutado" | No usé Benford. z-test 2-prop, Cohen h, bootstrap. |
| "Eres opositor" | Cero afiliación. Datos públicos ONPE, MIT, replicable vía `rtk pytest`. |
| "Es casualidad" | z=698, IC95 [29.5%, 30.8%]. Probabilidad azar ≈ 0. |
| "Mesas especiales son distintas" | Sí, pero 41.65% vs 10.91% = 31pp. ONPE explica por qué. |
| "Solo un partido se queja" | No me quejo. Pido auditoría. Anomalía no es fraude. |
| "Son militares / extranjero" | Universo 900k+ NO está caracterizado solo como militar. Mesas regulares IE distribuidas geográficamente. |

---

## 7. Restricciones específicas v2-92k

- **Universo:** 92,766 mesas (88,063 normales + 4,703 especiales 900k+)
- **NO usar:** "Prime Institute 4,343", "2,687,621 ≠ 2,595,320", Benford, reconcile mesa-a-mesa refutado
- **SÍ usar:** H1, H2, H3, H4 del `findings_consolidado_0420.json`
- **Stack técnico:** Polars + DuckDB + PyArrow (pandas prohibido)
- **Mapping prefix→depto:** ONPE alfabético con Callao=24 (validado)

---

## 8. Branding

- **Marca:** Neuracode Academy
- **Autor técnico:** Jack Aguilar (Tony) — Agentic AI Builder · Founder Neuracode
- **Redes Jack:** [@JackTonyAC](https://x.com/JackTonyAC) · [LinkedIn](https://www.linkedin.com/in/jackaguilarc/) · TikTok `@jack.de.neura.code`
- **Colores:** `#0a0e1a` (bg), `#ffb800` (amber), `#ef4444` (critical), `#10b981` (verified)
- **Fonts:** JetBrains Mono (data/hash), Inter (body)
- **Firma cierre:** "Metodología open-source · Código reproducible · SHA-256 · neuracode.academy"

---

## 9. Inputs que lee el agente

```
reports/hallazgos_20260420/findings_consolidado_0420.json   # findings autoritativos
reports/ipfs_cids.json                                       # cadena custodia nivel 4
HALLAZGOS_VIGENTES.md                                        # contexto v2-92k
CLAUDE.md                                                    # convenciones proyecto
~/.claude/rules/common/musk-principles.md                    # algoritmo cavernicola
memory/feedback_defensa_h4_publica.md                        # regla oro + anti-ataque
```

---

## 10. Orden de entrega sugerido

1. **Hook maestro** primero. Si no pega en 12 palabras → todo se cae.
2. **Hilo X** (crítico: pone a disposición antes que TV).
3. **Script TikTok 60s** (viralidad).
4. **Titulares prensa** (3 versiones).
5. **Pitch 30s TV** + dossier panelistas.
6. **10 componentes Claude Design** (últimos, son costosos).

Tony aprueba pieza por pieza antes de pasar a la siguiente.

---

**Owner:** Jack Aguilar · **Última actualización:** 2026-04-20T06:30 UTC
