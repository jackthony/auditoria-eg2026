"""Genera imagen shareable del finding FDR 4 supervivientes — modo ciudadano."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

FDR = json.load(open("reports/fdr_results.json", encoding="utf-8"))

ALIAS = {
    "impugnation.ztest_lima_vs_resto": "Lima vs resto (impugnadas)",
    "impugnation_velocity.mann_whitney_12h": "Velocidad impugnación",
    "impugnation_bias.pearson_tasa_imp_vs_share_rla": "Tasa imp ↔ share candidato",
    "spatial_cluster.share_rla": "Cluster espacial votos",
    "spatial_cluster.tasa_impugnacion": "Cluster espacial impugnadas",
    "spatial_cluster.pct_fuera": "Cluster espacial pendientes",
    "impugnation_bias.pearson_tasa_imp_vs_share_sanchez": "Imp vs share oponente",
    "benford.pool_chi2": "Ley Benford (pooled)",
    "last_digit.Belmont.chi2": "Last digit Belmont",
    "last_digit.López Aliaga (RLA).chi2": "Last digit RLA",
    "last_digit.Fujimori.chi2": "Last digit Fujimori",
    "last_digit.Sánchez.chi2": "Last digit Sánchez",
    "last_digit.Nieto.chi2": "Last digit Nieto",
    "impugnation_bias.spearman_tasa_imp_vs_share_sanchez": "Spearman imp/Sánchez",
    "impugnation_bias.spearman_tasa_imp_vs_share_rla": "Spearman imp/RLA",
    "spatial_cluster.bivariate_rla_impug": "Bivariado RLA/imp",
    "spatial_cluster.share_sanch": "Cluster Sánchez",
}

results = FDR["results"]
names = [ALIAS.get(r["test"], r["test"]) for r in results]
qs = [r["q_value_fdr_bh"] for r in results]
survives = [r["survives"] == "SI" for r in results]

fig, ax = plt.subplots(figsize=(12, 8), facecolor="#faf7f2")
ax.set_facecolor("#faf7f2")

colors = ["#b0171f" if s else "#bbb" for s in survives]

y_pos = list(range(len(names)))
bars = ax.barh(y_pos, qs, color=colors, height=0.65, edgecolor="#111", linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=10)
ax.invert_yaxis()

ax.axvline(0.05, color="#c99a2e", linestyle="--", linewidth=2, alpha=0.8)
ax.text(0.05, -1.2, "umbral α=0.05", fontsize=10,
        color="#c99a2e", fontweight="600", ha="center")

for bar, q, s in zip(bars, qs, survives):
    label = f"{q:.3f}"
    ax.text(q + 0.015, bar.get_y() + bar.get_height() / 2,
            label, va="center", fontsize=9, fontweight="700" if s else "400",
            fontfamily="serif", color="#b0171f" if s else "#888")

ax.set_xlim(0, 1.0)
ax.set_xlabel("q-value (Benjamini-Hochberg, corregido por múltiples tests)",
              fontsize=11, fontfamily="serif", color="#111")
ax.tick_params(axis="x", labelsize=9)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#111")
ax.spines["bottom"].set_color("#111")

title = "4 de 17 anomalías pasan la corrección estadística"
ax.set_title(title, fontsize=24, fontweight="900", fontfamily="serif",
             color="#111", pad=20, loc="left")

subtitle = "Benjamini-Hochberg α=0.05 · Benford y last-digit NO pasan · las 4 rojas sí son reales"
fig.text(0.06, 0.91, subtitle, fontsize=10, fontfamily="sans-serif",
         color="#555", style="italic")

fig.text(0.06, 0.03,
         "Fuente: ONPE agregado + mesa-a-mesa · captura 2026-04-19 · "
         "SHA-256 verificable",
         fontsize=9, color="#666")
fig.text(0.06, 0.01,
         "Análisis: Jack de Neuracode · github.com/jackthony/auditoria-eg2026 · "
         "auditoria.neuracode.dev",
         fontsize=9, color="#b0171f", fontweight="bold")

out = Path("web/og-fdr.png")
out.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout(rect=(0, 0.06, 1, 0.89))
plt.savefig(out, dpi=144, facecolor="#faf7f2")
print(f"generated: {out}")
