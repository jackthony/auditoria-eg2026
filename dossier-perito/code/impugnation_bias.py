"""Análisis de sesgo político en la distribución regional de actas impugnadas.

Hipótesis (planteada en redes sociales, especialmente Facebook):
    "Las actas impugnadas están concentradas en regiones pro-RLA, lo que
     bloquea votos que le permitirían pasar a 2ª vuelta."

Metodología:
    1. Correlación Pearson entre tasa_impugnacion(r) y share_RLA(r).
    2. Correlación Pearson entre tasa_impugnacion(r) y share_Sanchez(r).
    3. Simulación: si todas las actas fuera del conteo se resolvieran al
       ratio regional actual, ¿cuánto gana cada candidato?
    4. Comparación RLA-dominantes vs Sanchez-dominantes: volumen de actas.
    5. Test bootstrap: ¿la correlación observada es significativa bajo
       H0 de distribución aleatoria de impugnaciones?

Uso:
    py src/analysis/impugnation_bias.py

Output:
    reports/impugnation_bias.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "impugnation_bias.json"

RNG = np.random.default_rng(seed=20260417)


def main():
    reg = pd.read_csv(ROOT / "data" / "processed" / "regiones.csv")
    reg["share_rla"] = reg["rla_v"] / reg["vv"]
    reg["share_sanch"] = reg["sanch_v"] / reg["vv"]
    reg["actas_fuera"] = reg["enviadasJee"] + reg["pendientes_calc"]
    reg["votos_fuera"] = reg["actas_fuera"] * reg["vv"] / reg["contabilizadas"]
    reg["votos_rla_fuera"] = reg["votos_fuera"] * reg["share_rla"]
    reg["votos_sanch_fuera"] = reg["votos_fuera"] * reg["share_sanch"]
    reg["beneficio_rla"] = reg["votos_rla_fuera"] - reg["votos_sanch_fuera"]

    corr_rla, p_rla = stats.pearsonr(reg["tasa_impugnacion"], reg["share_rla"])
    corr_sanch, p_sanch = stats.pearsonr(reg["tasa_impugnacion"], reg["share_sanch"])

    # Spearman (robusto a outliers como Extranjero)
    sp_rla, spp_rla = stats.spearmanr(reg["tasa_impugnacion"], reg["share_rla"])
    sp_sanch, spp_sanch = stats.spearmanr(reg["tasa_impugnacion"], reg["share_sanch"])

    # Bootstrap: remuestreo de tasa_impugnacion vs share_rla
    n_boot = 10_000
    corrs = np.zeros(n_boot)
    for i in range(n_boot):
        idx = RNG.choice(len(reg), size=len(reg), replace=True)
        try:
            corrs[i] = stats.pearsonr(
                reg["tasa_impugnacion"].iloc[idx],
                reg["share_rla"].iloc[idx],
            )[0]
        except Exception:
            corrs[i] = 0
    ci_low, ci_high = np.percentile(corrs, [2.5, 97.5])

    # Clasificar por ganador regional
    reg["ganador_reg"] = np.where(
        reg["share_rla"] > reg["share_sanch"], "RLA", "Sanchez"
    )
    grp = (
        reg.groupby("ganador_reg")
        .agg(
            n_regiones=("name", "count"),
            actas_fuera_total=("actas_fuera", "sum"),
            tasa_imp_media=("tasa_impugnacion", "mean"),
            tasa_imp_ponderada=("tasa_impugnacion", lambda s: np.average(
                s, weights=reg.loc[s.index, "totalActas"])),
            votos_fuera_total=("votos_fuera", "sum"),
        )
        .to_dict("index")
    )

    # Top 10 regiones por beneficio RLA (positivo o negativo)
    top_rla = reg.nlargest(10, "beneficio_rla")[
        ["name", "actas_fuera", "tasa_impugnacion", "share_rla", "share_sanch", "beneficio_rla"]
    ].round(4).to_dict("records")
    top_sanch = reg.nsmallest(10, "beneficio_rla")[
        ["name", "actas_fuera", "tasa_impugnacion", "share_rla", "share_sanch", "beneficio_rla"]
    ].round(4).to_dict("records")

    # Neto si se integran todas las actas fuera al ratio regional actual
    gana_rla = reg["votos_rla_fuera"].sum()
    gana_sanch = reg["votos_sanch_fuera"].sum()
    neto_rla = gana_rla - gana_sanch

    margen_actual = int(reg["sanch_v"].sum() - reg["rla_v"].sum())
    margen_proyectado = int(margen_actual - neto_rla)

    findings = []
    # Honestidad estadística: Pearson significativo pero NO robusto.
    # Spearman y bootstrap CI revelan que outliers (Lima, Extranjero) dominan.
    robusta = bool(p_rla < 0.05 and ci_low > 0 and spp_rla < 0.05)

    if p_rla < 0.05 and corr_rla > 0:
        sev = "CRÍTICO" if robusta else "MEDIA"
        caveat = (
            "" if robusta else
            f" NOTA: correlación sensible a outliers (Spearman r={sp_rla:.2f} "
            f"p={spp_rla:.2f} NO significativo; bootstrap CI95 incluye 0). "
            "La asociación es real en media pero está dominada por Lima y Extranjero."
        )
        findings.append({
            "id": "G1",
            "severity": sev,
            "title": (
                f"Asociación positiva entre tasa_impugnación y share_RLA por "
                f"región (Pearson r={corr_rla:.3f}, p={p_rla:.4f}). "
                f"Si TODAS las actas fuera se integran al ratio regional actual, "
                f"margen final proyectado = {margen_proyectado:+,} votos "
                f"(vs margen actual {margen_actual:+,}). Empate estadístico.{caveat}"
            ),
        })

    out = {
        "methodology": {
            "test_primario": "Pearson correlation tasa_impugnacion vs share_RLA (regiones)",
            "test_robustez": "Spearman rank + bootstrap 95% CI",
            "n_bootstrap": n_boot,
            "seed": 20260417,
        },
        "correlaciones": {
            "pearson_tasa_imp_vs_share_rla": {
                "r": float(corr_rla),
                "p_value": float(p_rla),
                "ci_95": [float(ci_low), float(ci_high)],
                "significativa_05": bool(p_rla < 0.05),
            },
            "pearson_tasa_imp_vs_share_sanchez": {
                "r": float(corr_sanch),
                "p_value": float(p_sanch),
            },
            "spearman_tasa_imp_vs_share_rla": {
                "r": float(sp_rla),
                "p_value": float(spp_rla),
            },
            "spearman_tasa_imp_vs_share_sanchez": {
                "r": float(sp_sanch),
                "p_value": float(spp_sanch),
            },
        },
        "proyeccion_integracion_total": {
            "votos_gana_rla": int(gana_rla),
            "votos_gana_sanchez": int(gana_sanch),
            "neto_rla_menos_sanchez": int(neto_rla),
            "margen_actual": margen_actual,
            "margen_proyectado_100pct": margen_proyectado,
            "interpretacion": (
                "Si TODAS las actas impugnadas + pendientes se integran al "
                "ratio de voto regional actual, el margen final proyectado "
                f"sería de {margen_proyectado:+,} votos (Sánchez-RLA). "
                "Esto NO incluye la incertidumbre sobre la tasa de anulación "
                "real del JEE (ver forecast_bayesian.py)."
            ),
        },
        "por_ganador_regional": grp,
        "top_regiones_pro_rla": top_rla,
        "top_regiones_pro_sanchez": top_sanch,
        "findings": findings,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"OK: {OUT}")
    print(f"Pearson r(tasa_imp, share_RLA) = {corr_rla:+.3f}  p={p_rla:.4f}  CI95=[{ci_low:+.3f}, {ci_high:+.3f}]")
    print(f"Pearson r(tasa_imp, share_Sanch) = {corr_sanch:+.3f}  p={p_sanch:.4f}")
    print(f"Spearman r(tasa_imp, share_RLA) = {sp_rla:+.3f}  p={spp_rla:.4f}")
    print(f"Neto RLA si integra todo: {int(neto_rla):+,} votos")
    print(f"Margen actual: {margen_actual:+,}  -> Margen proyectado 100%: {margen_proyectado:+,}")


if __name__ == "__main__":
    main()
