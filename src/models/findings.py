"""
Modelos Pydantic para hallazgos forenses del escrutinio ONPE 2026.
Frozen=True para inmutabilidad. Validación schema-first.
"""

from typing import Literal, Optional
from pathlib import Path
import json

from pydantic import BaseModel, ConfigDict

# Definición de severidad permitida
Severity = Literal["CRÍTICO", "MEDIA", "BAJA", "INFO"]


class Finding(BaseModel):
    """Hallazgo individual con contexto metodológico y trazabilidad."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str  # ej: "A0", "F2", "E1"
    severity: Severity
    test: str  # nombre del test/análisis que lo generó
    h0: str  # hipótesis nula explícita
    interpretation: str  # interpretación técnica del resultado
    limitations: str  # limitaciones conocidas del test
    captura_sha256: str  # SHA-256 del archivo fuente (MANIFEST)
    captura_ts: str  # timestamp ISO 8601 de la captura
    statistic: Optional[float] = None  # valor del estadístico (χ², z, r, etc)
    p_value: Optional[float] = None  # p-valor del test
    threshold: Optional[float] = None  # umbral de significancia usado (ej: 0.05)
    method: Optional[str] = None  # nombre del método/test (ej: "χ² Benford-1")


class ReconcileResult(BaseModel):
    """Resultado de reconciliación con trazabilidad de captura."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    findings: list[Finding]
    capture_ts: str  # timestamp ISO 8601 de la captura
    status: Literal["OK", "WARN", "ERROR"]  # estado general de reconciliación


def load_findings(path: Path) -> list[Finding]:
    """
    Carga hallazgos desde archivo JSON.

    Args:
        path: ruta a findings.json

    Returns:
        Lista de Finding validados con Pydantic

    Raises:
        FileNotFoundError: si el archivo no existe
        json.JSONDecodeError: si JSON es inválido
        ValueError: si algún Finding no valida
    """
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    findings_raw = data.get("findings", [])
    return [Finding(**item) for item in findings_raw]


def dump_findings(findings: list[Finding], path: Path) -> None:
    """
    Serializa lista de Finding a JSON.

    Args:
        findings: lista de Finding
        path: ruta de salida (se sobrescribe si existe)
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "findings": [f.model_dump(mode="json") for f in findings],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
