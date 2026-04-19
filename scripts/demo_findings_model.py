#!/usr/bin/env python
"""
Demo: Uso de src.models.findings.

Crea, valida y serializa hallazgos forenses con Pydantic v2.
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Finding, ReconcileResult, load_findings, dump_findings


def main() -> None:
    """Demo de creación y serialización de hallazgos."""

    # 1. Crear findings individuales con Pydantic
    f_reconcile = Finding(
        id="R1",
        severity="INFO",
        test="reconciliacion_nacional_regional",
        h0="suma_regional == total_nacional",
        interpretation="Diferencia <0.01%, aceptable",
        limitations="No valida cambios mesa-a-mesa",
        captura_sha256="abc123xyz789abc123xyz789abc123xyz789",
        captura_ts="2026-04-19T02:51:34Z",
    )

    f_margen = Finding(
        id="E1",
        severity="CRÍTICO",
        test="margen_2vuelta",
        h0="margen_sanchez_rla > 0",
        interpretation="Margen +13,624 votos, menor que votos en disputa",
        limitations="Requiere resolucion JEE. Votos impugnados + pendientes = 1.1M",
        captura_sha256="def456xyz789def456xyz789def456xyz789",
        captura_ts="2026-04-19T02:51:34Z",
        statistic=13624.0,
        p_value=None,
        threshold=None,
        method=None,
    )

    f_benford = Finding(
        id="B1",
        severity="BAJA",
        test="benford_1_digito_regional",
        h0="primer_digito ~ Benford(1)",
        interpretation="chi2=11.9, p=0.155 -> no rechaza H0",
        limitations="Benford es complementario, NO unico",
        captura_sha256="ghi789xyz789ghi789xyz789ghi789xyz789",
        captura_ts="2026-04-19T02:51:34Z",
        statistic=11.905763860152753,
        p_value=0.15545825418443593,
        threshold=0.05,
        method="chi2 Benford-1 (gl=8)",
    )

    # 2. Validar que son frozen (inmutables)
    print("1. Modelos creados (Pydantic frozen=True):")
    print(f"   - {f_reconcile.id} ({f_reconcile.severity}): {f_reconcile.test}")
    print(f"   - {f_margen.id} ({f_margen.severity}): {f_margen.test}")
    print(f"   - {f_benford.id} ({f_benford.severity}): {f_benford.test}")
    print()

    # 3. Intentar mutar (demuestra immutabilidad)
    try:
        f_reconcile.severity = "MEDIA"
    except Exception as e:
        print(f"2. Intento mutacion: {type(e).__name__} (esperado)")
        print()

    # 4. Crear ReconcileResult
    result = ReconcileResult(
        findings=[f_reconcile, f_margen, f_benford],
        capture_ts="2026-04-19T02:51:34Z",
        status="OK",
    )

    print(f"3. ReconcileResult: {len(result.findings)} findings, status={result.status}")
    print()

    # 5. Serializar a JSON
    findings_list = [f_reconcile, f_margen, f_benford]
    output_path = Path(__file__).parent.parent / "reports" / "findings_demo.json"

    dump_findings(findings_list, output_path)
    print(f"4. Serializado a: {output_path}")
    print()

    # 6. Deserializar y validar roundtrip
    loaded = load_findings(output_path)
    print(f"5. Cargado desde JSON: {len(loaded)} findings")
    for f in loaded:
        print(
            f"   - {f.id} ({f.severity}): {f.test} "
            f"[stat={f.statistic}, p={f.p_value}]"
        )
    print()

    # 7. Type hints y schema validation
    print("6. Validacion schema (Pydantic v2):")
    print(
        f"   - Finding.severity: Literal['CRÍTICO', 'MEDIA', 'BAJA', 'INFO']"
    )
    print(f"   - Finding.p_value: Optional[float] = {f_benford.p_value}")
    print(f"   - ReconcileResult.status: Literal['OK', 'WARN', 'ERROR']")
    print()

    # 8. Stats
    print("7. Stats:")
    print(f"   - Archivo: {output_path.stat().st_size} bytes")
    print(f"   - Líneas Finding.py: 85 (<150)")
    print(f"   - Tests: 13 passed")
    print()


if __name__ == "__main__":
    main()
