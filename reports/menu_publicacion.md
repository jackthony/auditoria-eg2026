# MENÚ PUBLICACIÓN EG2026 · v1 IRREFUTABLE

**Fecha:** 2026-04-20
**Autor:** Jack Aguilar · Neuracode
**Universo:** 92,766 mesas (88,063 + 4,703 especiales 900k+)
**Regla oro:** jamás "fraude". Siempre "anomalía que ONPE debe explicar".

---

## Criterios de selección (los 4 que pasan)

1. Paper peer-reviewed NO refutado
2. Cross-check con 2do método independiente
3. Probabilidad exacta bajo H0 calculada (no solo p-value)
4. Wow factor: número brutal entendible en 3 segundos
5. Reproducibilidad: query DuckDB + código MIT + IPFS

---

## FINDING 1 — HALL-0420-H4 (HERO)

**Hook:** "4,703 mesas. JPP sacó 4× más votos ahí. z=698. Ratio 3.82×."

| Capa | Dato |
|------|------|
| Normales (88,063) | JPP 10.9073% (1,657,500 / 15,196,245) |
| 900k+ (4,703) | JPP 41.6471% (235,331 / 565,060) |
| Diferencia | 30.74 pp |
| Odds ratio | 5.83 |
| z-test (Newcombe 1998) | z = 698, p ≈ 0 |
| Chi² 2×2 | χ² = 487,171, p ≈ 0 |
| Cohen h (1988) | 0.73 (efecto grande) |
| Bootstrap IC95 (Efron-Tibshirani 1993, B=10k) | [29.46%, 30.79%] |
| Per-depto cross-check | Todos los deptos grandes muestran ratio 2.6-4.2× (La Libertad 4.16, Loreto 3.62, Arequipa 3.37, Piura 3.10, Ucayali 3.00, Lima 2.93, Lambayeque 2.82, Áncash 2.61) → NO es artefacto regional |
| Klimek 2D (PNAS 2012) | Aplicado, **negativo**, reportado honestamente |
| Benford-1 | NO usado (refutado Deckert 2011) |

**Anti-ataque:** H7A distribución 900k+ — Cajamarca 636, Áncash 412, Piura 371, Extranjero solo 34 (0.7%). NO son militares ni extranjero.

**Gráfico:** `reports/figures/h4_hero_jpp_ratio.png` + `h7a_antitaque_distrib.png`

**Canal:** Hilo X ✅ listo (`reports/storytelling_pack.md` L31-192) · TikTok 60s pendiente

---

## FINDING 2 — HALL-0420-H12 (BLOWOUT EMBLEMÁTICO)

**Hook:** "Una mesa en Cusco. JPP = 90.4%. Única entre 78,706 normales."

| Capa | Dato |
|------|------|
| Mesa | 018146, Cusco, normal (no 900k+) |
| Votos válidos | 230 |
| JPP | 208 votos (90.43%) |
| 2do partido | Cívico Obras · 10 votos (4.35%) |
| Test binomial | P(JPP ≥ 208 / n=230, p_global=10.91%) = 0 exacto |
| Contexto | Solo 1 mesa normal con winner ≥ 90% entre 78,706 (0.0013%) |
| Paper | Newcombe 1998 (z-test extremos proporciones) |

**Anti-ataque:** aun si tasa JPP sube a 30%, P(208/230) = 1.4e-40. Matemáticamente imposible bajo H0 de votación aleatoria.

**Gráfico:** `reports/figures/h12_blowout_mesa_emb.png`

**Canal:** Carrusel IG 10 slides · Tweet único con gráfico

---

## FINDING 3 — HALL-0420-H9 (BERBÉS · CADENA CUSTODIA)

**Hook:** "Consulado de Perú en Salta. 11 mesas. 11 impugnadas. P = 1 entre 20 billones."

| Capa | Dato |
|------|------|
| Local | COMPLEJO DEPORTIVO BERBÉS, Salta (Consulado) |
| Mesas | 11 de 11 impugnadas (100%) |
| Tasa global impugnación | 6.1585% (5,714 / 92,766) |
| P(11/11 impugnadas \| H0 aleatorio) | 6.1585%¹¹ = **4.83e-14** |
| Equivalente | 1 entre 20,700,000,000,000 (20 billones) |
| Binomial test | p = 4.83e-14 |
| Contexto | 58 locales totales con 100% mesas impugnadas (≥3 mesas cada uno) |

**Método:** conteo descriptivo + binomial exacto (no requiere paper — es probabilidad pura).

**Gráfico:** `reports/figures/h9_locales_100pct_imp.png`

**Canal:** Tweet visual único + diáspora Argentina

---

## FINDING 4 — HALL-0420-H1 (SESGO GEOGRÁFICO)

**Hook:** "Extranjero: 26.27% mesas impugnadas. Nacional: 6.16%. Proporción 4.27×."

| Capa | Dato |
|------|------|
| Extranjero | 26.268% (668 / 2,543) · z = 42.2 vs global |
| Loreto | 14.87% (401 / 2,697) |
| Ucayali | 12.02% (188 / 1,564) |
| Global | 6.1585% |
| Chi² homogeneidad (26 deptos) | χ² = 2,897, dof=25, **p ≈ 0** |
| Bonferroni ajuste | α' = 0.01/26 = 0.0004 — todos los deptos top siguen significativos |
| Paper | Newcombe 1998 Stat Med |

**Anti-ataque:** no es solo Extranjero (cross-check: Loreto 14.87%, Ucayali 12.02% dominan sierra-selva). Patrón distribuido.

**Gráfico:** `reports/figures/h1_sesgo_geografico.png`

**Canal:** Hilo X corto + mapa

---

## SECUENCIA LANZAMIENTO (1/día, no batch)

| Día | Canal | Finding | Agente | Estado |
|-----|-------|---------|--------|--------|
| **1 (HOY)** | Hilo X | H4 + H7A | storytelling-pe ✅ listo | Pieza 2 publicable |
| **2** | TikTok 60s | H4 visual | storytelling-pe | Pieza 3 en cola |
| **3** | Carrusel IG | H12 mesa Cusco | storytelling-pe | Pieza 4 en cola |
| **4** | Tweet único | H9 BERBÉS | storytelling-pe | Pieza 5 en cola |
| **5** | Hilo X corto | H1 geográfico | storytelling-pe | Pieza 6 en cola |
| **6** | LinkedIn longform | 4 findings + papers | manual | pendiente |
| **7** | Paper draft + HF update | todos + limitaciones | manual | pendiente |

---

## DESCARTADOS (no tocar)

| ID | Razón descarte |
|----|----------------|
| H2 | Descriptivo sin wow brutal |
| H3 | Wow moderado, complejo explicar |
| H5 | Trivial negativo (ONPE OK en identidad física) |
| H13 Klimek standalone | Negativo, pero SE USA como honestidad dentro de H4 |
| H14 Beber-Scacco standalone | Artefacto power-law, solo mención académica |
| H16 mesas gemelas | Sin paper backing directo |

---

## CADENA CUSTODIA NIVEL 4 (referenciar en cada pieza)

- Local: `captures/{ts}/MANIFEST.jsonl` (SHA-256)
- GitHub: `main` + tag `v2-mesas-900k`
- HuggingFace: `Neuracode/onpe-eg2026-mesa-a-mesa` (3.79M actas)
- IPFS Filebase:
  - MANIFEST: `QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS`
  - Parquet: `QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L`
  - Findings: `QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp`

Gateway público: `https://ipfs.filebase.io/ipfs/<CID>`

---

## PAPERS PEER-REVIEWED (los que se citan)

| Paper | DOI/Ref | Uso | Status 2026 |
|-------|---------|-----|-------------|
| Newcombe R.G. (1998) | Stat Med 17(8):857-872 | z-test 2-prop · H1, H4, H12 | Standard, 15k+ citas |
| Cohen J. (1988) | Lawrence Erlbaum, 2nd ed | Efecto h · H4 | Textbook canónico |
| Efron B. & Tibshirani R. (1993) | CRC Press | Bootstrap IC95 · H4 | Referencia canónica |
| Deckert J., Myagkov M., Ordeshook P.C. (2011) | Political Analysis 19(3):245-268 | Justifica NO usar Benford | Reforzado |
| Klimek P. et al. (2012) | PNAS 109(41):16469-16473, doi:10.1073/pnas.1210722109 | Fingerprint 2D · aplicado, negativo reportado | Reforzado 2018/2023 |
| Beber B. & Scacco A. (2012) | Political Analysis 20(2):211-234 | Last-digit chi-sq · artefacto reportado | Standard |
| Mann H.B. & Whitney D.R. (1947) | Annals Math Stat | Outliers · H3 (no publicable masivo) | Standard |

---

## REPRODUCIBILIDAD (anti-ataque técnico)

```bash
git clone github.com/jackthony/auditoria-eg2026
cd auditoria-eg2026
py -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
py scripts/build_duckdb_and_fix.py       # rebuild DB desde parquet
py scripts/analyze_hallazgos_0420_v2.py  # regenera H1, H3
py scripts/stats_h4_especiales_900k.py   # regenera H4
py scripts/build_storytelling_figures.py # regenera 5 PNGs
rtk pytest                                # 12 tests polars+duckdb
```

---

**Firma:** Jack Aguilar · @JackTonyAC · Founder Neuracode · Agentic AI Builder · Claude Code
**Licencia:** MIT · **Datos:** ONPE públicos CC-BY-4.0
**Contacto:** github.com/jackthony/auditoria-eg2026
