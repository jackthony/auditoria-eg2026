"""
src/analysis/jee_simulation.py

Simulación del impacto de la resolución de actas impugnadas + pendientes
sobre el margen Sánchez-RLA para el 2º puesto.
"""

from __future__ import annotations

import json
from pathlib import Path

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def run(root: Path | None = None):
    ROOT = root or Path(__file__).resolve().parents[2]
    meta = json.loads((ROOT / "data/processed/meta.json").read_text(encoding="utf-8"))
    capture_dir = ROOT / meta["capture_dir"]
    snap1 = json.loads((capture_dir / "raw" / "snap1.json").read_text(encoding="utf-8"))
    nat = snap1["national"]

    margen = meta["margen_sanch_rla_votos"]
    jee = nat["enviadasJee"]
    pend = nat["pendientesJee"]
    votos_por_acta = nat["votosValidos"] / nat["contabilizadas"]
    votos_juego = int((jee + pend) * votos_por_acta)

    # Proyección proporcional
    rla_natural = votos_juego * nat["candidates"]["rla"] / 100
    sanch_natural = votos_juego * nat["candidates"]["sanch"] / 100
    margen_proyectado = margen + (sanch_natural - rla_natural)

    # Break-even: qué % de los votos RLA+Sánchez en disputa debe ir a RLA
    share_combined = (nat["candidates"]["rla"] + nat["candidates"]["sanch"]) / 100
    votos_para_los_dos = votos_juego * share_combined
    x_needed = (votos_para_los_dos + margen) / 2
    pct_rla_break_even = 100 * x_needed / votos_para_los_dos
    pct_rla_historico = (100 * nat["candidates"]["rla"] /
                         (nat["candidates"]["rla"] + nat["candidates"]["sanch"]))

    print("═" * 70)
    print(" E. SIMULACIÓN — resolución de actas JEE y 2º puesto")
    print("═" * 70)
    print(f"  Margen actual Sánchez − RLA: {margen:+,} votos "
          f"({meta['margen_sanch_rla_pct']:+.3f} pts)")
    print(f"  Actas impugnadas (JEE): {jee:,}")
    print(f"  Actas pendientes: {pend:,}")
    print(f"  Votos válidos/acta: {votos_por_acta:.1f}")
    print(f"  Votos en juego: ~{votos_juego:,}")
    print()
    print("  Proyección con distribución proporcional al nacional:")
    print(f"    → RLA ganaría {rla_natural:,.0f}")
    print(f"    → Sánchez ganaría {sanch_natural:,.0f}")
    print(f"    → Margen final: {margen_proyectado:+,.0f} "
          f"(a favor de {'Sánchez' if margen_proyectado > 0 else 'RLA'})")
    print()
    print(f"  Break-even: RLA necesita {pct_rla_break_even:.2f}% de "
          f"RLA+Sánchez en disputa para empatar")
    print(f"  Histórico:  RLA tiene {pct_rla_historico:.2f}% de RLA+Sánchez")
    print(f"  → Requiere sobre-performance de "
          f"{pct_rla_break_even - pct_rla_historico:+.2f}pp vs histórico")

    findings = [{
        "severity": "CRÍTICO",
        "id": "E1",
        "title": "Pase a 2ª vuelta depende de la resolución del JEE",
        "detail": (f"Margen Sánchez−RLA ({margen:+,} votos, "
                   f"{meta['margen_sanch_rla_pct']:+.3f}pp) es aproximadamente "
                   f"{abs(votos_juego/margen):.0f}× menor que los votos contenidos "
                   f"en actas impugnadas + pendientes (~{votos_juego:,}). "
                   f"Bajo distribución proporcional al nacional, el margen final "
                   f"sería {margen_proyectado:+,.0f}. "
                   f"Para empatar, RLA requiere {pct_rla_break_even:.2f}% del "
                   f"subgrupo RLA+Sánchez en disputa "
                   f"(vs {pct_rla_historico:.2f}% histórico)."),
    }]

    return {
        "findings": findings,
        "margen_actual": margen,
        "votos_juego": votos_juego,
        "margen_proyectado": margen_proyectado,
        "break_even_pct_rla": pct_rla_break_even,
        "historico_pct_rla": pct_rla_historico,
    }


if __name__ == "__main__":
    run()
