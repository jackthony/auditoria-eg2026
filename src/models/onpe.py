from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class OnpeResponse(BaseModel, Generic[T]):
    success: bool
    data: T
    message: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class TotalesData(BaseModel):
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


class PresidencialItem(BaseModel):
    nombreAgrupacionPolitica: str
    codigoAgrupacionPolitica: str
    nombreCandidato: str
    dniCandidato: str
    totalVotosValidos: int
    porcentajeVotosValidos: float
    porcentajeVotosEmitidos: float

    model_config = ConfigDict(frozen=True, extra="ignore")


class MapaCalorItem(BaseModel):
    ambitoGeografico: Optional[str] = None
    ubigeoNivel01: Optional[str] = None
    ubigeoNivel02: Optional[str] = None
    ubigeoNivel03: Optional[str] = None
    distritoElectoral: Optional[str] = None
    porcentajeActasContabilizadas: float
    actasContabilizadas: int

    model_config = ConfigDict(frozen=True, extra="ignore")


class ResumenEleccionItem(BaseModel):
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


class MesaTotales(BaseModel):
    mesasInstaladas: int
    mesasNoInstaladas: int
    mesasPendientes: int

    model_config = ConfigDict(frozen=True, extra="ignore")


class ProcesoActivo(BaseModel):
    id: int
    nombre: str
    acronimo: str
    fechaProceso: str
    idEleccionPrincipal: int
    tipoProcesoElectoral: str
    activoFechaProceso: bool

    model_config = ConfigDict(frozen=True, extra="ignore")


class EleccionItem(BaseModel):
    id: int
    nombre: str
    padre: Optional[int] = None
    hijos: Optional[list] = None
    icono: Optional[str] = None
    orden: int
    idEleccion: int
    url: Optional[str] = None
    esPrincipal: bool
    descripcion: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class UbigeoItem(BaseModel):
    ubigeo: str
    nombre: str

    model_config = ConfigDict(frozen=True, extra="ignore")
