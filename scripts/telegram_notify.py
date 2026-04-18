"""TG-BOT-01 — Notifica cambios relevantes al canal Telegram @AuditoriaEG2026.

Uso:
    py scripts/telegram_notify.py

Requisitos (env vars, NUNCA commit):
    TELEGRAM_BOT_TOKEN  - token de @BotFather
    TELEGRAM_CHAT_ID    - id del canal (ej: @AuditoriaEG2026 o -100xxxxxx)

Reglas de disparo:
    - Margen RLA-Sanchez cambio >= 0.1 pp vs corte anterior.
    - Nuevo finding con severidad CRITICO que no existia en el snapshot previo.

Estado persistente:
    data/processed/telegram_last_state.json  (ultimo margen + ids de findings notificados)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "web" / "data.json"
STATE_JSON = ROOT / "data" / "processed" / "telegram_last_state.json"
MARGIN_THRESHOLD_PP = 0.1  # puntos porcentuales

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_state() -> dict:
    if STATE_JSON.exists():
        return json.loads(STATE_JSON.read_text(encoding="utf-8"))
    return {"last_margin_pp": None, "notified_finding_ids": []}


def save_state(state: dict) -> None:
    STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def send_message(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = resp.status == 200
            if ok:
                logger.info("Telegram OK (%d chars)", len(text))
            return ok
    except Exception as e:
        logger.exception("Telegram fallo: %s", e)
        return False


def compute_margin_pp(state_data: dict) -> float | None:
    """Margen RLA - Sanchez en puntos porcentuales (sobre votos validos)."""
    rla = state_data.get("rla")
    sanch = state_data.get("sanchez")
    if rla is None or sanch is None:
        return None
    return float(rla) - float(sanch)


def _is_critical(sev: str) -> bool:
    s = (sev or "").upper()
    # Tolera acentos/encoding: CRITICO / CRITICAL / CR?TICO.
    return "CRIT" in s


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.error("Faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID en el env.")
        return 1

    if not DATA_JSON.exists():
        logger.error("data.json no existe: %s", DATA_JSON)
        return 1

    d = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    state = d.get("state", {})
    findings = d.get("findings", [])
    meta = d.get("meta", {})

    prev = load_state()
    msgs: list[str] = []

    # Regla 1: cambio de margen
    margin = compute_margin_pp(state)
    if margin is not None:
        if prev.get("last_margin_pp") is None:
            logger.info("Primer run, margen base = %.3f pp", margin)
        else:
            delta = margin - prev["last_margin_pp"]
            if abs(delta) >= MARGIN_THRESHOLD_PP:
                sign = "+" if delta >= 0 else ""
                msgs.append(
                    f"*Cambio de margen RLA-Sanchez*\n"
                    f"Anterior: `{prev['last_margin_pp']:.3f} pp`\n"
                    f"Actual:   `{margin:.3f} pp`\n"
                    f"Delta:    `{sign}{delta:.3f} pp`\n"
                    f"[Dashboard](https://jackthony.github.io/auditoria-eg2026/)"
                )

    # Regla 2: nuevos findings CRITICOS
    notified = set(prev.get("notified_finding_ids", []))
    new_critical = [f for f in findings
                    if _is_critical(f.get("severity", ""))
                    and f.get("id") and f["id"] not in notified]
    for f in new_critical:
        msgs.append(
            f"*NUEVO HALLAZGO CRITICO*\n"
            f"ID: `{f.get('id')}`\n"
            f"Test: {f.get('test', 'n/a')}\n"
            f"Interpretacion: {f.get('interpretation', '')[:300]}"
        )

    # Envio
    sent = 0
    for m in msgs:
        if send_message(token, chat_id, m):
            sent += 1

    # Persistencia
    if margin is not None:
        prev["last_margin_pp"] = margin
    if new_critical:
        notified.update(f["id"] for f in new_critical)
        prev["notified_finding_ids"] = sorted(notified)
    save_state(prev)

    logger.info("Enviados %d / %d mensajes (corte %s)",
                sent, len(msgs), meta.get("generated_at", "n/a"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
