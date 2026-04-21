"""
scripts/briefing.py

Daily briefing 8AM Lima → Telegram Jack.
Resume últimas 24h: findings, comments, merges, refutaciones.

Uso:
  py scripts/briefing.py
"""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from notify import notify

AUDIT_LOG = Path("reports/audit_log.jsonl")
COMMUNITY_LOG = Path("reports/community_log.jsonl")
SYNTHESIS_LOG = Path("reports/synthesis_log.jsonl")
WEB_DIR = Path("web")


def _read_jsonl(path: Path, since: datetime) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("ts_utc") or entry.get("timestamp") or ""
                if ts:
                    entry_ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if entry_ts >= since:
                        out.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue
    return out


def _git_merges_last_24h() -> list[str]:
    """Commits en main de las últimas 24h con autor forensis-bot."""
    try:
        out = subprocess.run(
            ["git", "log", "--since=24 hours ago", "--author=forensis-bot",
             "--pretty=format:%s", "main"],
            capture_output=True, text=True, check=False,
        )
        return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception:
        return []


def _count_findings_published() -> int:
    """Landings en web/ con index.html que no son about/stats/dashboard/index."""
    if not WEB_DIR.exists():
        return 0
    count = 0
    for p in WEB_DIR.glob("*/index.html"):
        if p.parent.name in ("_tpl", "_dev", "about", "stats", "dashboard"):
            continue
        count += 1
    return count


def build_briefing() -> str:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    audit = _read_jsonl(AUDIT_LOG, since)
    community = _read_jsonl(COMMUNITY_LOG, since)
    synthesis = _read_jsonl(SYNTHESIS_LOG, since)
    merges = _git_merges_last_24h()

    comment_types = Counter(c.get("tipo", "?") for c in community)
    refutas_fuertes = sum(1 for s in synthesis if s.get("verdict") == "VÁLIDA_FUERTE")
    refutas_debiles = sum(1 for s in synthesis if s.get("verdict") == "VÁLIDA_DÉBIL")
    findings_total = _count_findings_published()

    agents_actions = Counter(a.get("agent", "?") for a in audit)

    lines = [
        f"*Briefing 24h* ({now.strftime('%Y-%m-%d %H:%M UTC')})",
        "",
        f"📊 Findings total publicados: *{findings_total}*",
        f"🚀 Merges últimas 24h: *{len(merges)}*",
        f"💬 Comments recibidos: *{sum(comment_types.values())}*",
    ]

    if comment_types:
        lines.append("  • " + " · ".join(f"{t}:{n}" for t, n in comment_types.most_common()))

    lines.extend([
        f"🔬 Refutas válidas: *{refutas_fuertes} fuertes + {refutas_debiles} débiles*",
        f"🤖 Acciones agentes: *{sum(agents_actions.values())}*",
    ])

    if agents_actions:
        top_agents = agents_actions.most_common(3)
        lines.append("  • " + " · ".join(f"{a}:{n}" for a, n in top_agents))

    if merges:
        lines.append("")
        lines.append("*Merges:*")
        for m in merges[:5]:
            lines.append(f"  • {m[:80]}")

    lines.extend([
        "",
        "Dashboard: https://auditoria.neuracode.dev/dashboard/",
    ])

    return "\n".join(lines)


def main() -> int:
    body = build_briefing()
    notify("Daily briefing", body, "INFO")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
