"""Pydantic models para mesa ONPE con invariantes contables."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

TOLERANCIA_SUMA = 2  # diferencia Σdetalle vs totalVotosEmitidos


class Detalle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    adAgrupacionPolitica: int
    adCodigo: str
    adDescripcion: str
    adVotos: int | None = Field(default=None, ge=0)
    adTotalVotosValidos: int | None = Field(default=None, ge=0)


class MesaRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigoMesa: str
    idUbigeo: int
    idEleccion: int
    totalElectoresHabiles: int | None = Field(default=None, ge=0)
    totalVotosEmitidos: int | None = Field(default=None, ge=0)
    totalVotosValidos: int | None = Field(default=None, ge=0)
    estadoActa: str | None = None
    codigoEstadoActa: str | None = None
    descripcionEstadoActa: str | None = None
    nombreLocalVotacion: str | None = None
    codigoLocalVotacion: str | None = None
    totalAsistentes: int | None = None
    porcentajeParticipacionCiudadana: float | None = None
    detalle: list[Detalle] = Field(default_factory=list)

    @model_validator(mode="after")
    def _invariantes(self) -> "MesaRecord":
        habiles = self.totalElectoresHabiles or 0
        emitidos = self.totalVotosEmitidos or 0
        validos = self.totalVotosValidos or 0
        if emitidos > habiles and habiles > 0:
            raise ValueError(
                f"emitidos({emitidos}) > habiles({habiles})"
            )
        if validos > emitidos and emitidos > 0:
            raise ValueError(
                f"validos({validos}) > emitidos({emitidos})"
            )
        if self.detalle and emitidos > 0:
            suma = sum(d.adVotos or 0 for d in self.detalle)
            if abs(suma - emitidos) > TOLERANCIA_SUMA:
                raise ValueError(
                    f"suma detalle({suma}) != emitidos({emitidos})"
                )
        return self
