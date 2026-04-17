"""
src/report/figures.py

Genera las figuras PNG del informe técnico.

Uso:
    py src\\report\\figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    ROOT = Path(__file__).resolve().parents[2]
    OUT = ROOT / "reports" / "figures"
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ROOT / "data/processed/regiones.csv")
    meta = json.loads((ROOT / "data/processed/meta.json").read_text(encoding="utf-8"))

    tasa_nac = meta["enviadas_jee"] / meta["actas_total"] * 100

    # ── Fig 1: tasa de impugnación por región ────────────────────
    df_sorted = df.sort_values("tasa_impugnacion", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#c0392b" if x > 10 else "#e67e22" if x > tasa_nac else "#2980b9"
              for x in df_sorted["tasa_impugnacion"]]
    bars = ax.barh(df_sorted["name"], df_sorted["tasa_impugnacion"],
                   color=colors, edgecolor="black", linewidth=0.4)
    ax.axvline(tasa_nac, color="black", linestyle="--", alpha=0.6, linewidth=1.2)
    ax.text(tasa_nac + 0.3, 0, f"Promedio nacional: {tasa_nac:.2f}%",
            fontsize=9, alpha=0.7)
    ax.set_xlabel("Tasa de impugnación (%)", fontsize=11)
    ax.set_title(
        f"Fig. 1 — Tasa de actas enviadas a JEE, por región\n"
        f"ONPE al {meta['pct_global']}% · corte {meta['capture_ts_utc'][:8]} "
        f"{meta['capture_ts_utc'][9:11]}:{meta['capture_ts_utc'][11:13]} UTC",
        fontsize=12, pad=12
    )
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    for bar, v in zip(bars, df_sorted["tasa_impugnacion"]):
        ax.text(v + 0.2, bar.get_y() + bar.get_height()/2,
                f"{v:.2f}%", va="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "fig1_impugnacion_region.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ {OUT.name}/fig1_impugnacion_region.png")

    # ── Fig 2: serie temporal ────────────────────────────────────
    tp = ROOT / "data/processed/tracking.csv"
    if tp.exists():
        dfc = pd.read_csv(tp, parse_dates=["ts"])
        dfc = dfc.drop_duplicates(subset=["pct"], keep="last").sort_values("ts")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                        gridspec_kw={"height_ratios": [2, 1]})
        ax1.plot(dfc["ts"], dfc["rla"], label="López Aliaga (RP)",
                 color="#e74c3c", linewidth=2)
        ax1.plot(dfc["ts"], dfc["sanchez"], label="Sánchez (JPP)",
                 color="#2c3e50", linewidth=2)
        ax1.plot(dfc["ts"], dfc["nieto"], label="Nieto (PBG)",
                 color="#7f8c8d", linewidth=1, alpha=0.6)
        ax1.plot(dfc["ts"], dfc["belmont"], label="Belmont (PCO)",
                 color="#95a5a6", linewidth=1, alpha=0.6)
        ax1.fill_between(dfc["ts"], dfc["rla"], dfc["sanchez"],
                         where=(dfc["sanchez"] >= dfc["rla"]),
                         color="#2c3e50", alpha=0.08)
        ax1.fill_between(dfc["ts"], dfc["rla"], dfc["sanchez"],
                         where=(dfc["sanchez"] < dfc["rla"]),
                         color="#e74c3c", alpha=0.08)
        ax1.set_ylabel("% votos válidos")
        ax1.set_title("Fig. 2 — Evolución del 2º puesto (disputa Sánchez / López Aliaga)",
                      fontsize=12)
        ax1.legend(loc="lower right", fontsize=9, ncol=2)
        ax1.grid(linestyle=":", alpha=0.4)

        ax2.plot(dfc["ts"], dfc["pct"], color="#27ae60", linewidth=2)
        ax2.fill_between(dfc["ts"], dfc["pct"], alpha=0.2, color="#27ae60")
        ax2.set_ylabel("% actas procesadas")
        ax2.set_xlabel("Tiempo (UTC)")
        ax2.grid(linestyle=":", alpha=0.4)

        plt.tight_layout()
        plt.savefig(OUT / "fig2_serie_temporal.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"✓ {OUT.name}/fig2_serie_temporal.png")

    # ── Fig 3: estratos ──────────────────────────────────────────
    # Reconstruir estratos inline para evitar dependencia de src.* en ejecución directa
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    from src.analysis.impugnation_rates import analyze_impugnation
    r = analyze_impugnation(df, meta)
    strata_df = r["by_stratum"]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(strata_df))
    w = 0.25
    ax.bar([i - w for i in x], strata_df["tasa_imp_pct"], w,
           label="Tasa impugnación %", color="#c0392b")
    ax.bar(x, strata_df["rla_pct"], w, label="Voto RLA %", color="#e67e22")
    ax.bar([i + w for i in x], strata_df["sanch_pct"], w,
           label="Voto Sánchez %", color="#2c3e50")
    ax.set_xticks(list(x))
    ax.set_xticklabels(strata_df["estrato"], rotation=10, fontsize=9)
    ax.set_ylabel("Porcentaje")
    ax.legend()
    ax.set_title("Fig. 3 — Impugnación vs voto por estrato geográfico", fontsize=12)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(OUT / "fig3_estratos.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ {OUT.name}/fig3_estratos.png")


if __name__ == "__main__":
    main()
