"""
scripts/notify.py

Canal de notificaciones a Jack. Primary: Telegram. Fallback: console.

Uso CLI:
  py scripts/notify.py "título" "body" [INFO|URGENT]

Uso módulo:
  from scripts.notify import notify
  notify("finding publicado", "H12 score=0.92", "INFO")
  notify("refutación fuerte", "H9 issue #42", "URGENT")
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import requests

Priority = Literal["INFO", "URGENT"]

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
NOTIFY_LOG = Path("reports/notify_log.jsonl")

EMOJI = {"INFO": "ℹ️", "URGENT": "⚠️"}


def _log(title: str, priority: Priority, sent_telegram: bool, error: str | None = None) -> None:
    NOTIFY_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "priority": priority,
        "sent_telegram": sent_telegram,
        "error": error,
    }
    with NOTIFY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _send_telegram(text: str) -> tuple[bool, str | None]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False, "TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID vacío"

    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return True, None
    except requests.HTTPError as e:
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def notify(title: str, body: str = "", priority: Priority = "INFO", link: str | None = None) -> dict:
    """Envía notificación a Jack. Retorna dict con status."""
    emoji = EMOJI.get(priority, "ℹ️")
    text_parts = [f"{emoji} *{title}*"]
    if body:
        text_parts.append(body)
    if link:
        text_parts.append(f"[Abrir]({link})")
    text_parts.append("\n— FORENSIS")
    text = "\n\n".join(text_parts)

    sent, err = _send_telegram(text)
    _log(title, priority, sent, err)

    if not sent:
        # Fallback: console stderr para que GitHub Actions logs capturen
        print(f"[NOTIFY-FALLBACK {priority}] {title}: {body}", file=sys.stderr)
        if err:
            print(f"  Telegram error: {err}", file=sys.stderr)

    return {"sent_telegram": sent, "error": err, "priority": priority}


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: py scripts/notify.py <título> [body] [INFO|URGENT]", file=sys.stderr)
        return 1
    title = sys.argv[1]
    body = sys.argv[2] if len(sys.argv) > 2 else ""
    priority = sys.argv[3] if len(sys.argv) > 3 else "INFO"
    if priority not in ("INFO", "URGENT"):
        print(f"Priority inválida: {priority}. Usar INFO|URGENT", file=sys.stderr)
        return 2
    result = notify(title, body, priority)  # type: ignore[arg-type]
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["sent_telegram"] else 3


if __name__ == "__main__":
    sys.exit(main())
