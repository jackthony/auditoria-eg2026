"""
scripts/hitl_router.py

Router determinista: decide tier publicación según confidence score.
  score >= 0.90 → AUTO (publica sin aprobación manual)
  score >= 0.70 → PENDING-JACK (PR + badge amarillo)
  score <  0.70 → DRAFT (no publica, queda privado)

También decide si crear PR auto y con qué badge.

Uso:
  py scripts/hitl_router.py <confidence_score.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

TIER_CONFIG: dict[str, dict[str, Any]] = {
    "AUTO": {
        "badge": "autonomo",
        "badge_label": "🤖 AUTÓNOMO",
        "badge_color": "#1e88e5",
        "publish": True,
        "pr_required": True,
        "auto_merge_eligible": False,  # semana 1 siempre manual
        "jack_notify": False,
    },
    "PENDING-JACK": {
        "badge": "pending_jack",
        "badge_label": "⏳ PENDIENTE JACK",
        "badge_color": "#fbc02d",
        "publish": True,
        "pr_required": True,
        "auto_merge_eligible": False,
        "jack_notify": True,
        "jack_message": "FORENSIS detectó anomalía con score medio. Necesita tu verificación.",
    },
    "DRAFT": {
        "badge": "draft",
        "badge_label": "🔍 DRAFT INTERNO",
        "badge_color": "#757575",
        "publish": False,
        "pr_required": False,
        "auto_merge_eligible": False,
        "jack_notify": False,
    },
}


def route(score_json: dict) -> dict:
    tier = score_json.get("tier", "DRAFT")
    cfg = TIER_CONFIG[tier]

    return {
        "finding_id": score_json.get("finding_id"),
        "score": score_json.get("score"),
        "tier": tier,
        "publish": cfg["publish"],
        "pr_required": cfg["pr_required"],
        "auto_merge_eligible": cfg["auto_merge_eligible"],
        "jack_notify": cfg["jack_notify"],
        "badge": {
            "id": cfg["badge"],
            "label": cfg["badge_label"],
            "color": cfg["badge_color"],
        },
        "jack_message": cfg.get("jack_message", ""),
        "branch_name": f"forensis/{score_json.get('finding_id', 'h0')}-{_slug()}",
    }


def _slug() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: py scripts/hitl_router.py <confidence_score.json>", file=sys.stderr)
        return 1

    score_path = Path(sys.argv[1])
    score_json = json.loads(score_path.read_text(encoding="utf-8"))

    decision = route(score_json)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
