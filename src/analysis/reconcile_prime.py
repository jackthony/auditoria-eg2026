"""
src/analysis/reconcile_prime.py — Las 4 reconciliations tipo Prime Institute.

Responde las 4 preguntas críticas de la tesis Prime:
  F1. Suma mesa-a-mesa vs total nacional: ¿ranking cambia?
  F2. ¿Dónde están las mesas faltantes? (universo JEE - walker)
  F3. ¿44% del desfase va a candidato con 11%?
  F4. Pendientes reales vs pendientes reportados.

Input:
  reports/mesas_summary.json       (desde extract_mesa_votes.py)
  reports/mesas_presidencial.csv   (detalle mesa×agrupación)
  captures/{ts}/raw/totales.json
  captures/{ts}/raw/presidencial.json
  captures/{ts}/raw/mesa_totales.json

Output:
  reports/findings_prime.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def is_special(nombre: str) -> bool:
    n = (nombre or "").upper()
    return "BLANCO" in n or "NULO" in n


def load_oficial(capture_ts: str, ROOT: Path) -> dict:
    raw = ROOT / "captures" / capture_ts / "raw"
    tot = json.loads((raw / "totales.json").read_text(encoding="utf-8"))["data"]
    presi = json.loads((raw / "presidencial.json").read_text(encoding="utf-8"))["data"]
    mesa = json.loads((raw / "mesa_totales.json").read_text(encoding="utf-8"))["data"]
    return {"totales": tot, "presidencial": presi, "mesa": mesa}


def agrupaciones_oficial(presi_list: list) -> dict[str, dict]:
    out = {}
    for x in presi_list:
        nombre = (x.get("nombreAgrupacionPolitica") or "").strip()
        if not nombre or is_special(nombre):
            continue
        out[nombre] = {
            "votos": x.get("totalVotosValidos", 0),
            "pct": x.get("porcentajeVotosValidos", 0.0),
        }
    return out


def agrupaciones_mesa(csv_path: Path) -> dict[str, int]:
    """Suma votos por agrupación solo en mesas Contabilizadas."""
    out: Counter = Counter()
    with csv_path.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["estado"] != "Contabilizada":
                continue
            nombre = row["agrupacion"]
            if is_special(nombre):
                continue
            try:
                out[nombre] += int(row["votos"])
            except (ValueError, TypeError):
                pass
    return dict(out)


def ranking(d: dict[str, int | float], key="votos") -> list[tuple[str, int, float, int]]:
    """→ [(nombre, votos, pct, rank)] ordenado desc."""
    if not d:
        return []
    total = sum(d.values()) if isinstance(list(d.values())[0], int) else \
            sum(v.get("votos", 0) for v in d.values())
    items = []
    for k, v in d.items():
        votos = v if isinstance(v, int) else v.get("votos", 0)
        pct = votos / total * 100 if total else 0
        items.append((k, votos, pct))
    items.sort(key=lambda x: -x[1])
    return [(n, v, p, i + 1) for i, (n, v, p) in enumerate(items)]


def finding_1_ranking(oficial: dict, mesa: dict[str, int]) -> dict:
    """F1: ¿Ranking cambia? (el gran hallazgo Prime)"""
    rk_of = ranking(oficial)
    rk_me = ranking(mesa)
    top10_of = [(n, v, round(p, 3), r) for n, v, p, r in rk_of[:10]]
    top10_me = [(n, v, round(p, 3), r) for n, v, p, r in rk_me[:10]]

    # Posición por nombre
    pos_of = {n: r for n, _, _, r in rk_of}
    pos_me = {n: r for n, _, _, r in rk_me}
    cambios = []
    for n in set(pos_of) | set(pos_me):
        ro = pos_of.get(n, None)
        rm = pos_me.get(n, None)
        if ro and rm and ro != rm and min(ro, rm) <= 10:
            cambios.append({"agrupacion": n, "rank_oficial": ro, "rank_mesa": rm,
                            "delta": ro - rm})
    cambios.sort(key=lambda x: x["rank_oficial"])

    return {
        "id": "PRIME-F1-RANKING",
        "severity": "CRITICO" if cambios else "INFO",
        "pregunta": "¿Suma mesa-a-mesa da ranking distinto al total nacional?",
        "top10_oficial": top10_of,
        "top10_mesa_a_mesa": top10_me,
        "cambios_ranking_top10": cambios,
        "interpretacion": "Cambio en 2° puesto = hallazgo Prime confirmado" if cambios else
                          "Ranking top-10 coincide",
    }


def finding_2_mesas_faltantes(oficial: dict, procesadas: int, contabilizadas: int) -> dict:
    """F2: Universo oficial vs universo walker."""
    total_actas_oficial = oficial["totales"]["totalActas"]
    contab_oficial = oficial["totales"]["contabilizadas"]
    mesas_instaladas = oficial["mesa"]["mesasInstaladas"]

    faltantes = total_actas_oficial - procesadas
    delta_contab = contabilizadas - contab_oficial
    return {
        "id": "PRIME-F2-MESAS-FALTANTES",
        "severity": "CRITICO" if faltantes > 1000 else ("MEDIA" if faltantes > 0 else "INFO"),
        "pregunta": "¿Dónde están las mesas que faltan entre la API y el universo oficial?",
        "totalActas_oficial": total_actas_oficial,
        "mesasInstaladas_oficial": mesas_instaladas,
        "mesas_obtenidas_walker": procesadas,
        "mesas_contabilizadas_walker": contabilizadas,
        "mesas_contabilizadas_oficial": contab_oficial,
        "delta_universo": faltantes,
        "delta_contabilizadas": delta_contab,
        "interpretacion": f"{faltantes:,} mesas del universo oficial no devuelven data "
                          f"mesa-a-mesa. Prime reportó 4,343 — nosotros {faltantes:,}.",
    }


def finding_3_desfase_agrupacion(oficial: dict, mesa: dict[str, int]) -> dict:
    """F3: ¿44% del desfase va a agrupación con 11%?"""
    total_of = sum(v["votos"] for v in oficial.values())
    total_me = sum(mesa.values())
    delta_total = total_of - total_me  # votos oficiales que no aparecen mesa-a-mesa

    desfase_por_agr = []
    for n, info in oficial.items():
        v_of = info["votos"]
        v_me = mesa.get(n, 0)
        delta = v_of - v_me
        pct_of = info["pct"]
        pct_delta = delta / delta_total * 100 if delta_total else 0
        desfase_por_agr.append({
            "agrupacion": n,
            "votos_oficial": v_of,
            "votos_mesa": v_me,
            "delta": delta,
            "pct_oficial": round(pct_of, 3),
            "pct_del_desfase": round(pct_delta, 3),
            "ratio_desfase_vs_pct_oficial": round(pct_delta / pct_of, 2) if pct_of else None,
        })
    desfase_por_agr.sort(key=lambda x: -abs(x["delta"]))

    # ¿Hay alguna agrupación con ratio desfase/peso real >> 1?
    atipicas = [x for x in desfase_por_agr
                if x["ratio_desfase_vs_pct_oficial"] and x["ratio_desfase_vs_pct_oficial"] >= 2
                and x["pct_oficial"] < 15]

    return {
        "id": "PRIME-F3-DESFASE-AGRUPACION",
        "severity": "CRITICO" if atipicas else "MEDIA",
        "pregunta": "¿El desfase entre suma mesa-a-mesa y total oficial está sesgado a una agrupación?",
        "votos_totales_oficial": total_of,
        "votos_totales_mesa": total_me,
        "delta_total": delta_total,
        "top_agrupaciones_por_desfase": desfase_por_agr[:15],
        "agrupaciones_atipicas_ratio_ge_2": atipicas,
        "interpretacion": f"Delta total = {delta_total:,} votos válidos faltan en mesa-a-mesa. "
                          + ("Hay agrupaciones con sobre-representación en el desfase." if atipicas
                             else "Desfase proporcional a peso real."),
    }


def finding_4_pendientes(oficial: dict, mesas_observadas: int,
                          mesas_pendientes_walker: int, mesas_otros: int) -> dict:
    """F4: Pendientes reales en API vs reportados oficialmente."""
    pendientes_oficial = oficial["totales"]["pendientesJee"]
    enviadas_jee = oficial["totales"]["enviadasJee"]
    no_contabilizadas_walker = mesas_observadas + mesas_pendientes_walker + mesas_otros

    return {
        "id": "PRIME-F4-PENDIENTES",
        "severity": "MEDIA" if no_contabilizadas_walker > pendientes_oficial * 3 else "INFO",
        "pregunta": "¿El número de pendientes en el sistema coincide con lo reportado?",
        "pendientes_oficial": pendientes_oficial,
        "enviadas_jee_oficial": enviadas_jee,
        "mesas_no_contabilizadas_walker": no_contabilizadas_walker,
        "interpretacion": f"Oficial reporta {pendientes_oficial} pendientes, "
                          f"walker encuentra {no_contabilizadas_walker} mesas en estados "
                          f"no-Contabilizada.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ts", help="capture ts con totales.json, ej. 20260419T031241Z")
    ap.add_argument("--mesa-ts", default=None,
                    help="capture ts del walker (default: mismo que ts)")
    args = ap.parse_args()

    ROOT = Path(__file__).resolve().parents[2]
    mesa_ts = args.mesa_ts or args.ts

    # Summary extractor
    summary_p = ROOT / "reports" / "mesas_summary.json"
    csv_p = ROOT / "reports" / "mesas_presidencial.csv"
    if not summary_p.exists() or not csv_p.exists():
        print(f"ERROR: correr extract_mesa_votes.py {mesa_ts} primero", file=sys.stderr)
        return 2

    summary = json.loads(summary_p.read_text(encoding="utf-8"))
    oficial = load_oficial(args.ts, ROOT)
    of_agr = agrupaciones_oficial(oficial["presidencial"])
    me_agr = agrupaciones_mesa(csv_p)

    f1 = finding_1_ranking(of_agr, me_agr)
    f2 = finding_2_mesas_faltantes(oficial,
                                    summary["mesas_procesadas"],
                                    summary["mesas_contabilizadas"])
    f3 = finding_3_desfase_agrupacion(of_agr, me_agr)
    f4 = finding_4_pendientes(oficial,
                               summary["mesas_observadas_jee"],
                               summary["mesas_pendientes"],
                               summary["mesas_otros_estado"])

    out = {
        "capture_oficial_ts": args.ts,
        "capture_mesa_ts": mesa_ts,
        "findings": [f1, f2, f3, f4],
        "metadata": {
            "oficial_totalActas": oficial["totales"]["totalActas"],
            "oficial_contabilizadas": oficial["totales"]["contabilizadas"],
            "oficial_porcentaje": oficial["totales"]["actasContabilizadas"],
            "walker_mesas_procesadas": summary["mesas_procesadas"],
            "walker_mesas_contabilizadas": summary["mesas_contabilizadas"],
        },
    }

    out_p = ROOT / "reports" / "findings_prime.json"
    out_p.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print humano
    print("═" * 70)
    print("FINDINGS PRIME-STYLE")
    print("═" * 70)
    for f in out["findings"]:
        print(f"\n[{f['severity']}] {f['id']}")
        print(f"  {f['pregunta']}")
        print(f"  → {f['interpretacion']}")
    print()
    print("F1 RANKING:")
    print("  Oficial top 5:")
    for n, v, p, r in f1["top10_oficial"][:5]:
        print(f"    #{r}  {p:>6.3f}%  {v:>10,}  {n[:50]}")
    print("  Mesa-a-mesa top 5:")
    for n, v, p, r in f1["top10_mesa_a_mesa"][:5]:
        print(f"    #{r}  {p:>6.3f}%  {v:>10,}  {n[:50]}")
    if f1["cambios_ranking_top10"]:
        print("  CAMBIOS DE RANK:")
        for c in f1["cambios_ranking_top10"]:
            print(f"    {c['agrupacion'][:40]}: of#{c['rank_oficial']} → mesa#{c['rank_mesa']}")
    print()
    print(f"[extract] Output: {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
