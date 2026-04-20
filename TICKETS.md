# TICKETS — auditoria-eg2026

Estado vivo del backlog. Cada ítem: **ID · descripción · esfuerzo · owner**.
Marcar `[x]` al completar. `/ecc:plan <ID>` para iniciar.

---

## 🔴 Urgente (datos stale — bloquea publicación nueva)

- [x] **AUS-02** · ✓ 2026-04-19. Actualizado ratio 4.64× (margen 13,624) en `MEMORIAL_TECNICO_FISCAL.md`, `EVIDENCIA_CIUDADANA.md`, `dossier-perito/00_RESUMEN_EJECUTIVO.md`, `dossier-perito/02_HALLAZGOS.md`. Notas: `HIPOTESIS_CIENTIFICAS.md` no tenía el ratio; perito zip (Apr 18) congelado — se regenerará post-AUS-01.
- [x] **AUS-01** · ✓ 2026-04-20. `src/analysis/ausentismo.py` completo y wired en `run_all.py`. Regenera `reports/ausentismo_comparacion.json` desde `meta.json` cada corte. Ratio 4.65× auto-calculado.

## 🟠 Sprint 0 — Rebrand editorial Neuracode (bloquea sprints siguientes)

- [ ] **BRAND-01** · Extraer sistema de diseño de `web/chat/` + `web/historia/` a `web/styles/brand.css`. Tokens: Fraunces 700/900 + Caveat + Inter; paleta `--ink #111` / `--paper #faf7f2` / `--blood #b0171f` / `--muted`; branding "Jack de Neuracode @JackDeNeuracode". · 2 h · Tony
- [ ] **BRAND-02** · Rehacer `web/index.html` (949 L monolito AI-looking) heredando `brand.css`. Conservar 4 tabs y funcionalidad (mapa Leaflet, slider diff, slider JEE, findings search, share, hash). Eliminar toggle EN, badge "EN VIVO" pulsante, alertas genéricas. · 6 h · Tony
- [ ] **BRAND-03** · Landing `/` narrativa tipo `historia/` con CTAs a `/dashboard`, `/chat`, `/historia`, memorial PDF. · 2 h · Tony
- [ ] **BRAND-04** · OG image unificada (estilo Fraunces+paper+blood), hero "4.703 mesas no aparecen · 2° puesto cambia". Regenerar `build_og_image.py`. · 1 h · Tony
- [ ] **BRAND-05** · DNS pendiente Tony: en registrar de `neuracode.dev` agregar `CNAME audit → jackthony.github.io` (proxy OFF). Luego repo Settings → Pages → Custom domain `audit.neuracode.dev` + Enforce HTTPS. `web/CNAME` ya commiteado. · 15 min · Tony

## ✅ Sprint 1 — Quick wins (COMPLETO 2026-04-19)

- [x] **MAPA-01** · Leaflet + GeoJSON por margen López Aliaga−Sánchez.
- [x] **LIVE-01** · Auto-refresh + badge EN VIVO + relative time.
- [x] **SHARE-01** · X / WhatsApp / Telegram / Copiar con texto pre-armado.
- [x] **OG-01** · OG image regenerada por `build_og_image.py`.
- [x] **HASH-01** · SHA-256 footer + alert hash completo.
- [x] **FOOT-01** · Footer TikTok/IG/FB/GitHub + Memorial PDF + API pública.

## 🟢 Sprint 2 — Diferenciador técnico (~23 h)

- [x] **TABS-01** · Tabs implementados (Resultado · Hallazgos · Forecast · Verificación).
- [x] **TABLE-01** · Tabla findings con sort por severidad + filtros + búsqueda.
- [x] **DIFF-01** · Slider de corte histórico vs corte actual (diff-slider).
- [x] **FCAST-INT-01** · Slider fcast-slider 20-80% integración JEE en cliente.
- [x] **TG-BOT-01** · `scripts/telegram_notify.py` dispara en Δmargen ≥0.1pp o finding CRÍTICO.
- [x] **API-01** · 7 endpoints en `web/api/` (findings, forecast, state, regions, series, projection, findings_gap).
- [ ] **HIST-01** · Comparador 2026 vs 2021 vs 2016 — tabla en informe, no script nuevo. Ya parcialmente cubierto por `ausentismo.py`.

## 🔵 Sprint 3 — Diferenciación absoluta (~1 semana)

- [x] **MESA-01** · ✓ 2026-04-20. 5,419 impugnadas / 88,063 (6.15% CRÍTICO). Electores en juego: 1,715,680 (ratio 125.9× vs margen). `src/analysis/mesa_impugnadas.py`.
- [x] **MESA-04** · ✓ 2026-04-19. Endpoints confirmados en `docs/ONPE_API_ENDPOINTS.md`.
- [ ] **IPFS-01** · IPFS pinning + hash IPFS junto al SHA-256.
- [ ] **PERITO-01** · ZIP firmado captura + análisis + memorial para Fiscalía.

## ⚫ Post-cierre escrutinio (bloquea firma fiscal)

- [ ] **PDF-01** · Refactor `scripts/build_pdf_v3.py`: 5 hardcoded CRÍTICOS → `findings.json`/`meta.json`/`forecast.json`. Leer `forecast.json` (hoy ignorado). Log ERROR si figura faltante. Disclaimer "estimación" en S/ 216k/72k/40k. `.hexval()` → `colors.toHexString()`. · 4 h · Tony
  - Hardcoded: L495 (Extranjero 24.11%/z=+3.66), L506 (Lima+Callao z=−17.17/4.13%/6.94%), L809 (116 cortes/76.44%/92.91%/72 artefactos), L659-663 (98 mesas/~5,325 votos Infobae), L726-727 (Lima 50,362 + Extranjero 23,201).

## 💭 Sueño (sin fecha)

(Limpiado 2026-04-20 — sin tracción/ROI. DATA-MARKET completado, BRAND-02 duplicado en Sprint 0.)

---

## ✅ Completados

- [x] **DATA-MARKET** · ✓ 2026-04-20. Dataset 3.6M filas en https://huggingface.co/datasets/Neuracode/onpe-eg2026-mesa-a-mesa · parquet 10.6MB · CC-BY-4.0.
- [x] **HALL-0420** · ✓ 2026-04-20. H1 sesgo geográfico, H2 partidos vs imp, H3 outliers nb. DB `eg2026.duckdb` + `findings_consolidado_0420.json`. Mapping prefix→depto ONPE corregido (alfabético + Callao=24).
- [x] **MESA-02** · Reconcile contable cross-endpoint (7 checks, 0 findings). ✓ 2026-04-18 · captura 20260419T025134Z.
- [x] **RESEARCH-01** · Endpoints mesa-a-mesa confirmados. ✓ 2026-04-18 · `/actas/observadas`, `/actas/{id}` con lineaTiempo T/D/C/O/E, `/ubigeos/{dep,prov,dist}`.
- [x] **MESA-03** · Worker allowlist ampliada (actas/observadas, actas/{id}, ubigeos/*). ✓ 2026-04-18 · `proxy/onpe-proxy-neuracode/src/worker.js` L13-20.
