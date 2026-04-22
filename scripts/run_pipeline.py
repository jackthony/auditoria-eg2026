"""
scripts/run_pipeline.py

Runner principal del agente FORENSIS.

Dado un signal.json O finding_id (H<N>), ejecuta el pipeline completo:
  1. data-forensic → raw_finding
  2. stats-expert → stat_finding
  3. forensic-challenger → challenge
  4. confidence_scorer → score + tier
  5. hitl_router → decisión publish
  6. (si publish) narrator-technical + narrator-market paralelo
  7. virality-engine → meta/og/share
  8. publishing-guard → veto final
  9. web-builder → landing HTML
  10. git push branch forensis/H<N>-<ts> + abre PR

Requiere env var ANTHROPIC_API_KEY.

Uso:
  py scripts/run_pipeline.py --signal reports/signals/sig_<ts>.json
  py scripts/run_pipeline.py --finding H4
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Windows cp1252 safety — allow Unicode in stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".claude" / "agents"
AUDIT_LOG = ROOT / "reports" / "audit_log.jsonl"

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # CI no necesita .env

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: pip install anthropic", file=sys.stderr)
    sys.exit(1)


def load_agent_prompt(agent_name: str) -> tuple[str, str]:
    """Devuelve (model, system_prompt_body) parseando frontmatter YAML."""
    path = AGENTS_DIR / f"{agent_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent {agent_name}.md not found")

    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError(f"{agent_name}.md sin frontmatter")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{agent_name}.md frontmatter malformado")

    fm, body = parts[1], parts[2]
    model = "sonnet"
    for line in fm.splitlines():
        if line.strip().startswith("model:"):
            m = line.split(":", 1)[1].strip()
            model = m

    model_map = {
        "haiku": "claude-haiku-4-5-20251001",
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-7",
    }

    return model_map.get(model, "claude-sonnet-4-6"), body.strip()


def call_agent(client: Anthropic, agent_name: str, user_msg: str, max_tokens: int = 8000) -> str:
    """Invoca un agente y devuelve texto respuesta."""
    model, system = load_agent_prompt(agent_name)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return "".join(block.text for block in resp.content if hasattr(block, "text"))


def log(event: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event["ts_utc"] = datetime.now(timezone.utc).isoformat()
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def ts_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_pipeline(finding_id: str, signal_path: Path | None = None) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no configurada")

    client = Anthropic(api_key=api_key)
    ts = ts_slug()
    context: dict[str, Any] = {"finding_id": finding_id, "ts": ts}

    log({"event": "pipeline_start", "finding_id": finding_id, "ts": ts})

    # Stage 1: data-forensic → raw_finding
    log({"event": "stage_start", "stage": "data-forensic", "finding_id": finding_id})
    # Nota: data-forensic ejecuta SQL directo. Aquí delegamos al humano o script,
    # porque Claude no tiene DB access en GitHub Actions. Para MVP:
    # - Si raw_finding ya existe en reports/raw_findings/ para H<N>, reusar.
    # - Si no, skip y notificar humano.
    raw_dir = ROOT / "reports" / "raw_findings"
    raw_candidates = sorted(raw_dir.glob(f"raw_{finding_id.lower()}_*.json"))
    if not raw_candidates:
        log({"event": "pipeline_blocked", "reason": "no raw_finding, ejecutar data-forensic local"})
        return {"status": "blocked", "reason": "no raw_finding, ejecutar data-forensic local"}
    raw_path = raw_candidates[-1]
    context["raw_finding"] = json.loads(raw_path.read_text(encoding="utf-8"))
    log({"event": "stage_done", "stage": "data-forensic", "artifact": str(raw_path.relative_to(ROOT))})

    # Stage 2: stats-expert → stat_finding
    log({"event": "stage_start", "stage": "stats-expert"})
    stat_candidates = sorted((ROOT / "reports" / "stat_findings").glob(f"stat_{finding_id.lower()}_*.json"))
    if not stat_candidates:
        stat_prompt = (
            f"Input raw_finding:\n```json\n{json.dumps(context['raw_finding'], indent=2)}\n```\n\n"
            "Produce el stat_finding JSON siguiendo tu contrato. Paper del registry obligatorio."
        )
        stat_text = call_agent(client, "stats-expert", stat_prompt)
        stat_path = ROOT / "reports" / "stat_findings" / f"stat_{finding_id.lower()}_{ts}.json"
        stat_path.parent.mkdir(parents=True, exist_ok=True)
        stat_path.write_text(stat_text, encoding="utf-8")
    else:
        stat_path = stat_candidates[-1]
    context["stat_finding"] = json.loads(stat_path.read_text(encoding="utf-8"))
    log({"event": "stage_done", "stage": "stats-expert", "artifact": str(stat_path.relative_to(ROOT))})

    # Stage 3: forensic-challenger → challenge.md
    log({"event": "stage_start", "stage": "forensic-challenger"})
    challenger_prompt = (
        f"Stat finding:\n```json\n{json.dumps(context['stat_finding'], indent=2)}\n```\n\n"
        "Ataca los 7 vectores. Output: markdown con VEREDICTO: SOBREVIVE | DEBIL | CAE."
    )
    challenge_md = call_agent(client, "forensic-challenger", challenger_prompt)
    challenge_path = ROOT / "reports" / "challenges" / f"{finding_id}_{ts}.md"
    challenge_path.parent.mkdir(parents=True, exist_ok=True)
    challenge_path.write_text(challenge_md, encoding="utf-8")
    log({"event": "stage_done", "stage": "forensic-challenger", "artifact": str(challenge_path.relative_to(ROOT))})

    # Stage 4: confidence_scorer
    log({"event": "stage_start", "stage": "confidence_scorer"})
    score_proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "confidence_scorer.py"), str(stat_path), str(challenge_path)],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    score_json = json.loads(score_proc.stdout)
    log({"event": "stage_done", "stage": "confidence_scorer", "score": score_json["score"], "tier": score_json["tier"]})

    # Stage 5: hitl_router
    score_path = ROOT / "reports" / "scores" / f"{finding_id}_{ts}.json"
    score_path.parent.mkdir(parents=True, exist_ok=True)
    score_path.write_text(json.dumps(score_json, indent=2), encoding="utf-8")

    router_proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "hitl_router.py"), str(score_path)],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    decision = json.loads(router_proc.stdout)
    log({"event": "stage_done", "stage": "hitl_router", "tier": decision["tier"], "publish": decision["publish"]})

    if not decision["publish"]:
        log({"event": "pipeline_halt", "reason": "tier=DRAFT", "finding_id": finding_id})
        return {"status": "draft_only", "decision": decision}

    # Stage 6: narratives (paralelo conceptual, secuencial en código MVP)
    log({"event": "stage_start", "stage": "narrator-technical"})
    narr_tech_prompt = (
        f"Stat finding:\n```json\n{json.dumps(context['stat_finding'], indent=2)}\n```\n\n"
        f"Challenge:\n{challenge_md}\n\n"
        "Produce tech.md y scientific.md siguiendo tu contrato. Salida formateada con 2 archivos marcados "
        "`## === tech.md ===` y `## === scientific.md ===`."
    )
    narr_tech = call_agent(client, "narrator-technical", narr_tech_prompt)
    narr_dir = ROOT / "reports" / "narratives" / finding_id
    narr_dir.mkdir(parents=True, exist_ok=True)
    _write_split_narrative(narr_dir, narr_tech, ["tech.md", "scientific.md"])

    log({"event": "stage_start", "stage": "narrator-market"})
    narr_mkt_prompt = (
        f"Stat finding:\n```json\n{json.dumps(context['stat_finding'], indent=2)}\n```\n\n"
        f"Challenge:\n{challenge_md}\n\n"
        "Produce mercado.md siguiendo tu contrato. Cero jerga, señora del mercado."
    )
    narr_mkt = call_agent(client, "narrator-market", narr_mkt_prompt)
    (narr_dir / "mercado.md").write_text(narr_mkt, encoding="utf-8")
    log({"event": "stage_done", "stage": "narratives", "path": str(narr_dir.relative_to(ROOT))})

    # Stage 7: virality-engine
    log({"event": "stage_start", "stage": "virality-engine"})
    vir_prompt = (
        f"Stat:\n{json.dumps(context['stat_finding'], indent=2)}\n\n"
        f"Tech narrative:\n{(narr_dir / 'tech.md').read_text(encoding='utf-8')}\n\n"
        f"Market narrative:\n{(narr_dir / 'mercado.md').read_text(encoding='utf-8')}\n\n"
        "Produce meta.json + og.json + share.json como 3 bloques JSON separados por `## === <file>.json ===`."
    )
    vir_out = call_agent(client, "virality-engine", vir_prompt)
    vir_dir = ROOT / "web" / finding_id.lower()
    vir_dir.mkdir(parents=True, exist_ok=True)
    _write_split_json(vir_dir, vir_out, ["meta.json", "og.json", "share.json"])
    log({"event": "stage_done", "stage": "virality-engine"})

    # Stage 8: publishing-guard
    log({"event": "stage_start", "stage": "publishing-guard"})
    guard_prompt = (
        f"Stat:\n{json.dumps(context['stat_finding'], indent=2)}\n\n"
        f"Mercado:\n{(narr_dir / 'mercado.md').read_text(encoding='utf-8')}\n\n"
        f"Meta:\n{(vir_dir / 'meta.json').read_text(encoding='utf-8') if (vir_dir / 'meta.json').exists() else '{}'}\n\n"
        "Ejecuta los 5 chequeos y devuelve verdict JSON."
    )
    guard_out = call_agent(client, "publishing-guard", guard_prompt, max_tokens=2000)
    guard_path = ROOT / "reports" / "guard" / f"{finding_id}_{ts}.json"
    guard_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        guard_json = json.loads(_extract_json_block(guard_out))
        guard_json["_raw_snippet"] = guard_out[:500]
        violations = [v for v in guard_json.get("violations", []) if v.get("check") != "parse"]
    except Exception:
        guard_json = {"verdict": "WARN", "violations": [], "_raw_snippet": guard_out[:500]}
        violations = []
    guard_path.write_text(json.dumps(guard_json, indent=2), encoding="utf-8")
    log({"event": "stage_done", "stage": "publishing-guard", "verdict": guard_json.get("verdict")})

    if guard_json.get("verdict") == "VETOED" and violations:
        log({"event": "pipeline_halt", "reason": "guard_vetoed", "violations": violations})
        return {"status": "vetoed", "violations": violations}
    elif guard_json.get("verdict") != "APPROVED":
        log({"event": "guard_warn", "verdict": guard_json.get("verdict"), "raw": guard_out[:200]})

    # Stage 9: web-builder (landing final)
    log({"event": "stage_start", "stage": "web-builder"})
    _render_landing(finding_id, vir_dir, narr_dir, decision, context["stat_finding"])
    log({"event": "stage_done", "stage": "web-builder", "path": f"web/{finding_id.lower()}/index.html"})

    # Stage 10: git branch + PR
    branch = decision["branch_name"]
    log({"event": "pipeline_complete", "finding_id": finding_id, "branch": branch, "tier": decision["tier"]})

    return {
        "status": "ready_to_commit",
        "branch": branch,
        "finding_id": finding_id,
        "tier": decision["tier"],
        "score": decision["score"],
        "badge": decision["badge"],
    }


def _extract_json_block(text: str) -> str:
    """Extrae primer bloque JSON de texto Claude."""
    import re
    # Busca ```json ... ``` o un { balanceado
    m = re.search(r"```json\s*(.+?)\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    # fallback: busca primer { hasta balanceo
    start = text.find("{")
    if start == -1:
        return "{}"
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return "{}"


def _write_split_narrative(out_dir: Path, text: str, filenames: list[str]) -> None:
    import re
    parts = re.split(r"##\s*===\s*(\S+?)\s*===", text)
    # parts: ["prefix", "file1", "body1", "file2", "body2", ...]
    for i in range(1, len(parts), 2):
        fname = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        target = out_dir / fname
        if fname in filenames:
            target.write_text(body, encoding="utf-8")


def _write_split_json(out_dir: Path, text: str, filenames: list[str]) -> None:
    import re
    parts = re.split(r"##\s*===\s*(\S+?)\s*===", text)
    for i in range(1, len(parts), 2):
        fname = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if fname in filenames:
            # Limpia markdown fences
            body = re.sub(r"^```json\s*", "", body)
            body = re.sub(r"\s*```\s*$", "", body)
            try:
                parsed = json.loads(body)
                (out_dir / fname).write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
            except json.JSONDecodeError:
                (out_dir / fname).write_text(body, encoding="utf-8")


def _extract_observed(stat: dict) -> str:
    """Extrae dato observado del stat_finding."""
    s = stat.get("statistic", {})
    if "phat" in s:
        return f"{s['phat']*100:.2f}% observado"
    if "chi2" in s:
        return f"χ² = {s['chi2']:.1f}"
    return stat.get("id", "N/A")


def _format_pvalue(p) -> str:
    """Formatea p-value para display."""
    if p is None:
        return "N/A"
    if p == 0:
        return "< 1e-300 (underflow)"
    if p < 1e-100:
        return f"{p:.2e}"
    if p < 0.001:
        return f"{p:.2e}"
    return f"{p:.4f}"


def _format_effect(effect: dict) -> str:
    """Formatea effect size."""
    if not effect:
        return "N/A"
    metric = effect.get("metric", "")
    value = effect.get("value", 0)
    mag = effect.get("magnitud", "")
    return f"{metric} = {value:.2f} ({mag})"


def _format_papers(citations: list) -> str:
    """Formatea lista de papers."""
    if not citations:
        return "N/A"
    return "<br>".join(citations[:3])


def _format_limitations(items: list) -> str:
    """Formatea limitaciones como lista HTML."""
    if not items:
        return "<li>Ver stat_finding.json para detalles</li>"
    if isinstance(items, dict):
        items = [f"{k}: {v}" for k, v in items.items()]
    return "".join(f"<li>{item if isinstance(item, str) else item.get('limitacion', str(item))}</li>" for item in items[:5])


def _render_landing(finding_id: str, vir_dir: Path, narr_dir: Path, decision: dict, stat: dict) -> None:
    """Render simple landing desde template."""
    tpl_path = ROOT / "web" / "_tpl" / "finding.html"
    if not tpl_path.exists():
        return
    tpl = tpl_path.read_text(encoding="utf-8")

    meta_path = vir_dir / "meta.json"
    share_path = vir_dir / "share.json"
    mercado_path = narr_dir / "mercado.md"
    tech_path = narr_dir / "tech.md"

    meta = json.loads(_extract_json_block(meta_path.read_text(encoding="utf-8"))) if meta_path.exists() else {}
    share = json.loads(_extract_json_block(share_path.read_text(encoding="utf-8"))) if share_path.exists() else {}
    mercado = mercado_path.read_text(encoding="utf-8") if mercado_path.exists() else ""
    tech = tech_path.read_text(encoding="utf-8") if tech_path.exists() else ""

    badge = decision["badge"]
    headline = meta.get("headlines", ["FORENSIS detectó anomalía"])[meta.get("selected_headline_index", 0)]
    hero = meta.get("hook_hero", "")
    sub = meta.get("subtitle", "")

    def _md_safe(text: str) -> str:
        """Escapa para template literal JS: backticks y ${ """
        import re
        lines = text.splitlines()
        # strip primera línea si es solo el nombre del archivo
        if lines and lines[0].strip().lower().endswith('.md'):
            lines = lines[1:]
        text = "\n".join(lines).strip()
        # strip outer ```markdown ... ``` or ``` ... ``` fences
        text = re.sub(r'^```(?:markdown)?\s*\n', '', text)
        text = re.sub(r'\n```\s*$', '', text)
        # strip internal production notes (## Notas de producción or --- followed by notes)
        text = re.split(r'\n---\s*\n## Notas de producci[oó]n|\n## Notas de producci[oó]n', text, maxsplit=1)[0]
        text = text.strip()
        return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    replacements = {
        "{{FINDING_ID}}": finding_id,
        "{{BADGE_LABEL}}": badge["label"],
        "{{BADGE_COLOR}}": badge["color"],
        "{{HEADLINE}}": headline,
        "{{HERO}}": hero,
        "{{SUBTITLE}}": sub,
        "{{MERCADO_BODY}}": _md_safe(mercado),
        "{{TECH_BODY}}": _md_safe(tech),
        "{{SCORE}}": str(decision["score"]),
        "{{TIER}}": decision["tier"],
        "{{SHARE_X}}": share.get("shares", {}).get("twitter", {}).get("text", ""),
        "{{SHARE_WA}}": share.get("shares", {}).get("whatsapp", {}).get("text", ""),
        "{{SHARE_TG}}": share.get("shares", {}).get("telegram", {}).get("text", ""),
        "{{URL}}": f"https://auditoria.neuracode.dev/{finding_id.lower()}/",
        "{{TS}}": datetime.now(timezone.utc).isoformat(),
        # Sustentación técnica
        "{{SUST_OBSERVED}}": _extract_observed(stat),
        "{{SUST_UNIVERSE}}": stat.get("assumptions_checked", {}).get("n_suficiente", "92,766 mesas"),
        "{{SUST_COMPARISON}}": f"H0: {stat.get('h0', 'N/A')}",
        "{{SUST_TEST}}": stat.get("test", "N/A"),
        "{{SUST_PVALUE}}": _format_pvalue(stat.get("p_value")),
        "{{SUST_EFFECT}}": _format_effect(stat.get("effect_size", {})),
        "{{SUST_PAPER}}": _format_papers(stat.get("method_citation", [])),
        "{{SUST_LIMITATIONS}}": _format_limitations(stat.get("limitaciones", stat.get("anti_ataque", []))),
    }

    out = tpl
    for k, v in replacements.items():
        out = out.replace(k, v)

    out_path = ROOT / "web" / finding_id.lower() / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")

    # Update main index.html with card for this finding
    _update_index_card(finding_id, meta, decision)


def _update_index_card(finding_id: str, meta: dict, decision: dict) -> None:
    """Inserta o actualiza card del finding en web/index.html"""
    import re
    index_path = ROOT / "web" / "index.html"
    if not index_path.exists():
        return

    html = index_path.read_text(encoding="utf-8")
    fid_lower = finding_id.lower()

    # Generar card HTML
    headline = meta.get("headlines", ["Hallazgo"])[0]
    # Extraer número simple del headline o usar score
    hero = meta.get("hook_hero", decision.get("score", ""))
    subtitle = meta.get("subtitle", "")[:120]
    tier = decision.get("tier", "AUTO")
    severity = "crítico" if tier in ("AUTO", "PENDING-JACK") else "medio"

    card_html = f'''    <a class="finding-card" href="{fid_lower}/" role="listitem" aria-label="{finding_id}: {headline[:50]}">
      <div class="fc-tag">{finding_id} · {severity} · live</div>
      <div class="fc-num">{hero}</div>
      <div class="fc-body">{subtitle}</div>
      <div class="fc-arrow">ver análisis →</div>
    </a>'''

    # Buscar si ya existe card para este finding
    pattern = rf'<a class="finding-card" href="{fid_lower}/"[^>]*>.*?</a>'
    if re.search(pattern, html, re.DOTALL):
        # Ya existe, no sobrescribir (preservar ediciones manuales)
        return
    else:
        # Insertar antes del cierre de findings-grid
        html = html.replace('  </div>\n\n  <div class="proof-bar"',
                           f'{card_html}\n  </div>\n\n  <div class="proof-bar"')

    index_path.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signal", type=str, help="path a signal.json")
    parser.add_argument("--finding", type=str, help="finding_id H<N>")
    args = parser.parse_args()

    finding_id = None
    if args.signal:
        sig = json.loads(Path(args.signal).read_text(encoding="utf-8"))
        candidatos = sig.get("findings_candidatos", [])
        if candidatos:
            finding_id = candidatos[0]
    if args.finding:
        finding_id = args.finding

    if not finding_id:
        print("ERROR: requiero --signal o --finding", file=sys.stderr)
        return 1

    result = run_pipeline(finding_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in ("ready_to_commit", "draft_only") else 2


if __name__ == "__main__":
    sys.exit(main())
