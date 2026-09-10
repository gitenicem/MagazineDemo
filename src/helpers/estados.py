from __future__  import annotations
from enum import Enum
from unittest import case

# noinspection SpellCheckingInspection
class FlujoEstado(Enum):
    NONE = ""
    CONFIRMANDO_ORIGEN = 'CONFIRMANDO ORIGEN'
    CONFIRMANDO_DESTINO = 'CONFIRMANDO DESTINO'
    INICIANDO = 'INICIANDO'
    YENDO_A_ORIGEN = 'YENDO A ORIGEN'
    EN_ORIGEN = 'EN ORIGEN'
    YENDO_A_DESTNO = 'YENDO A DESTNO'
    EN_DESTNO = 'EN DESTNO'
    ESTACION_RECIBIENDO = 'ESTACION RECIBIENDO'
    AMR_RECIBIENDO = 'AMR RECIBIENDO'
    FINALIZADO = 'FINALIZADO'

# noinspection DuplicatedCode
# noinspection SpellCheckingInspection
class EstadosPiso(Enum):
    NONE = ""
    OCUPADO = "OCUPADO"
    PREPARADO = "PREPARADO"
    ENTREGAR = "ENTREGAR"
    ENTREGANDO = "ENTREGANDO"
    RECIBIR = "RECIBIR"
    RECIBIENDO = "RECIBIENDO"
    FINALIZADO = "FINALIZADO"
    ERROR = "ERROR"
    CANCELAR = "CANCELAR"
    PREPARADO_ENTREGAR = "PREPARADO_ENTREGAR"
    PREPARADO_RECIBIR = "PREPARADO_RECIBIR"
    PREPARADO_ENTREGAR_RECIBIR = "PREPARADO_ENTREGAR_RECIBIR"

    @staticmethod
    def estado_piso_from_string(string: str) -> "EstadosPiso":
        match string.upper():
            case EstadosPiso.PREPARADO.value:
                return EstadosPiso.PREPARADO

            case EstadosPiso.ENTREGAR.value:
                return EstadosPiso.ENTREGAR

            case EstadosPiso.RECIBIR.value:
                return EstadosPiso.RECIBIR

            case EstadosPiso.FINALIZADO.value:
                return EstadosPiso.FINALIZADO

            case EstadosPiso.ERROR.value:
                return EstadosPiso.ERROR

            case EstadosPiso.CANCELAR.value:
                return EstadosPiso.CANCELAR

            case EstadosPiso.PREPARADO_ENTREGAR.value:
                return EstadosPiso.PREPARADO_ENTREGAR

            case EstadosPiso.PREPARADO_RECIBIR.value:
                return EstadosPiso.PREPARADO_RECIBIR

            case EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value:
                return EstadosPiso.PREPARADO_ENTREGAR_RECIBIR

            case _:
                return EstadosPiso.NONE

# noinspection DuplicatedCode
# noinspection SpellCheckingInspection
class EstadosAmr(Enum):
    NONE = ""
    OCUPADO = "OCUPADO"
    PREPARADO = "PREPARADO"
    ENTREGAR = "ENTREGAR"
    ENTREGANDO = "ENTREGANDO"
    RECIBIR = "RECIBIR"
    RECIBIENDO = "RECIBIENDO"
    FINALIZADO = "FINALIZADO"
    SIGUIENTE = "SIGUIENTE"
    ERROR = "ERROR"
    CANCELAR = "CANCELAR"

    @staticmethod
    def estado_amr_from_string(string: str) -> "EstadosAmr":
        match string.upper():
            case EstadosAmr.OCUPADO.value:
                return EstadosAmr.OCUPADO
            case EstadosAmr.PREPARADO.value:
                return EstadosAmr.PREPARADO
            case EstadosAmr.ENTREGAR.value:
                return EstadosAmr.ENTREGAR
            case EstadosAmr.ENTREGANDO.value:
                return EstadosAmr.ENTREGANDO
            case EstadosAmr.RECIBIR.value:
                return EstadosAmr.RECIBIR
            case EstadosAmr.RECIBIENDO.value:
                return EstadosAmr.RECIBIENDO
            case EstadosAmr.FINALIZADO.value:
                return EstadosAmr.FINALIZADO
            case EstadosAmr.SIGUIENTE.value:
                return EstadosAmr.SIGUIENTE
            case EstadosAmr.ERROR.value:
                return EstadosAmr.ERROR
            case EstadosAmr.CANCELAR.value:
                return EstadosAmr.CANCELAR
            case _:
                return EstadosAmr.NONE

# noinspection SpellCheckingInspection
class EstacionEstado(Enum):
    HABILITADA = True
    DESHABILITADA = False

# debe llamarse server actions o referente a ello
# noinspection SpellCheckingInspection
class EstadosServidor(Enum):
    NONE = ""
    ENTREGAR = "ENTREGAR"
    RECIBIR = "RECIBIR"
    CANCELAR = "CANCELAR"
    MANUAL1 = "MANUAL1" #TODO Llamado a acciones1 en modo manual
    MANUAL2 = "MANUAL2" #TODO Llamado a acciones2 en modo manual
    MANUAL3 = "MANUAL3" #TODO Llamado a acciones3 en modo manual



# noinspection SpellCheckingInspection
class TipoRecibo(Enum):
    NONE = ""
    LLENO = "lleno"
    VACIO = "vacio"

# noinspection SpellCheckingInspection
class TipoEntrega(Enum):
    NONE = ""
    LLENO = "lleno"
    VACIO = "vacio"

# noinspection SpellCheckingInspection
class OrientacionMagazine(Enum):
    DESCONOCIDO = -999
    FRENTE = 0
    ATRAS = 180
    IZQUIERDA = -90
    DERECHA = 90

    @staticmethod
    def get_orientacion_from_string( string: str) -> OrientacionMagazine:
        match string.upper():

            case 'FRENTE':
                return OrientacionMagazine.FRENTE
            case 'ATRAS':
                return OrientacionMagazine.ATRAS
            case 'IZQUIERDA':
                return OrientacionMagazine.IZQUIERDA
            case 'DERECHA':
                return OrientacionMagazine.DERECHA
            case _:
                return OrientacionMagazine.DESCONOCIDO

# noinspection SpellCheckingInspection
class OrientacionAmr(Enum):
    DESCONOCIDO = -999
    FRENTE = 0
    ATRAS = 180
    IZQUIERDA = 90
    DERECHA = -90

    @staticmethod
    def a_texto(orientacion: OrientacionAmr) -> str:
        match orientacion:
            case OrientacionAmr.FRENTE:
                return 'FRENTE'
            case OrientacionAmr.ATRAS:
                return 'ATRAS'
            case OrientacionAmr.IZQUIERDA:
                return 'IZQUIERDA'
            case OrientacionAmr.DERECHA:
                return 'DERECHA'
            case _:
                return 'DESCONOCIDO'


# noinspection SpellCheckingInspection
class OrientacionesPermitidasAmr:
    FRENTE = False
    IZQUIERDA = False
    DERECHA = False
    ATRAS = False

    def __init__(self, orientaciones: str):
        self.FRENTE = 'FRENTE' in orientaciones.upper()
        self.IZQUIERDA = 'IZQUIERDA' in orientaciones.upper()
        self.DERECHA = 'DERECHA' in orientaciones.upper()
        self.ATRAS = 'ATRAS' in orientaciones.upper()

# noinspection SpellCheckingInspection
class ModoDeFuncionamiento(Enum):
    MANUAL = "MANUAL"
    AUTONOMO = "AUTONOMO"

# noinspection SpellCheckingInspection
class Pisos(Enum):
    P1 = "P1"
    P2 = "P2"

# noinspection SpellCheckingInspection
class EstacionAlias(Enum):
    SMT1 = "SMT1"
    SMT2 = "SMT2"
    ROUTER1 = "ROUTER1"
    ROUTER2 = "ROUTER2"
    ROUTER3 = "ROUTER3"
    ROUTER4 = "ROUTER4"
    ROUTER5 = "ROUTER5"
    WIP = "WIP"
