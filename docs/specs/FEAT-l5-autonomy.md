# FEAT — FORENSIS L5 full autonomy

**Autor:** Jack Aguilar
**Fecha:** 2026-04-21
**Depende:** `FEAT-autonomous-auditor.md` (L3 base)
**Scope:** todo L3 + auto-merge + self-reflect + reporting a Jack

## Objetivo

Jack = espectador. Agente decide publicar, merge, retract. Jack recibe Telegram diario con resumen. Jack interviene solo si lo pide ajuste.

## No-objetivos

- Reemplazar Jack en decisiones legales/políticas
- Modificar captures/ (intocable)
- Eliminar audit_log

## Diferencias vs L3

| Aspecto | L3 (antes) | L5 (nuevo) |
|---|---|---|
| Tier AUTO ≥0.90 | PR a Jack | Auto-merge directo |
| Tier PENDING-JACK | PR + issue urgente | PR + Telegram Jack |
| Loop | GitHub Actions workflow | Claude Agent SDK streaming |
| Tools agente | Pre-definidos | Dinámicos (tool-use) |
| Reflexión | Ninguna | Weekly self-reflect |
| Rollback | Manual | Auto si 3 refutas válidas 24h |
| Comunicación Jack | GitHub issues | Telegram + briefing diario |

## Arquitectura nueva

```
[sensor cron 6h] → signal
    ↓
[forensis_agent_loop.py] ← Claude Agent SDK streaming
    ├─ tool: duckdb_query
    ├─ tool: web_search (Perplexity)
    ├─ tool: git_commit + push branch
    ├─ tool: create_pr
    └─ tool: notify_jack (Telegram)
    ↓
[confidence_scorer] → score
    ↓
tier=AUTO (≥0.95)?  ──┬── SÍ → auto-merge + notify Jack
                      ├── PENDING (0.70-0.94) → PR + Telegram urgente
                      └── DRAFT → reports/drafts/ + log
    ↓
[rollback-watcher cron 1h]
    - scan issues label=refuta-valida-fuerte
    - ≥3 en 24h → git revert + notify Jack
    ↓
[briefing cron 8AM Lima]
    - summary 24h: findings publicados, merges, comments, deltas
    - Telegram a Jack
    ↓
[self-reflect cron weekly domingo]
    - audit lo que publicó
    - propone edits a .claude/agents/*.md
    - PR a Jack
```

## Reporting a Jack (canales)

### Telegram (primary)

Usando `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` ya en `.env`.

| Evento | Prioridad | Ejemplo mensaje |
|---|---|---|
| Finding publicado (AUTO) | INFO | "✓ H4 publicado. score=0.92. Ver landing." |
| Finding pending | URGENT | "⚠ H7 pending. score=0.78. Revisa PR." |
| Refutación fuerte | URGENT | "⚠ H12 recibió refuta fuerte. Ver issue." |
| Rollback auto | URGENT | "↩ H9 revertido. 3 refutas válidas." |
| Briefing diario 8AM | INFO | "Daily: 2 findings, 15 comments, 1 refuta." |
| Self-reflect weekly | INFO | "Weekly: propongo 3 deltas a specs." |
| Error pipeline | URGENT | "✗ Pipeline falló H<N>. Ver logs." |

### Dashboard (secondary)

`web/dashboard.html` → stats live:
- findings publicados total + week
- comments clasificados (SPAM/PREGUNTA/APORTA/REFUTA)
- tier distribution
- refutaciones válidas vs inválidas
- uptime pipeline

## Self-reflect (weekly)

Domingo 8AM Lima. `scripts/self_reflect.py`:

1. Lee `reports/audit_log.jsonl` última semana
2. Analiza:
   - ¿qué findings tuvieron más refuta-válidas?
   - ¿qué palabras causaron más vetos de guard?
   - ¿qué tipo de comment clasifica peor?
3. Propone delta:
   - editar `.claude/agents/<agente>.md` con lecciones
   - nueva regla en `.claude/rules/`
4. PR a Jack: `forensis/self-reflect-<week>`

## Budget

Sin cambios infra (gratis). Extra API:
- Agent loop streaming: +$15-25/mes
- Self-reflect weekly: +$2/mes
- Briefing daily: +$1/mes
- **Total target: $55-90/mes** (vs $35-65 de L3)

## Criterio de éxito (semana 2: 2026-04-28 → 2026-05-05)

- [ ] ≥1 auto-merge tier AUTO sin intervención Jack
- [ ] ≥1 briefing diario recibido por Jack en Telegram
- [ ] ≥0 rollbacks automáticos (idealmente no necesarios)
- [ ] ≥1 PR self-reflect con delta real
- [ ] Jack interviene <15 min/día

## Kill-switch

Si algo sale mal:
```bash
rtk gh workflow disable forensis-pipeline.yml
rtk gh workflow disable forensis-sensor.yml
rtk gh workflow disable forensis-briefing.yml
```

Telegram envía: "KILL-SWITCH activado por Jack." → agente se detiene.

## Invariantes L5 (no relajables)

- NUNCA auto-merge si score <0.95
- NUNCA auto-merge si guard=VETOED
- NUNCA auto-merge si tone-check falla
- NUNCA editar `main` sin PR (aún en auto-merge, queda PR record)
- NUNCA tocar `captures/**`, `memory/reference_papers_forenses.md`, `.env`
- SIEMPRE Telegram Jack en acciones URGENT
- SIEMPRE log `reports/audit_log.jsonl`

## Archivos nuevos

- `scripts/notify.py` — Telegram helper
- `scripts/forensis_agent_loop.py` — Claude Agent SDK streaming loop
- `scripts/self_reflect.py` — weekly reflection
- `scripts/briefing.py` — daily summary
- `.github/workflows/briefing.yml` — cron 8AM
- `.github/workflows/self-reflect.yml` — cron weekly
- `.github/workflows/rollback-watcher.yml` — cron 1h
- `web/dashboard.html` — live stats
- `.claude/agents/reflection-writer.md` — sidecar agente self-reflect
