"""
scripts/perplexity_client.py

Helper mínimo para Perplexity API (web-grounded fact-check).
Usado por expert-synthesizer (validar refutaciones) y publishing-guard (fact-check datos públicos).

Modelos:
  - sonar              → web search + cita (default, económico)
  - sonar-pro          → deeper search, más caro
  - sonar-reasoning    → web + reasoning (chain-of-thought)

Uso CLI:
  py scripts/perplexity_client.py "¿Existe el paper 'Klimek 2012 election fingerprints'?"

Uso como módulo:
  from scripts.perplexity_client import ask
  result = ask("validar: Cohen h = 0.73 es 'efecto grande'?")
  print(result["answer"])
  print(result["citations"])
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_MODEL = "sonar"
TIMEOUT_S = 30


def ask(
    question: str,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    max_tokens: int = 1000,
) -> dict[str, Any]:
    """Pregunta factual con citas web. Retorna answer + citations."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY no seteada. Ver .env.example")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "return_citations": True,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()

    answer = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])
    usage = data.get("usage", {})

    return {
        "answer": answer,
        "citations": citations,
        "model": model,
        "usage": usage,
    }


def fact_check(claim: str) -> dict[str, Any]:
    """Wrapper: evalúa claim binario con evidencia web."""
    system = (
        "Eres fact-checker forense. Evalúa el claim dado. "
        "Responde estructurado: VERDICT (VERDADERO|FALSO|PARCIAL|NO_VERIFICABLE), "
        "luego 2-3 bullets con evidencia citada. Cavernícola: max 5 bullets."
    )
    return ask(claim, system=system)


def validate_paper(citation: str) -> dict[str, Any]:
    """Verifica si un paper citado existe realmente."""
    system = (
        "Eres bibliotecario académico. Dada una citación, "
        "responde: EXISTE|NO_EXISTE|DUDOSO + DOI/link si existe."
    )
    return ask(f"Validar cita: {citation}", system=system)


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: py scripts/perplexity_client.py <pregunta>", file=sys.stderr)
        return 1
    result = ask(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
