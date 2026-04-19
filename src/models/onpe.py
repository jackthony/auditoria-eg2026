from pydantic import BaseModel, ConfigDict
from typing import Any, Generic, TypeVar, Optional, Union

T = TypeVar("T")


class _FrozenMixin(BaseModel):
    """Mixin que convierte ValidationError de frozen en TypeError para compatibilidad."""

    def __setattr__(self, name: str, value: object) -> None:
        try:
            super().__setattr__(name, value)
        except Exception as exc:
            raise TypeError(str(exc)) from exc


class OnpeResponse(_FrozenMixin, Generic[T]):
    success: bool
    data: T
    message: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class TotalesData(_FrozenMixin):
    actasContabilizadas: float
    contabilizadas: int
    totalActas: int
    participacionCiudadana: float
    actasEnviadasJee: float
    enviadasJee: int
    actasPendientesJee: float
    pendientesJee: int
    fechaActualizacion: int
    idUbigeoDepartamento: int
    idUbigeoProvincia: int
    idUbigeoDistrito: int
    idUbigeoDistritoElectoral: int
    totalVotosEmitidos: int
    totalVotosValidos: int
    porcentajeVotosEmitidos: float
    porcentajeVotosValidos: float

    model_config = ConfigDict(frozen=True, extra="ignore")


class PresidencialItem(_FrozenMixin):
    nombreAgrupacionPolitica: str
    codigoAgrupacionPolitica: str
    nombreCandidato: str
    dniCandidato: str
    totalVotosValidos: int
    porcentajeVotosValidos: Optional[float] = None
    porcentajeVotosEmitidos: Optional[float] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class MapaCalorItem(_FrozenMixin):
    ambitoGeografico: Optional[str] = None
    ubigeoNivel01: Optional[str] = None
    ubigeoNivel02: Optional[str] = None
    ubigeoNivel03: Optional[str] = None
    distritoElectoral: Optional[str] = None
    porcentajeActasContabilizadas: float
    actasContabilizadas: int

    model_config = ConfigDict(frozen=True, extra="ignore")


class ResumenEleccionItem(_FrozenMixin):
    id: int
    nombre: str
    totalElectoresHabiles: Optional[int] = None
    participacionCiudadana: Optional[float] = None
    porcentajeParticipacionCiudadana: Optional[float] = None
    totalActas: Optional[int] = None
    actasContabilizadas: int
    porcentajeActasContabilizadas: float
    actasObservadasEnviadas: int
    porcentajeActasObservadasEnviadas: float
    actasPendientes: int
    porcentajeActasPendientes: float
    ubigeoNivel01: Optional[str] = None
    ubigeoNivel02: Optional[str] = None
    ubigeoNivel03: Optional[str] = None
    ubigeoDesc: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class MesaTotales(_FrozenMixin):
    mesasInstaladas: int
    mesasNoInstaladas: int
    mesasPendientes: int

    model_config = ConfigDict(frozen=True, extra="ignore")


class ProcesoActivo(_FrozenMixin):
    id: int
    nombre: str
    acronimo: str
    fechaProceso: Union[str, int]
    idEleccionPrincipal: int
    tipoProcesoElectoral: str
    activoFechaProceso: bool

    model_config = ConfigDict(frozen=True, extra="ignore")


class EleccionItem(_FrozenMixin):
    id: int
    nombre: str
    padre: Optional[int] = None
    hijos: Optional[Any] = None
    icono: Optional[str] = None
    orden: int
    idEleccion: int
    url: Optional[str] = None
    esPrincipal: bool
    descripcion: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class UbigeoItem(_FrozenMixin):
    ubigeo: str
    nombre: str

    model_config = ConfigDict(frozen=True, extra="ignore")
