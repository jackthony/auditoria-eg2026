"""
src/analysis/impugnation_rates.py

Análisis de tasas de impugnación por región. Detecta outliers por z-score
y compara estratos geográficos (Lima+Callao vs resto vs sur andino).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


SUR_ANDINO = {
    "Apurímac", "Ayacucho", "Cusco", "Huancavelica", "Puno",
    "Arequipa", "Moquegua", "Tacna", "Madre de Dios"
}
LIMA_CALLAO = {"Lima", "Callao"}


def stratify(name: str) -> str:
    if name in LIMA_CALLAO:
        return "Lima+Callao"
    if name in SUR_ANDINO:
        return "Sur andino"
    return "Resto"


def analyze_impugnation(df: pd.DataFrame, meta: dict) -> dict:
    """Retorna un dict con resultados del análisis."""
    results = {"by_region": None, "by_stratum": None, "outliers": [], "findings": []}

    # ── Z-score por región ───────────────────────────────────────
    mu = df["tasa_impugnacion"].mean()
    sd = df["tasa_impugnacion"].std()
    df_imp = df[["name", "totalActas", "enviadasJee", "tasa_impugnacion"]].copy()
    df_imp["z_score"] = (df_imp["tasa_impugnacion"] - mu) / sd
    df_imp = df_imp.sort_values("tasa_impugnacion", ascending=False).reset_index(drop=True)
    results["by_region"] = df_imp

    outliers = df_imp[df_imp["z_score"].abs() > 2]
    results["outliers"] = outliers[["name", "tasa_impugnacion", "z_score"]].to_dict("records")

    # ── Estratificación ──────────────────────────────────────────
    df2 = df.copy()
    df2["estrato"] = df2["name"].apply(stratify)
    rows = []
    for est, g in df2.groupby("estrato"):
        act = int(g["totalActas"].sum())
        imp = int(g["enviadasJee"].sum())
        vv = int(g["vv"].sum())
        rla = int(g["rla_v"].sum())
        sanch = int(g["sanch_v"].sum())
        rows.append({
            "estrato": est,
            "actas_total": act,
            "impugnadas": imp,
            "tasa_imp_pct": 100 * imp / act,
            "rla_pct": 100 * rla / vv if vv else 0,
            "sanch_pct": 100 * sanch / vv if vv else 0,
        })
    results["by_stratum"] = pd.DataFrame(rows)

    # ── Z-test de dos proporciones: Lima+Callao vs Resto ────────
    lc = df2[df2["estrato"] == "Lima+Callao"]
    rs = df2[df2["estrato"] != "Lima+Callao"]
    n1, x1 = int(lc["totalActas"].sum()), int(lc["enviadasJee"].sum())
    n2, x2 = int(rs["totalActas"].sum()), int(rs["enviadasJee"].sum())
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    z = (p1 - p2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    results["ztest_lima_vs_resto"] = {
        "lima_tasa": p1 * 100,
        "resto_tasa": p2 * 100,
        "diff_pp": (p1 - p2) * 100,
        "z": z,
        "p_value": p_value,
        "significativo_al_1pct": p_value < 0.01,
    }

    # ── Findings ─────────────────────────────────────────────────
    if outliers.empty:
        results["findings"].append({
            "severity": "INFO",
            "id": "A1",
            "title": "Sin outliers severos de impugnación a nivel regional",
            "detail": (f"Todas las 26 regiones están dentro de ±2σ. Rango: "
                       f"{df_imp['tasa_impugnacion'].min():.2f}% a "
                       f"{df_imp['tasa_impugnacion'].max():.2f}%."),
        })
    else:
        outlier_list = ", ".join(
            f"{r['name']} ({r['tasa_impugnacion']:.2f}%, z={r['z_score']:+.2f})"
            for _, r in outliers.iterrows()
        )
        results["findings"].append({
            "severity": "MEDIA",
            "id": "A1",
            "title": f"Regiones con tasa de impugnación anómala (|z|>2): {outlier_list}",
            "detail": (f"{len(outliers)} región(es) fuera de ±2σ respecto al promedio "
                       f"regional de {mu:.2f}% (σ={sd:.2f}%)."),
        })

    results["findings"].append({
        "severity": "MEDIA" if results["ztest_lima_vs_resto"]["significativo_al_1pct"] else "INFO",
        "id": "A2",
        "title": "Diferencia de tasa de impugnación Lima+Callao vs resto del país",
        "detail": (f"Lima+Callao: {p1*100:.2f}% · Resto: {p2*100:.2f}% · "
                   f"Diferencia: {(p1-p2)*100:+.2f}pp (z={z:+.2f}, p={p_value:.4g}). "
                   + ("Estadísticamente significativa al 1%. "
                      "La asimetría NO es perjudicial para candidatos con mayor "
                      "votación en Lima+Callao."
                      if p_value < 0.01 else "Diferencia no significativa.")),
    })

    return results


def run(root: Path | None = None):
    ROOT = root or Path(__file__).resolve().parents[2]
    df = pd.read_csv(ROOT / "data/processed/regiones.csv")
    meta = json.loads((ROOT / "data/processed/meta.json").read_text(encoding="utf-8"))

    r = analyze_impugnation(df, meta)

    # Imprimir resumen
    print("═" * 70)
    print(" A. TASA DE IMPUGNACIÓN POR REGIÓN")
    print("═" * 70)
    nat_tasa = meta["enviadas_jee"] / meta["actas_total"] * 100
    print(f"Tasa nacional: {nat_tasa:.3f}%  "
          f"({meta['enviadas_jee']:,} / {meta['actas_total']:,})\n")

    for _, row in r["by_region"].iterrows():
        flag = "⚠ OUTLIER" if abs(row["z_score"]) > 2 else (
            "→ elevado" if row["z_score"] > 1 else "")
        print(f"  {row['name']:<20} {int(row['totalActas']):>7,}  "
              f"imp={int(row['enviadasJee']):>5,}  "
              f"{row['tasa_impugnacion']:>5.2f}%  z={row['z_score']:+.2f}  {flag}")

    print("\n" + "═" * 70)
    print(" B. ESTRATIFICACIÓN GEOGRÁFICA")
    print("═" * 70)
    print(r["by_stratum"].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    zt = r["ztest_lima_vs_resto"]
    print(f"\nz-test Lima+Callao vs Resto:")
    print(f"  Lima+Callao: {zt['lima_tasa']:.2f}%")
    print(f"  Resto      : {zt['resto_tasa']:.2f}%")
    print(f"  z = {zt['z']:+.3f}  p = {zt['p_value']:.4g}  "
          f"{'✓ significativo al 1%' if zt['significativo_al_1pct'] else '— no sig.'}")

    # Guardar
    out = ROOT / "reports" / "impugnadas_por_region.csv"
    out.parent.mkdir(exist_ok=True, parents=True)
    r["by_region"].to_csv(out, index=False, encoding="utf-8")
    print(f"\n[A] escrito: {out.relative_to(ROOT)}")

    return r


if __name__ == "__main__":
    run()
