from dataclasses import dataclass
from model.dataclass_estacion import Estacion, PisoConfig
from helpers.estados import OrientacionMagazine, OrientacionesPermitidasAmr, OrientacionAmr, FlujoEstado


# noinspection SpellCheckingInspection
class EstacionPisoConfig:
    def __init__(self, estacion: Estacion, piso: PisoConfig):
        self.estacion = estacion
        self.piso = piso
        self.tipo = piso.tipo
        self.alias = piso.alias
        self.altura = piso.altura
        self.recibe = piso.recibe
        self.entregar = piso.entregar
        self.recibe_de = piso.recibe_de
        self.tipo_recibo = piso.tipo_recibo
        self.tipo_entrega = piso.tipo_entrega
        self.orientacion_magazine = OrientacionMagazine.get_orientacion_from_string(piso.orientacion_magazine)
        self.orientaciones_permitidas_amr = OrientacionesPermitidasAmr(piso.orientacion_permitida_amr)

    estacion: Estacion
    tipo: str
    alias: str
    altura: int
    recibe: bool
    entregar: bool
    tipo_recibo: str
    tipo_entrega: str
    orientacion_magazine: OrientacionMagazine = OrientacionMagazine.DESCONOCIDO
    orientaciones_permitidas_amr: OrientacionesPermitidasAmr = OrientacionesPermitidasAmr('')
    recibe_de: list[str] = '' # type: ignore


    def __hash__(self):
        return hash(self.alias)

    def __eq__(self, other):
        if not isinstance(other, EstacionPisoConfig):
            return False
        return self.alias == other.alias

# noinspection SpellCheckingInspection
class SolucionDeGiro:

    def __init__(self, orientacion_amr_origen: OrientacionAmr, orientacion_amr_destino: OrientacionAmr):
        self.orientacion_amr_origen = orientacion_amr_origen
        self.orientacion_amr_destino = orientacion_amr_destino

    orientacion_amr_origen: OrientacionAmr
    orientacion_amr_destino: OrientacionAmr

# noinspection SpellCheckingInspection
@dataclass
class FlujoPiso:
    estacion_origen: EstacionPisoConfig
    estacion_destino: EstacionPisoConfig
    solucion_de_giro: SolucionDeGiro
    flujo_estado: FlujoEstado

    def get_alias(self):
        alias = self.estacion_origen.alias + ' -> ' + self.estacion_destino.alias
        return alias

    def __hash__(self):
        return hash((self.estacion_origen.alias, self.estacion_destino.alias))

    def __eq__(self, other):
        if not isinstance(other, FlujoPiso):
            return False
        return (self.estacion_origen.alias == other.estacion_origen.alias and
                self.estacion_destino.alias == other.estacion_destino.alias)