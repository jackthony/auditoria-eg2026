# FEAT — FORENSIS autonomous auditor (L3)

**Autor:** Jack Aguilar
**Fecha:** 2026-04-21
**Tipo:** Feature infra (no finding)
**Scope:** `web/` + `reports/{raw,stat,narrative,challenge,feedback}_findings/` + `reports/audit_log.jsonl`

## Problema

Semana viral arranca 2026-04-21. Jack disponible ~10 min/día. Hallazgos bloqueados por bottleneck humano. Sin loop auto → no hay influencer-auditor.

## Objetivo

Auditor IA 24/7 que:
- Detecta cambios ONPE cada 6h
- Ejecuta pipeline forense end-to-end
- Publica landings virales en `web/<finding_id>/`
- Responde comentarios comunidad
- Aprende de refutaciones técnicas
- Jamás publica en `main` sin merge humano

## No-objetivos

- Postear en X/WhatsApp/Telegram (lo hace la comunidad)
- Editar fuera del scope declarado
- Tomar decisiones legales (escala a Jack)
- Reemplazar humano en merge

## Arquitectura

12 agentes en pipeline coordinado por `forensis-orchestrator`:

| # | Agente | Modelo | Rol |
|---|--------|--------|-----|
| 0 | forensis-orchestrator | Sonnet | Coordina + dispatch |
| 1 | sensor | Haiku | Detecta deltas captura |
| 2 | data-forensic | Haiku | SQL → raw_finding.json |
| 3 | stats-expert | Sonnet | Stats + paper → stat_finding.json |
| 4 | forensic-challenger | Sonnet | Red-team adversarial |
| 5 | narrator-technical | Sonnet | tech.md + scientific.md |
| 6 | narrator-market | Haiku | mercado.md (sin jerga) |
| 7 | virality-engine | Sonnet | meta/og/share JSON |
| 8 | web-builder | Opus | Render landing |
| 9 | publishing-guard | Haiku | Veto final |
| 10 | comment-router | Haiku | Clasifica comments Giscus |
| 11 | expert-synthesizer | Sonnet | Refuta técnica → PR spec |

## Flujo

```
[sensor cron 6h] → signal.json
  ↓
[pipeline workflow_dispatch] → data-forensic → stats-expert → challenger
  ↓
[confidence_scorer.py] → score + tier
  ↓
tier == AUTO (≥0.90)?
  ├─ SÍ  → narrator-tech + narrator-market + virality + guard → PR auto
  └─ NO → tier == PENDING-JACK (0.70-0.89)? → PR + issue urgent-jack
          tier == DRAFT (<0.70) → reports/drafts/ (no PR)
  ↓
[Jack merge] → gh-pages auto-deploy
  ↓
[comunidad comenta] → comment-router → auto-reply | expert-synthesizer | jack
```

## Scoring (formula)

```python
score = 0.4 * p_factor + 0.3 * effect_factor + 0.3 * challenger_factor

p_factor        = min(1, -log10(p) / 15)
effect_factor   = min(1, cohen_h / 0.8)
challenger_factor = {SOBREVIVE: 1.0, DÉBIL: 0.5, CAE: 0.0}[verdict]
```

Tier:
- AUTO ≥ 0.90 → publicar directo (Jack revisa después)
- PENDING-JACK 0.70-0.89 → PR + issue urgente
- DRAFT < 0.70 → no se publica, queda en drafts

## Cadena de custodia

- Raw captures intactos (`captures/{ts}/`)
- DB autoritativa: `reports/hallazgos_20260420/eg2026.duckdb`
- SHA-256 de DB en cada stat_finding
- audit_log.jsonl append-only (cada acción + agente + ts)
- Commits firmados por `forensis-bot <bot@neuracode.dev>`
- Branch naming: `forensis/{finding_id}-{ts}`
- Nunca push directo a `main`

## Guardrails

- Scope boundary: agentes rechazan path fuera de whitelist
- Tone-guard: publishing-guard veta "fraude", "🚨", "BREAKING"
- Regla oro: "anomalía que ONPE debe explicar"
- Fact-check: guard compara números narrativa vs stat_finding
- Paper registry: stats-expert solo cita `memory/reference_papers_forenses.md`
- logsf para p <1e-15

## Infra (costo mensual target: $35-65)

- GitHub Actions (captura + pipeline + sensor + comments) — gratis
- gh-pages (web estática) — gratis
- Giscus (comentarios → issues) — gratis
- Cloudflare Worker (proxy ONPE) — gratis
- HuggingFace dataset — gratis
- IPFS Filebase + Pinata — free tier
- Anthropic API — $35-65/mes (Haiku+Sonnet, Opus solo web-builder)

## Invariantes

- No editar `captures/**` ni `MANIFEST.jsonl`
- No escribir `main` sin merge
- No postear redes sociales
- No afirmar "fraude"
- Universo = 92,766 mesas

## Criterio de éxito (semana 1: 2026-04-21 → 2026-04-28)

- [ ] Sensor detecta ≥1 signal real sin intervención Jack
- [ ] Pipeline completa ≥1 finding tier AUTO end-to-end
- [ ] Landing publicado con meta/og/share ok
- [ ] ≥5 comments comunidad clasificados correctamente
- [ ] ≥1 refutación técnica procesada por expert-synthesizer
- [ ] Zero commits en `main` sin merge Jack
- [ ] Zero violaciones tone-guard detectadas

## Archivos

**Agentes** (`.claude/agents/`):
- forensis-orchestrator.md, sensor.md, narrator-technical.md, narrator-market.md, virality-engine.md, publishing-guard.md, comment-router.md, expert-synthesizer.md

**Scripts** (`scripts/`):
- confidence_scorer.py, hitl_router.py, snapshot_diff.py, run_pipeline.py

**Workflows** (`.github/workflows/`):
- sensor.yml (cron 6h)
- pipeline.yml (workflow_dispatch + issue label)
- comment-router.yml (issue_comment)

**Template** (`web/_tpl/`):
- finding.html (placeholders)

## Deployment checklist

Jack ejecuta 1 vez:

1. Secret `ANTHROPIC_API_KEY` en GitHub repo settings
2. Giscus: `data-repo-id` + `data-category-id` en `web/_tpl/finding.html`
3. Test: `gh workflow run forensis-pipeline.yml -f finding=H4`
4. Verificar PR auto-creado en rama `forensis/H4-*`
5. Merge → gh-pages deploy → landing viva

## Roll-back

Si falla:
- Pausar sensor: `gh workflow disable forensis-sensor.yml`
- Revertir commits forensis-bot: `git revert <sha>`
- Retractar landing: borrar `web/<finding_id>/` + commit manual
