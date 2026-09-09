import threading
from threading import Lock

from helpers.amr import AMR
from model.dataclass_amr import AmrConfig, AMRs
from config.db_config import db_config
from model.conexion import DAO


class AmrsController:
    amrs: list[AMR] = []
    version = 1
    __conexion: DAO | None = None
    __candado = Lock()
    _tiene_error = False
    _thread_check: threading.Timer | None = None

    @classmethod
    def _get_conexion(cls) -> DAO:
        if cls.__conexion is None:
            cls.__conexion = DAO(db_config)
        return cls.__conexion

    @classmethod
    def revisar_version(cls, table: str, version_var) -> tuple[bool, int]:
        query = f"SELECT version FROM {table} WHERE id = 1"
        [res] = cls._get_conexion().execute_query(query)
        version = res.get("version")
        if version != version_var:
            return True, version # type: ignore
        else:
            return False, version_var

    @classmethod
    def _revisar_amr_config_version(cls):
        actualizado, version = cls.revisar_version("amr_connection_version", cls.version)
        cls.version = version
        return actualizado

    @classmethod
    def start_timer(cls):
        cls._thread_check = threading.Timer(1.0, cls.update_amrs_connections)
        cls._thread_check.daemon = True
        cls._thread_check.start()

    @classmethod
    def update_amrs_connections(cls):
        if cls._revisar_amr_config_version():
            cls.iniciar()  # _iniciar reagenda el timer
        else:
            cls.start_timer()

    @staticmethod
    def iniciar():
        AmrsController._iniciar()

    @staticmethod
    def send(amr_alias: str, message: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            if amr.is_connected():
                amr.send(message)
            else:
                print("",f"[{amr_alias}] desconectado, No se puede enviar el mensaje")

    @staticmethod
    def get_amr_status(amr_alias: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send("status")

    @staticmethod
    def get_amr_status_socket(amr_alias: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        return amr.estado_amr.estado.Status # type: ignore

    @staticmethod
    def get_amr_usando_alias(alias: str) -> AMR | None:
        for amr in AmrsController.amrs:
            if amr.alias == alias:
                return amr
        return None

    @staticmethod
    def enviar_amr_a_objetivo(amr_alias: str, objetivo: str):
        #print(f"{amr_alias} -> {objetivo}")
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send(f"goto {objetivo}")

    @staticmethod
    def enviar_amr_a_estacion_origen(amr_alias: str, objetivo):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        amr.objetivo = objetivo # type: ignore
        if amr:
            amr.send(f"queuepickup {objetivo}") # Parametros opcionales [prioridad] [id]

    @staticmethod
    def enviar_amr_a_estacion_destino(amr_alias: str, objetivo):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        amr.objetivo = objetivo # type: ignore
        if amr:
            amr.send(f"queuedropoff {objetivo}") # Parametros opcionales [prioridad] [id]

    @staticmethod
    def enviar_amr_a_objetivo_seguro(amr_alias: str, objetivo):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send(f"goto {objetivo}")

    @staticmethod
    def obtener_objetivo_seguro(estacion: str):
        return AMR.obtener_objetivo_seguro(estacion) # type: ignore

    @staticmethod
    def enviar_amr_a_ruta(amr_alias: str, ruta: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send(f'goto {ruta}')

    @staticmethod
    def acoplar_amr_en_estacion_de_carga(amr_alias: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send('dock')

    @staticmethod
    def desacoplar_amr_de_estacion_de_carga(amr_alias: str):
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        if amr:
            amr.send('undock')

    @staticmethod
    def get_message(amr_alias: str) -> str:
        amr = AmrsController.get_amr_usando_alias(amr_alias)
        return amr.get_message() if amr else ""

    @classmethod
    def get_amr_config(cls):
        with cls.__candado:
            try:
                amr_config = {}
                query = "SELECT * FROM amr_config"
                res = cls._get_conexion().execute_query(query)
                if res:
                    amr_config = [AmrConfig(**row) for row in res]
                return amr_config
            except Exception as e:
                raise Exception(f"Error al parsear configuracion: {e}")

    # ------------------------------------------------------------------ #
    # METODOS protejidos
    # ------------------------------------------------------------------ #
    @classmethod
    def _iniciar(cls):
        cls._clear_amrs()
        AMRs[:] = cls.get_amr_config()
        for amr in AMRs:
            nuevo_amr = AMR(amr)
            nuevo_amr.connect()
            AmrsController.amrs.append(nuevo_amr)
        cls.start_timer()

    @classmethod
    def _clear_amrs(cls):
        print("",f"Limpiando amrs")
        for amr in AmrsController.amrs:
            print("",f"Desconectando {amr.alias}")
            amr.disconnect()
        cls.amrs.clear()

    @staticmethod
    def _error_on(e: Exception):
        #todo agregar log del la Exception
        AmrsController._tiene_error = True

    @staticmethod
    def _error_off():
        AmrsController._tiene_error = False

    @staticmethod
    def tiene_error():
        return AmrsController._tiene_error


