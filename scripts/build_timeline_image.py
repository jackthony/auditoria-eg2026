"""Genera imagen shareable del finding timeline — modo ciudadano."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

FINDING = json.load(open("reports/timeline_gap.json", encoding="utf-8"))

low = FINDING["jpp_pct_por_grupo"]["low_gap_lte_p50"]
high = FINDING["jpp_pct_por_grupo"]["high_gap_gt_p95"]
delta = FINDING["jpp_pct_por_grupo"]["delta_pp"]
pval = FINDING["mannwhitney_jpp_pct_low_vs_high"]["p_value"]
n_mesas = FINDING["n_mesas_con_timeline"]

fig, ax = plt.subplots(figsize=(12, 7.5), facecolor="#faf7f2")
ax.set_facecolor("#faf7f2")

categories = ["Mesas RÁPIDAS\n(<3 min)", "Mesas LENTAS\n(>29 min)"]
values = [low, high]
colors = ["#2d2d2d", "#b0171f"]

bars = ax.barh(categories, values, color=colors, height=0.55, edgecolor="#111", linewidth=2)

for bar, val in zip(bars, values):
    ax.text(val + 0.25, bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}%", va="center", fontsize=32, fontweight="900",
            fontfamily="serif", color="#111")

ax.set_xlim(0, 22)
ax.set_xlabel("% votos JUNTOS POR EL PERÚ", fontsize=14, fontfamily="serif", color="#111")
ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=11)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#111")
ax.spines["bottom"].set_color("#111")

title = f"Mesas lentas dieron +{delta:.2f}pp más a JPP"
ax.set_title(title, fontsize=28, fontweight="900", fontfamily="serif",
             color="#111", pad=20, loc="left")

subtitle = (f"n = {n_mesas:,} mesas con timeline · probabilidad de azar: "
            f"1 en {int(1/pval):,} (p={pval:.1e})")
fig.text(0.125, 0.87, subtitle, fontsize=11, fontfamily="sans-serif",
         color="#555", style="italic")

fig.text(0.125, 0.04,
         "Fuente: ONPE /presentacion-backend/actas · lineaTiempo T→C · captura 2026-04-19 · "
         "SHA-256 verificable",
         fontsize=9, color="#666")
fig.text(0.125, 0.015,
         "Análisis: Jack de Neuracode · github.com/jackthony/auditoria-eg2026 · "
         "audit.neuracode.com",
         fontsize=9, color="#b0171f", fontweight="bold")

out = Path("web/og-mesas-lentas.png")
out.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout(rect=(0, 0.08, 1, 0.88))
plt.savefig(out, dpi=144, facecolor="#faf7f2")
print(f"generated: {out}")
