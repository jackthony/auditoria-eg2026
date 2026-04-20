"""Genera imagen shareable del finding ranking (oficial vs mesa-a-mesa)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

FINDING = next(f for f in json.load(open("reports/findings_gap.json", encoding="utf-8"))["findings"]
               if f["id"] == "GAP-F1-RANKING")

ABREV = {
    "FUERZA POPULAR": "FP",
    "JUNTOS POR EL PERU": "JPP",
    "JUNTOS POR EL PERÚ": "JPP",
    "RENOVACION POPULAR": "RP",
    "RENOVACIÓN POPULAR": "RP",
    "PARTIDO DEL BUEN GOBIERNO": "BG",
    "PARTIDO CIVICO OBRAS": "PCO",
    "PARTIDO CÍVICO OBRAS": "PCO",
}

def norm(n): return ABREV.get(n, n[:14])

top_of = FINDING["top10_oficial"][:5]
top_mm = FINDING["top10_mesa_a_mesa"][:5]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 7.5), facecolor="#faf7f2")
for ax in (ax1, ax2):
    ax.set_facecolor("#faf7f2")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#111")
    ax.spines["bottom"].set_color("#111")

def draw(ax, data, title, highlight_jpp):
    names = [norm(r[0]) for r in data][::-1]
    pcts = [r[2] for r in data][::-1]
    colors = ["#b0171f" if "JPP" in n else "#2d2d2d" for n in names]
    bars = ax.barh(names, pcts, color=colors, height=0.6, edgecolor="#111", linewidth=1.5)
    for bar, p in zip(bars, pcts):
        ax.text(p + 0.2, bar.get_y() + bar.get_height()/2,
                f"{p:.2f}%", va="center", fontsize=16, fontweight="900",
                fontfamily="serif", color="#111")
    ax.set_xlim(0, 20)
    ax.set_title(title, fontsize=18, fontweight="900", fontfamily="serif",
                 color="#111", pad=15, loc="left")
    ax.tick_params(axis="y", labelsize=14)
    ax.tick_params(axis="x", labelsize=10)

draw(ax1, top_of, "ONPE dice (agregado)", True)
draw(ax2, top_mm, "Suma mesa-a-mesa", True)

fig.suptitle("JPP pasa de #2 a #4 cuando sumas mesa-a-mesa",
             fontsize=24, fontweight="900", fontfamily="serif",
             color="#111", x=0.06, y=0.96, ha="left")

fig.text(0.06, 0.89,
         "RP sube al #2 · BG sube al #3 · diferencia: 235,389 votos JPP",
         fontsize=11, fontfamily="sans-serif", color="#555", style="italic")

fig.text(0.06, 0.04,
         "Fuente: ONPE /presentacion-backend · captura 2026-04-19 · "
         "SHA-256 verificable",
         fontsize=9, color="#666")
fig.text(0.06, 0.015,
         "Análisis: Jack de Neuracode · github.com/jackthony/auditoria-eg2026 · "
         "auditoria.neuracode.dev",
         fontsize=9, color="#b0171f", fontweight="bold")

out = Path("web/og-ranking-cambia.png")
out.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout(rect=(0.02, 0.08, 0.98, 0.86))
plt.savefig(out, dpi=144, facecolor="#faf7f2")
print(f"generated: {out}")
