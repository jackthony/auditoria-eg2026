"""
scripts/build_storytelling_figures.py — Assets PNG para storytelling.

Genera 5 PNGs listos para publicacion (X, TikTok, prensa):

- h4_hero_jpp_ratio.png         · Bar chart JPP 41.65% vs 10.91% (hero)
- h7a_antitaque_distrib.png     · Distribucion geografica 900k+ (anti-ataque)
- h12_blowout_mesa_emb.png      · Blowout mesa emblematica (dominancia >=80%)
- h9_locales_100pct_imp.png     · Top 10 locales 100% mesas impugnadas
- h1_sesgo_geografico.png       · Impugnadas por departamento (sorted)

Estilo: Neuracode brand — Fraunces-like (DejaVu Serif), paper/ink/blood.
Export 1200x675 (16:9 social), dpi=150.

Stack: Polars + DuckDB + Matplotlib.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib import font_manager

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "reports" / "hallazgos_20260420" / "eg2026.duckdb"
FINDINGS = ROOT / "reports" / "hallazgos_20260420" / "findings_consolidado_0420.json"
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

PAPER = "#faf7f2"
INK = "#111111"
BLOOD = "#b0171f"
MUTED = "#6b6b6b"
ACCENT = "#0a2540"
GOLD = "#ffb800"

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 11,
    "axes.facecolor": PAPER,
    "figure.facecolor": PAPER,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

FIG_SIZE = (12, 6.75)
DPI = 150


def add_footer(ax, fig, extra: str = "") -> None:
    txt = f"Neuracode · @JackTonyAC · 92,766 mesas · ONPE EG2026 · SHA-256 + IPFS{(' · ' + extra) if extra else ''}"
    fig.text(0.5, 0.02, txt, ha="center", fontsize=8, color=MUTED, style="italic")


# ---------- H4: hero JPP ratio ----------

def fig_h4() -> None:
    con = duckdb.connect(str(DB), read_only=True)
    q = """
    WITH per_mesa AS (
      SELECT v.codigo_mesa, m.mesa_especial, m.votos_validos,
        SUM(CASE WHEN v.partido='JUNTOS POR EL PERÚ' THEN v.votos ELSE 0 END) AS jpp
      FROM voto v JOIN mesa m USING(codigo_mesa)
      WHERE m.estado_acta='D' AND NOT v.es_voto_especial AND m.votos_validos > 0
      GROUP BY v.codigo_mesa, m.mesa_especial, m.votos_validos
    )
    SELECT mesa_especial,
           SUM(jpp) AS jpp,
           SUM(votos_validos) AS total,
           SUM(jpp)*100.0/SUM(votos_validos) AS pct
    FROM per_mesa GROUP BY mesa_especial
    """
    df = con.execute(q).pl()
    con.close()

    normal = df.filter(~pl.col("mesa_especial")).row(0, named=True)
    esp = df.filter(pl.col("mesa_especial")).row(0, named=True)

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    labels = ["Mesas normales\n(88,063)", "Mesas 900k+\n(4,703)"]
    values = [normal["pct"], esp["pct"]]
    colors = [ACCENT, BLOOD]
    bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor=INK, linewidth=1.2)

    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width()/2, v + 1.0, f"{v:.2f}%",
                ha="center", fontsize=28, fontweight="bold", color=INK)

    ax.set_ylim(0, max(values) * 1.22)
    ax.set_ylabel("% de votos por partido", fontsize=13)
    ax.set_title("HALL-0420-H4 · JUNTOS POR EL PERÚ: ratio 3.82× en mesas 900k+",
                 fontsize=17, fontweight="bold", pad=18, loc="left")

    fig.text(0.5, 0.88, "z = 698 · Cohen h = 0.73 · Bootstrap IC95 [29.46, 30.79] pp",
             ha="center", fontsize=11, color=MUTED)

    ax.grid(axis="y", alpha=0.25, ls="--")
    ax.set_axisbelow(True)

    add_footer(ax, fig, "Newcombe 1998 · Cohen 1988 · Efron-Tibshirani 1993")
    plt.tight_layout(rect=(0, 0.04, 1, 0.92))
    out = FIG_DIR / "h4_hero_jpp_ratio.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[H4] guardado: {out.relative_to(ROOT)}  N-normal={normal['pct']:.2f}%  N-900k={esp['pct']:.2f}%")


# ---------- H7A: distribucion geografica 900k+ (anti-ataque) ----------

def fig_h7a() -> None:
    finding = next(f for f in json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
                   if f["id"] == "HALL-0420-H7A")
    top = finding.get("top_deptos") or finding.get("distribucion_geografica")
    if not top:
        con = duckdb.connect(str(DB), read_only=True)
        q = """
        SELECT depto_real AS depto, COUNT(*) AS n
        FROM mesa WHERE mesa_especial
        GROUP BY depto_real ORDER BY n DESC
        """
        top = con.execute(q).pl().to_dicts()
        con.close()

    deptos = [r.get("depto") or r.get("departamento") or r.get("depto_real") for r in top]
    counts = [int(r.get("n") or r.get("mesas") or r.get("n_mesas") or r.get("mesas_900k") or 0) for r in top]

    order = np.argsort(counts)[::-1]
    deptos = [deptos[i] for i in order][:12]
    counts = [counts[i] for i in order][:12]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    ypos = np.arange(len(deptos))[::-1]
    colors = [BLOOD if d.upper() == "EXTRANJERO" else ACCENT for d in deptos]
    ax.barh(ypos, counts, color=colors, edgecolor=INK, linewidth=1.0)
    for y, c in zip(ypos, counts):
        ax.text(c + max(counts)*0.012, y, f"{c:,}", va="center", fontsize=11, fontweight="bold")

    ax.set_yticks(ypos)
    ax.set_yticklabels(deptos, fontsize=11)
    ax.set_xlabel("Mesas 900k+ (especiales)", fontsize=12)
    ax.set_title("HALL-0420-H7A · 900k+ NO son 'solo extranjero/militares'",
                 fontsize=17, fontweight="bold", pad=18, loc="left")

    fig.text(0.5, 0.88, "Extranjero = solo 34 mesas (0.7%). Distribución nacional real.",
             ha="center", fontsize=11, color=MUTED)

    ax.grid(axis="x", alpha=0.25, ls="--")
    ax.set_axisbelow(True)
    add_footer(ax, fig, "Anti-ataque · Dato ONPE mapping prefix→depto")
    plt.tight_layout(rect=(0, 0.04, 1, 0.92))
    out = FIG_DIR / "h7a_antitaque_distrib.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[H7A] guardado: {out.relative_to(ROOT)}  deptos={len(deptos)}")


# ---------- H12: blowout mesa emblematica ----------

def fig_h12() -> None:
    con = duckdb.connect(str(DB), read_only=True)
    q = """
    WITH mesa_winner AS (
      SELECT v.codigo_mesa, v.partido, v.votos,
             m.votos_validos, m.mesa_especial,
             ROW_NUMBER() OVER (PARTITION BY v.codigo_mesa ORDER BY v.votos DESC) AS rnk
      FROM voto v JOIN mesa m USING(codigo_mesa)
      WHERE m.estado_acta='D' AND NOT v.es_voto_especial
        AND m.votos_validos >= 100
        AND v.partido NOT IN ('VOTOS NULOS','VOTOS EN BLANCO','VOTOS IMPUGNADOS')
    )
    SELECT codigo_mesa, partido, votos, votos_validos, mesa_especial,
           votos*100.0/votos_validos AS pct
    FROM mesa_winner WHERE rnk=1 AND votos*100.0/votos_validos >= 80
      AND votos*100.0/votos_validos <= 100
    ORDER BY votos DESC, votos*100.0/votos_validos DESC
    LIMIT 1
    """
    row = con.execute(q).pl().row(0, named=True)
    con.close()

    mesa = row["codigo_mesa"]
    partido_winner = row["partido"]
    pct_winner = row["pct"]

    con = duckdb.connect(str(DB), read_only=True)
    q2 = f"""
    SELECT v.partido, v.votos, v.votos*100.0/m.votos_validos AS pct
    FROM voto v JOIN mesa m USING(codigo_mesa)
    WHERE v.codigo_mesa='{mesa}' AND NOT v.es_voto_especial
      AND v.partido NOT IN ('VOTOS NULOS','VOTOS EN BLANCO','VOTOS IMPUGNADOS')
    ORDER BY v.votos DESC LIMIT 8
    """
    df = con.execute(q2).pl()
    con.close()

    partidos = df["partido"].to_list()
    pcts = df["pct"].to_list()

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    colors = [BLOOD if p == partido_winner else MUTED for p in partidos]
    short = [p if len(p) <= 22 else p[:20] + "…" for p in partidos]
    ypos = np.arange(len(partidos))[::-1]
    ax.barh(ypos, pcts, color=colors, edgecolor=INK, linewidth=1.0)
    for y, v, p in zip(ypos, pcts, partidos):
        ax.text(v + 1.0, y, f"{v:.1f}%", va="center", fontsize=11, fontweight="bold",
                color=BLOOD if p == partido_winner else INK)

    ax.set_yticks(ypos)
    ax.set_yticklabels(short, fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% votos válidos", fontsize=12)
    ax.set_title(f"HALL-0420-H12 · Blowout mesa {mesa}: {partido_winner} = {pct_winner:.1f}%",
                 fontsize=15, fontweight="bold", pad=18, loc="left")

    fig.text(0.5, 0.88, f"Dominancia extrema — resto de partidos suma {100 - pct_winner:.1f}%",
             ha="center", fontsize=11, color=MUTED)

    ax.grid(axis="x", alpha=0.25, ls="--")
    ax.set_axisbelow(True)
    add_footer(ax, fig, "z-test Newcombe 1998 · blowout >= 80%")
    plt.tight_layout(rect=(0, 0.04, 1, 0.92))
    out = FIG_DIR / "h12_blowout_mesa_emb.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[H12] guardado: {out.relative_to(ROOT)}  mesa={mesa} {partido_winner}={pct_winner:.1f}%")


# ---------- H9: locales 100% impugnados ----------

def fig_h9() -> None:
    con = duckdb.connect(str(DB), read_only=True)
    q = """
    SELECT depto_real, codigo_local, COUNT(*) AS n_mesas,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS n_imp
    FROM mesa
    GROUP BY depto_real, codigo_local
    HAVING SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) = COUNT(*)
       AND COUNT(*) >= 3
    ORDER BY n_mesas DESC LIMIT 12
    """
    try:
        df = con.execute(q).pl()
    except Exception:
        q = """
        SELECT depto_real, local_votacion AS codigo_local, COUNT(*) AS n_mesas,
               SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS n_imp
        FROM mesa
        GROUP BY depto_real, local_votacion
        HAVING SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) = COUNT(*)
           AND COUNT(*) >= 3
        ORDER BY n_mesas DESC LIMIT 12
        """
        df = con.execute(q).pl()
    con.close()

    if len(df) == 0:
        finding = next(f for f in json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
                       if f["id"] == "HALL-0420-H9")
        top = finding.get("top_locales") or finding.get("locales_top") or []
        if not top:
            print("[H9] sin datos — saltado")
            return
        labels = [f"{l.get('depto','?')} · {l.get('codigo_local','?')}" for l in top[:12]]
        counts = [int(l.get("n_mesas", 0)) for l in top[:12]]
    else:
        labels = [f"{r['depto_real']} · {str(r['codigo_local'])[:12]}" for r in df.iter_rows(named=True)]
        counts = df["n_mesas"].to_list()

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    ypos = np.arange(len(labels))[::-1]
    ax.barh(ypos, counts, color=BLOOD, edgecolor=INK, linewidth=1.0)
    for y, c in zip(ypos, counts):
        ax.text(c + max(counts)*0.012, y, f"{c}", va="center", fontsize=11, fontweight="bold")

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("# mesas (todas impugnadas)", fontsize=12)
    ax.set_title("HALL-0420-H9 · Locales con 100% de mesas impugnadas",
                 fontsize=17, fontweight="bold", pad=18, loc="left")

    fig.text(0.5, 0.88, "Top 12 — todos sus escrutinios quedan en pausa forense",
             ha="center", fontsize=11, color=MUTED)

    ax.grid(axis="x", alpha=0.25, ls="--")
    ax.set_axisbelow(True)
    add_footer(ax, fig, "estado_acta='I' · DuckDB local")
    plt.tight_layout(rect=(0, 0.04, 1, 0.92))
    out = FIG_DIR / "h9_locales_100pct_imp.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[H9] guardado: {out.relative_to(ROOT)}  n_locales={len(labels)}")


# ---------- H1: sesgo geografico ----------

def fig_h1() -> None:
    con = duckdb.connect(str(DB), read_only=True)
    q = """
    SELECT depto_real,
           COUNT(*) AS n_total,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS n_imp,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS pct
    FROM mesa
    GROUP BY depto_real
    HAVING COUNT(*) >= 100
    ORDER BY pct DESC
    """
    df = con.execute(q).pl()
    con.close()

    deptos = df["depto_real"].to_list()
    pcts = df["pct"].to_list()
    global_pct = 6.16

    fig, ax = plt.subplots(figsize=(12, 8), dpi=DPI)
    ypos = np.arange(len(deptos))[::-1]
    colors = [BLOOD if p >= 10 else (GOLD if p >= global_pct else ACCENT) for p in pcts]
    ax.barh(ypos, pcts, color=colors, edgecolor=INK, linewidth=0.8)
    for y, v in zip(ypos, pcts):
        ax.text(v + 0.3, y, f"{v:.2f}%", va="center", fontsize=9)

    ax.axvline(global_pct, color=INK, ls="--", lw=1.2, label=f"Global {global_pct}%")

    ax.set_yticks(ypos)
    ax.set_yticklabels(deptos, fontsize=9)
    ax.set_xlabel("% mesas impugnadas", fontsize=12)
    ax.set_title("HALL-0420-H1 · Sesgo geográfico de impugnadas",
                 fontsize=17, fontweight="bold", pad=18, loc="left")

    fig.text(0.5, 0.93, "Extranjero 26.27% · Loreto 14.87% · Ucayali 12.02% · global 6.16%",
             ha="center", fontsize=11, color=MUTED)

    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="x", alpha=0.25, ls="--")
    ax.set_axisbelow(True)
    add_footer(ax, fig, "z-test 2-prop Newcombe 1998")
    plt.tight_layout(rect=(0, 0.04, 1, 0.95))
    out = FIG_DIR / "h1_sesgo_geografico.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[H1] guardado: {out.relative_to(ROOT)}  deptos={len(deptos)}")


def main() -> int:
    print(f"DB: {DB.relative_to(ROOT)}")
    print(f"Out: {FIG_DIR.relative_to(ROOT)}")
    print()
    fig_h4()
    fig_h7a()
    fig_h12()
    fig_h9()
    fig_h1()
    print()
    print("=== PNGs generados ===")
    for p in sorted(FIG_DIR.glob("h*.png")):
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
