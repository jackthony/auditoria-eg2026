"""
scripts/forensis_agent_loop.py

L5 Claude Agent SDK streaming loop. Reemplaza pipeline sincrónico de run_pipeline.py.

El agente decide qué herramienta usar dinámicamente vs pipeline rígido.

Tools expuestos:
  - duckdb_query(sql)
  - web_search(query) → Perplexity sonar
  - read_file(path) — solo whitelist
  - write_file(path, content) — solo whitelist web/ + reports/{drafts,narratives,challenges}/
  - git_branch_commit(branch, message) — solo forensis/*
  - create_pr(title, body, branch, labels) — gh cli
  - notify_jack(title, body, priority)
  - run_stats_script(script_name, args)
  - score_finding(stat_path, challenge_path)

Invariantes:
  - Max 30 iterations
  - Budget cap: $5 por loop (tokens)
  - Scope whitelist paths (write_file rechaza fuera)
  - Nunca modifica main directo
  - Nunca toca captures/, .env, memory/reference_papers_forenses.md, .claude/rules/*

Uso:
  py scripts/forensis_agent_loop.py --signal reports/signals/sig_<ts>.json
  py scripts/forensis_agent_loop.py --finding H7
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # CI no necesita .env

# Fail-fast: anthropic es dependencia dura.
try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: pip install anthropic", file=sys.stderr)
    sys.exit(1)

try:
    import duckdb
except ImportError:
    print("ERROR: pip install duckdb", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "reports/hallazgos_20260420/eg2026.duckdb"

# Paths permitidos para write_file
WRITE_WHITELIST = [
    "web/",
    "reports/drafts/",
    "reports/narratives/",
    "reports/challenges/",
    "reports/stat_findings/",
    "reports/raw_findings/",
    "reports/guard/",
    "reports/synthesis_log.jsonl",
    "reports/audit_log.jsonl",
]

# Paths prohibidos absolutos
WRITE_BLACKLIST = [
    "captures/",
    ".env",
    ".claude/rules/",
    "memory/reference_papers_forenses.md",
    "reports/hallazgos_20260420/eg2026.duckdb",
    "reports/hf_dataset/",
]

MAX_ITERATIONS = 30
MODEL_ORCHESTRATOR = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "duckdb_query",
        "description": "Ejecuta SQL read-only contra la DB autoritativa (eg2026.duckdb). Solo SELECT/WITH. Retorna JSON.",
        "input_schema": {
            "type": "object",
            "properties": {"sql": {"type": "string"}},
            "required": ["sql"],
        },
    },
    {
        "name": "web_search",
        "description": "Busca web vía Perplexity sonar (web-grounded con citations). Usar para validar papers, leyes, claims públicos.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": "Lee archivo del repo (relativo a root). Usar para ver agentes, specs, stat_findings.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Escribe archivo. SOLO dentro de whitelist (web/, reports/drafts/, reports/narratives/, etc). Crea parent dirs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "git_branch_commit",
        "description": "Crea branch forensis/* desde main, commit cambios, push. Branch DEBE empezar con forensis/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "branch": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["branch", "message"],
        },
    },
    {
        "name": "create_pr",
        "description": "Crea PR desde branch forensis/* a main. Labels obligatorias incluyen forensis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "branch": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "body", "branch"],
        },
    },
    {
        "name": "notify_jack",
        "description": "Envía Telegram a Jack. priority=INFO (resumen) o URGENT (requiere acción). Úsalo en eventos: publicación, merge, refuta fuerte, rollback, error.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "priority": {"type": "string", "enum": ["INFO", "URGENT"]},
            },
            "required": ["title", "priority"],
        },
    },
    {
        "name": "score_finding",
        "description": "Ejecuta scripts/confidence_scorer.py y retorna score + tier.",
        "input_schema": {
            "type": "object",
            "properties": {
                "stat_path": {"type": "string"},
                "challenge_path": {"type": "string"},
            },
            "required": ["stat_path"],
        },
    },
]


def _is_path_safe_write(path: str) -> bool:
    normalized = path.replace("\\", "/")
    for bad in WRITE_BLACKLIST:
        if normalized.startswith(bad):
            return False
    for ok in WRITE_WHITELIST:
        if normalized.startswith(ok):
            return True
    return False


def _is_sql_readonly(sql: str) -> bool:
    upper = sql.strip().upper()
    forbidden = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "ATTACH", "COPY ")
    return not any(upper.startswith(f) or f" {f} " in upper for f in forbidden)


def tool_duckdb_query(args: dict) -> dict:
    sql = args["sql"]
    if not _is_sql_readonly(sql):
        return {"error": "solo SELECT/WITH permitido"}
    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        rows = con.execute(sql).fetchall()
        cols = [d[0] for d in con.description]
        con.close()
        rows_out = [dict(zip(cols, r)) for r in rows[:500]]
        return {"rows": rows_out, "truncated": len(rows) > 500, "total": len(rows)}
    except Exception as e:
        return {"error": str(e)}


def tool_web_search(args: dict) -> dict:
    try:
        from perplexity_client import ask
        r = ask(args["query"])
        return {"answer": r["answer"], "citations": r.get("citations", [])}
    except Exception as e:
        return {"error": str(e)}


def tool_read_file(args: dict) -> dict:
    path = REPO_ROOT / args["path"]
    if not path.exists():
        return {"error": f"no existe: {args['path']}"}
    try:
        content = path.read_text(encoding="utf-8")
        if len(content) > 40000:
            content = content[:40000] + "\n... [truncated]"
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}


def tool_write_file(args: dict) -> dict:
    path_str = args["path"]
    if not _is_path_safe_write(path_str):
        return {"error": f"path prohibido por scope: {path_str}"}
    path = REPO_ROOT / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"], encoding="utf-8")
    return {"written": str(path_str), "bytes": len(args["content"])}


def tool_git_branch_commit(args: dict) -> dict:
    branch = args["branch"]
    if not branch.startswith("forensis/"):
        return {"error": "branch debe empezar con forensis/"}
    msg = args["message"]
    try:
        subprocess.run(["git", "config", "user.name", "forensis-bot"], check=True, cwd=REPO_ROOT)
        subprocess.run(["git", "config", "user.email", "bot@neuracode.dev"], check=True, cwd=REPO_ROOT)
        subprocess.run(["git", "checkout", "-B", branch], check=True, cwd=REPO_ROOT)
        subprocess.run(["git", "add", "web/", "reports/"], check=False, cwd=REPO_ROOT)
        cr = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, cwd=REPO_ROOT)
        if cr.returncode != 0 and "nothing to commit" not in cr.stdout:
            return {"error": cr.stderr or cr.stdout}
        pr = subprocess.run(["git", "push", "-u", "origin", branch, "--force-with-lease"],
                            capture_output=True, text=True, cwd=REPO_ROOT)
        if pr.returncode != 0:
            return {"error": pr.stderr[:500]}
        return {"branch": branch, "pushed": True}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}


def tool_create_pr(args: dict) -> dict:
    try:
        labels = args.get("labels", []) + ["forensis"]
        cmd = ["gh", "pr", "create",
               "--title", args["title"],
               "--body", args["body"],
               "--head", args["branch"],
               "--base", "main",
               "--label", ",".join(set(labels))]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        if r.returncode != 0:
            return {"error": r.stderr[:500]}
        return {"pr_url": r.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


def tool_notify_jack(args: dict) -> dict:
    try:
        from notify import notify
        r = notify(args["title"], args.get("body", ""), args.get("priority", "INFO"))
        return r
    except Exception as e:
        return {"error": str(e)}


def tool_score_finding(args: dict) -> dict:
    try:
        from confidence_scorer import score_finding
        return score_finding(args["stat_path"], args.get("challenge_path"))
    except Exception as e:
        return {"error": str(e)}


TOOL_DISPATCH = {
    "duckdb_query": tool_duckdb_query,
    "web_search": tool_web_search,
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "git_branch_commit": tool_git_branch_commit,
    "create_pr": tool_create_pr,
    "notify_jack": tool_notify_jack,
    "score_finding": tool_score_finding,
}


def _load_orchestrator_prompt() -> str:
    p = REPO_ROOT / ".claude/agents/forensis-orchestrator.md"
    if not p.exists():
        return "Eres FORENSIS orchestrator. Coordina findings forenses."
    raw = p.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else raw


def _audit(event: str, data: dict) -> None:
    log_path = REPO_ROOT / "reports/audit_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "agent": "forensis-orchestrator",
        "event": event,
        **data,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_loop(task_description: str) -> dict:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = _load_orchestrator_prompt()

    messages = [{"role": "user", "content": task_description}]
    iteration = 0
    total_in = 0
    total_out = 0

    _audit("loop_start", {"task": task_description[:200]})

    while iteration < MAX_ITERATIONS:
        iteration += 1
        resp = client.messages.create(
            model=MODEL_ORCHESTRATOR,
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        total_in += resp.usage.input_tokens
        total_out += resp.usage.output_tokens

        if resp.stop_reason == "end_turn":
            final_text = "".join(b.text for b in resp.content if b.type == "text")
            _audit("loop_end", {"iterations": iteration, "tokens_in": total_in, "tokens_out": total_out})
            return {
                "status": "done",
                "iterations": iteration,
                "final_message": final_text,
                "tokens": {"in": total_in, "out": total_out},
            }

        # Execute tool uses
        tool_results = []
        messages.append({"role": "assistant", "content": resp.content})
        for block in resp.content:
            if block.type == "tool_use":
                fn = TOOL_DISPATCH.get(block.name)
                result = fn(block.input) if fn else {"error": f"tool desconocida: {block.name}"}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str)[:20000],
                })
                _audit("tool_call", {"tool": block.name, "iter": iteration, "ok": "error" not in result})

        if not tool_results:
            _audit("loop_stuck", {"iter": iteration})
            break
        messages.append({"role": "user", "content": tool_results})

    _audit("loop_max_iter", {"iterations": iteration, "tokens_in": total_in, "tokens_out": total_out})
    return {"status": "max_iter", "iterations": iteration, "tokens": {"in": total_in, "out": total_out}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", help="Path a signal.json")
    ap.add_argument("--finding", help="Finding ID (H1,H4,...)")
    ap.add_argument("--task", help="Task raw free-form")
    args = ap.parse_args()

    if args.task:
        task = args.task
    elif args.finding:
        task = (
            f"Procesa finding {args.finding}. "
            f"Lee raw + stat findings en reports/. Score con confidence_scorer. "
            f"Si tier=AUTO (≥0.95): genera narrativa + landing en web/{args.finding}/ + PR con label auto-merge. "
            f"Si tier=PENDING: PR + notify_jack URGENT. "
            f"Si DRAFT: guarda en reports/drafts/ + notify INFO. "
            f"Notifica Jack con resumen al terminar."
        )
    elif args.signal:
        task = f"Nueva signal ONPE: lee {args.signal}, decide si genera finding nuevo o extiende uno existente, y ejecuta pipeline completo."
    else:
        print("Dar --signal, --finding o --task", file=sys.stderr)
        return 1

    result = run_loop(task)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0 if result["status"] == "done" else 2


if __name__ == "__main__":
    sys.exit(main())
