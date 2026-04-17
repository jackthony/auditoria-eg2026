"""
Autocorrelación espacial (Moran's I) para detección de clustering anómalo.

Test: ¿la tasa de impugnación y el share de RLA se distribuyen al azar
espacialmente, o hay clustering geográfico? Un I > 0 significativo indica
que valores altos (bajos) se agrupan con vecinos de valores altos (bajos).

Referencias:
- Moran, P. A. P. (1950). Notes on continuous stochastic phenomena.
  Biometrika, 37(1/2), 17-23.
- Anselin, L. (1995). Local indicators of spatial association — LISA.
  Geographical Analysis, 27(2), 93-115.

Aplicado a: 25 departamentos + Callao (26 unidades) con matriz de adyacencia
binaria (queen contiguity). Extranjero se excluye por no tener vecindad
geográfica.

Honestidad: con n=26 el poder estadístico es modesto. Un I no significativo
no descarta clustering a menor escala (provincial, distrital, mesa).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "processed" / "regiones.csv"
OUT = ROOT / "reports" / "spatial_cluster.json"

# Matriz de adyacencia geográfica (queen contiguity) departamentos Perú.
# Fuente: división política oficial INEI.
ADJACENCY = {
    "Amazonas": ["Cajamarca", "La Libertad", "San Martín", "Loreto"],
    "Áncash": ["La Libertad", "Huánuco", "Lima", "Pasco"],
    "Apurímac": ["Ayacucho", "Cusco", "Arequipa"],
    "Arequipa": ["Ica", "Ayacucho", "Apurímac", "Cusco", "Puno", "Moquegua"],
    "Ayacucho": ["Huancavelica", "Ica", "Arequipa", "Apurímac", "Cusco", "Junín"],
    "Cajamarca": ["Amazonas", "La Libertad", "Lambayeque", "Piura", "San Martín"],
    "Callao": ["Lima"],
    "Cusco": ["Apurímac", "Ayacucho", "Junín", "Ucayali", "Madre de Dios", "Puno", "Arequipa"],
    "Huancavelica": ["Junín", "Lima", "Ica", "Ayacucho"],
    "Huánuco": ["Áncash", "La Libertad", "San Martín", "Ucayali", "Pasco", "Lima"],
    "Ica": ["Lima", "Huancavelica", "Ayacucho", "Arequipa"],
    "Junín": ["Lima", "Pasco", "Huánuco", "Ucayali", "Cusco", "Ayacucho", "Huancavelica"],
    "La Libertad": ["Lambayeque", "Cajamarca", "Amazonas", "San Martín", "Huánuco", "Áncash"],
    "Lambayeque": ["Piura", "Cajamarca", "La Libertad"],
    "Lima": ["Áncash", "Huánuco", "Pasco", "Junín", "Huancavelica", "Ica", "Callao"],
    "Loreto": ["Amazonas", "San Martín", "Ucayali"],
    "Madre de Dios": ["Ucayali", "Cusco", "Puno"],
    "Moquegua": ["Arequipa", "Puno", "Tacna"],
    "Pasco": ["Huánuco", "Junín", "Lima", "Ucayali"],
    "Piura": ["Tumbes", "Lambayeque", "Cajamarca"],
    "Puno": ["Madre de Dios", "Cusco", "Arequipa", "Moquegua", "Tacna"],
    "San Martín": ["Amazonas", "Loreto", "Ucayali", "Huánuco", "La Libertad", "Cajamarca"],
    "Tacna": ["Moquegua", "Puno"],
    "Tumbes": ["Piura"],
    "Ucayali": ["Loreto", "San Martín", "Huánuco", "Pasco", "Junín", "Cusco", "Madre de Dios"],
}


def build_weight_matrix(names: list[str]) -> np.ndarray:
    """Matriz binaria de adyacencia, fila-estandarizada."""
    n = len(names)
    W = np.zeros((n, n))
    idx = {name: i for i, name in enumerate(names)}
    for name, neighbors in ADJACENCY.items():
        if name not in idx:
            continue
        for nb in neighbors:
            if nb in idx:
                W[idx[name], idx[nb]] = 1.0
    # Fila-estandarizada
    rowsum = W.sum(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        W = np.where(rowsum > 0, W / rowsum, 0.0)
    return W


def morans_i(x: np.ndarray, W: np.ndarray) -> dict:
    """Moran's I con inferencia por permutación (999 iteraciones)."""
    n = len(x)
    x_c = x - x.mean()
    num = (W * np.outer(x_c, x_c)).sum()
    den = (x_c ** 2).sum()
    S0 = W.sum()

    I = (n / S0) * (num / den) if den > 0 and S0 > 0 else 0.0

    # Inferencia por permutación (más robusto que asumir normalidad para n pequeño)
    rng = np.random.default_rng(seed=20260417)
    n_perm = 999
    perm_I = np.empty(n_perm)
    for k in range(n_perm):
        x_perm = rng.permutation(x)
        xp_c = x_perm - x_perm.mean()
        num_p = (W * np.outer(xp_c, xp_c)).sum()
        den_p = (xp_c ** 2).sum()
        perm_I[k] = (n / S0) * (num_p / den_p) if den_p > 0 else 0.0

    # p-valor bilateral empírico
    p_value = (np.abs(perm_I) >= abs(I)).mean()
    # Expected under null
    I_expected = -1.0 / (n - 1)

    return {
        "morans_I": float(I),
        "I_expected_under_null": float(I_expected),
        "n_observations": int(n),
        "S0_sum_weights": float(S0),
        "permutation_p_value": float(p_value),
        "permutation_mean_I": float(perm_I.mean()),
        "permutation_std_I": float(perm_I.std()),
        "verdict": (
            "CLUSTERING_POSITIVO" if I > I_expected and p_value < 0.05
            else "ANTICLUSTERING" if I < I_expected and p_value < 0.05
            else "ALEATORIO"
        ),
    }


def run() -> dict:
    df = pd.read_csv(REG)
    # Excluir Extranjero — no tiene adyacencia geográfica
    df_geo = df[df["name"] != "Extranjero"].copy().reset_index(drop=True)

    # Reordenar para que coincida con ADJACENCY keys
    df_geo["share_rla"] = df_geo["rla_v"] / df_geo["vv"]
    df_geo["share_sanch"] = df_geo["sanch_v"] / df_geo["vv"]

    names = df_geo["name"].tolist()
    W = build_weight_matrix(names)

    out: dict = {
        "method": "Moran's I global + permutation inference (999 perm, seed 20260417)",
        "weight_matrix": "queen contiguity, row-standardized",
        "n_regions": len(names),
        "excluded": ["Extranjero (no geographic adjacency)"],
        "tests": {},
    }

    variables = {
        "tasa_impugnacion": df_geo["tasa_impugnacion"].values / 100.0,
        "share_rla": df_geo["share_rla"].values,
        "share_sanch": df_geo["share_sanch"].values,
        "pct_fuera": ((df_geo["totalActas"] - df_geo["contabilizadas"]) / df_geo["totalActas"]).values,
    }

    for var_name, vals in variables.items():
        out["tests"][var_name] = morans_i(vals, W)

    # Test bivariado: ¿impugnación clusteriza en zonas pro-RLA?
    # Usamos producto cruzado x_RLA · x_impug con matriz W
    rla_c = variables["share_rla"] - variables["share_rla"].mean()
    imp_c = variables["tasa_impugnacion"] - variables["tasa_impugnacion"].mean()
    cross_num = (W * np.outer(rla_c, imp_c)).sum()
    cross_den = np.sqrt((rla_c ** 2).sum() * (imp_c ** 2).sum())
    n_biv = len(rla_c)
    S0_biv = W.sum()
    I_biv = (n_biv / S0_biv) * (cross_num / cross_den) if cross_den > 0 and S0_biv > 0 else 0.0

    # Permutación bivariada
    rng = np.random.default_rng(seed=20260418)
    perm_biv = np.empty(999)
    for k in range(999):
        imp_perm = rng.permutation(variables["tasa_impugnacion"])
        imp_pc = imp_perm - imp_perm.mean()
        num_p = (W * np.outer(rla_c, imp_pc)).sum()
        den_p = np.sqrt((rla_c ** 2).sum() * (imp_pc ** 2).sum())
        perm_biv[k] = (n_biv / S0_biv) * (num_p / den_p) if den_p > 0 else 0.0
    p_biv = (np.abs(perm_biv) >= abs(I_biv)).mean()

    out["bivariate_share_rla_x_tasa_impug"] = {
        "morans_I_bivariate": float(I_biv),
        "permutation_p_value": float(p_biv),
        "verdict": (
            "CLUSTER_RLA_IMPUG" if I_biv > 0 and p_biv < 0.05
            else "ANTI_CLUSTER_RLA_IMPUG" if I_biv < 0 and p_biv < 0.05
            else "ALEATORIO"
        ),
        "interpretation": (
            "I_biv > 0 ⇒ regiones pro-RLA se agrupan con vecinas de alta impugnación "
            "(consistente con hipótesis de focalización geográfica contra RLA)."
        ),
    }

    # Finding consolidado
    suspicious = [
        name for name, t in out["tests"].items()
        if t["verdict"].startswith("CLUSTERING_POSITIVO")
    ]
    if out["bivariate_share_rla_x_tasa_impug"]["verdict"] == "CLUSTER_RLA_IMPUG":
        suspicious.append("RLA×impugnación (bivariado)")

    out["finding"] = {
        "id": "M2",
        "severity": "ALTA" if "RLA×impugnación (bivariado)" in suspicious
                    else "MEDIA" if suspicious else "INFO",
        "description": (
            f"Clustering espacial positivo significativo en: {', '.join(suspicious)}"
            if suspicious else
            "Sin clustering espacial significativo en variables testadas"
        ),
        "suspects": suspicious,
        "caveat": (
            "n=25 regiones, matriz queen contiguity binaria. Un Moran's I no "
            "significativo a este nivel no descarta clustering provincial/distrital. "
            "Pedido formal de data mesa-a-mesa necesario para replicar a mayor "
            "granularidad."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    res = run()
    print("M2 Moran's I (univariados):")
    for var, t in res["tests"].items():
        print(f"  {var:22s} I={t['morans_I']:+.4f} p={t['permutation_p_value']:.3f} -> {t['verdict']}")
    biv = res["bivariate_share_rla_x_tasa_impug"]
    print(f"\n  {'RLA × impugnación':22s} I={biv['morans_I_bivariate']:+.4f} "
          f"p={biv['permutation_p_value']:.3f} -> {biv['verdict']}")
    print(f"\nFinding M2: {res['finding']['severity']} - {res['finding']['description']}")
