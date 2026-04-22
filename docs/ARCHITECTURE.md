# ARCHITECTURE — auditoria-eg2026

> Scope, boundaries, principios arquitectónicos. Este documento es referencia; `CLAUDE.md` solo apunta aquí.

## Principio

**CLAUDE.md no crece con scope.** Cada dominio = su doc en `docs/`. Agentes leen on-demand.

## Scope (multi-elección)

EG2026 Perú publica 5 votaciones simultáneas. Este proyecto cubre progresivamente:

| Elección | Status | Universo | Spec |
|---|---|---|---|
| Presidencial | ✅ Blindado (H1-H12) | 92,766 mesas | `docs/specs/H*.md` |
| Senadores | 🟡 Planeado | ~92,766 | `docs/specs/S*.md` |
| Diputados | 🟡 Planeado | ~92,766 | `docs/specs/D*.md` |
| Parlamento Andino | ⚪ Backlog | — | — |
| Referéndum | ⚪ Backlog | — | — |

Contrato técnico por elección en `docs/ELECCIONES.md`.

## Boundaries (qué SÍ / qué NO)

**SÍ:**
- Verificación estadística reproducible vs proceso limpio
- Cadena custodia SHA-256 → GitHub → HuggingFace → IPFS
- Tests peer-reviewed del paper registry
- Publicación transparente con limitaciones

**NO:**
- Declarar "fraude" o "trampa" (no autoridad legal)
- Métodos prohibidos (Benford-1, Beber-Scacco)
- Análisis sin spec SDD previa
- Datos privados (solo APIs públicas ONPE)

## Pipeline forense (4 agentes)

```
[human spec H<N>.md]
       ↓
data-forensic (Haiku) → raw_finding.json
       ↓
stats-expert (Sonnet) → stat_finding.json
       ↓
forensic-challenger (Sonnet) → challenge.md  ← red-team
       ↓ (si SOBREVIVE)
audit-narrator (Sonnet) → 3 narrativas
       ↓
human aprueba → sync + IPFS pin
```

Slash command `/publish H<N>` ejecuta todo.

## Worktrees — estrategia multi-elección

```
main (presidencial estable)
├── worktree/senadores          → feat/senadores
├── worktree/diputados          → feat/diputados
└── worktree/h<N>-exploratorio  → feat/h<N>
```

**Reglas:**
- 1 worktree = 1 elección o 1 finding grande
- `captures/` read-only desde worktree (symlink)
- Merge a main solo con: spec completa + 4 agentes + challenger SOBREVIVE + evals pass
- Sincronizar `docs/HALLAZGOS_VIGENTES.md` al merge

## Framework Neuracode (composición)

| Pieza | Origen |
|---|---|
| Claude Code + subagents + hooks | Anthropic (producto) |
| CLAUDE.md hierarchy | Convención oficial |
| SDD 4-step | Patrón propio (inspirado GitHub Spec-Kit) |
| Paper registry cerrado | Original — moat |
| Pipeline 3+1 agentes forense | Original — moat |
| Cadena custodia 4 niveles | Original — moat |
| Cavernícola-Musk style | Personal Jack |
| RTK token optimization | Rust Token Killer |

## Capas testing

| Capa | Tool | Cobertura |
|---|---|---|
| Código Python | pytest | `tests/` — integridad dataset |
| Findings regression | pytest | `evals/` — drift prompts |
| Cadena custodia | verify_manifest.py | SHA-256 |
| Web visual | Playwright | `reports/qa_visual_*/` |
| Hooks | manual test | validar bloqueos |

## Stack multi-repo (monorepo)

```
Python  src/ scripts/ tests/ evals/      → pytest + ruff
JS/TS   proxy/onpe-proxy-neuracode/      → CF Worker
HTML    web/                             → gh-pages
TS      reports/qa_visual_*/             → Playwright
```

## Invariantes no-negociables

1. Universo = **92,766 mesas**.
2. DB autoritativa = `reports/hallazgos_20260420/eg2026.duckdb`.
3. Probabilidades <1e-15 → `binom.logsf`.
4. Solo papers del registry cerrado.
5. Sin código forense sin spec.
6. Captures inmutables.

Cualquier violación → hook bloquea o challenger rechaza.

## Pointers

- `docs/ELECCIONES.md` — contrato multi-elección
- `docs/METHODOLOGY.md` — tests permitidos
- `docs/CHAIN_OF_CUSTODY.md` — cadena custodia
- `docs/specs/SDD.md` — flujo spec-first
- `.claude/rules/` — guardrails agentes
