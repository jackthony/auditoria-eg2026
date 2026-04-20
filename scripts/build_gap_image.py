"""Genera imagen shareable del finding gap mesas faltantes — modo ciudadano."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

FINDING = next(f for f in json.load(open("reports/findings_gap.json", encoding="utf-8"))["findings"]
               if f["id"] == "GAP-F2-MESAS-FALTANTES")

oficial = FINDING["totalActas_oficial"]
walker = FINDING["mesas_obtenidas_walker"]
gap = FINDING["delta_universo"]
pct = gap / oficial * 100

fig, ax = plt.subplots(figsize=(12, 7.5), facecolor="#faf7f2")
ax.set_facecolor("#faf7f2")

categories = ["Universo OFICIAL\n(ONPE dice)", "API mesa-a-mesa\n(ONPE devuelve)"]
values = [oficial, walker]
colors = ["#2d2d2d", "#b0171f"]

bars = ax.barh(categories, values, color=colors, height=0.55, edgecolor="#111", linewidth=2)

for bar, val in zip(bars, values):
    ax.text(val + 500, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", fontsize=32, fontweight="900",
            fontfamily="serif", color="#111")

ax.set_xlim(0, oficial * 1.15)
ax.set_xlabel("cantidad de mesas", fontsize=14, fontfamily="serif", color="#111")
ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=11)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#111")
ax.spines["bottom"].set_color("#111")

title = f"Faltan {gap:,} mesas en la API pública ONPE"
ax.set_title(title, fontsize=28, fontweight="900", fontfamily="serif",
             color="#111", pad=20, loc="left")

subtitle = (f"{pct:.1f}% del universo oficial no devuelve data mesa-a-mesa · "
            f"no son copias, no son extranjeras")
fig.text(0.125, 0.87, subtitle, fontsize=11, fontfamily="sans-serif",
         color="#555", style="italic")

fig.text(0.125, 0.04,
         "Fuente: ONPE /presentacion-backend/generales · captura 2026-04-19 · "
         "SHA-256 verificable",
         fontsize=9, color="#666")
fig.text(0.125, 0.015,
         "Análisis: Jack de Neuracode · github.com/jackthony/auditoria-eg2026 · "
         "auditoria.neuracode.dev",
         fontsize=9, color="#b0171f", fontweight="bold")

out = Path("web/og-mesas-faltantes.png")
out.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout(rect=(0, 0.08, 1, 0.88))
plt.savefig(out, dpi=144, facecolor="#faf7f2")
print(f"generated: {out}")
