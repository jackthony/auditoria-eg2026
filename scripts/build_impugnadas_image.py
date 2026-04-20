"""Genera imagen shareable del finding impugnadas Lima+Exterior — modo ciudadano."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

with open("reports/impugnadas_por_region.csv", encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f) if r["name"]]

rows_sorted = sorted(rows, key=lambda r: float(r["tasa_impugnacion"]), reverse=True)[:10][::-1]

names = [r["name"] for r in rows_sorted]
tasas = [float(r["tasa_impugnacion"]) for r in rows_sorted]
zscores = [float(r["z_score"]) for r in rows_sorted]

fig, ax = plt.subplots(figsize=(12, 7.5), facecolor="#faf7f2")
ax.set_facecolor("#faf7f2")

colors = ["#b0171f" if z > 1.96 else "#888" if z > 0 else "#2d2d2d" for z in zscores]

bars = ax.barh(names, tasas, color=colors, height=0.65, edgecolor="#111", linewidth=1.5)

for bar, tasa, z in zip(bars, tasas, zscores):
    label = f"{tasa:.1f}%"
    if z > 1.96:
        label += f"  (z={z:.1f})"
    ax.text(tasa + 0.3, bar.get_y() + bar.get_height() / 2,
            label, va="center", fontsize=14, fontweight="900",
            fontfamily="serif", color="#111")

ax.axvline(6.21, color="#c99a2e", linestyle="--", linewidth=2, alpha=0.7)
ax.text(6.21, -0.7, "media nacional 6.2%", fontsize=10,
        color="#c99a2e", fontweight="600", ha="center")

ax.set_xlim(0, 32)
ax.set_xlabel("% de actas impugnadas (enviadas al JEE)", fontsize=13, fontfamily="serif", color="#111")
ax.tick_params(axis="y", labelsize=13)
ax.tick_params(axis="x", labelsize=10)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#111")
ax.spines["bottom"].set_color("#111")

title = "Extranjero: 1 de cada 4 actas fue impugnada"
ax.set_title(title, fontsize=26, fontweight="900", fontfamily="serif",
             color="#111", pad=20, loc="left")

subtitle = "26.3% de tasa · z=3.9 · 4.2× la media nacional · Loreto y Ucayali siguen"
fig.text(0.06, 0.87, subtitle, fontsize=11, fontfamily="sans-serif",
         color="#555", style="italic")

fig.text(0.06, 0.04,
         "Fuente: ONPE /presentacion-backend/generales · captura 2026-04-19 · "
         "SHA-256 verificable",
         fontsize=9, color="#666")
fig.text(0.06, 0.015,
         "Análisis: Jack de Neuracode · github.com/jackthony/auditoria-eg2026 · "
         "auditoria.neuracode.dev",
         fontsize=9, color="#b0171f", fontweight="bold")

out = Path("web/og-impugnadas.png")
out.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout(rect=(0, 0.08, 1, 0.86))
plt.savefig(out, dpi=144, facecolor="#faf7f2")
print(f"generated: {out}")
