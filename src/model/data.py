import json
from dataclasses import asdict
from threading import Lock
from datetime import datetime

from helpers.bcript import is_hashed, check_password, hash_password
from helpers.crypto import encrypt_password, decrypt_password, is_encrypt_password

#import bcrypt

from model.conexion import DAO
from config.db_config import db_config
from model.dataclass_amr import AmrConfig
from model.dataclass_estacion import Estacion, PisosEstado, PisosConfig, Detectadas, PisoConfig, ManagerConfig, \
    EstacionConfig


class DataAccess:
    __conexion = None
    __candado = None
    __estaciones_version = 0
    __amr_config_version = 0
    __estaciones_detectadas_version = 0
    __manager_config_version = 0
    __estaciones_config_version = 0

    def __init__(self):
        DataAccess.__candado = Lock()
        if DataAccess.__conexion is None:
            DataAccess.__conexion = DAO(db_config)

    # noinspection PyTypeChecker
    # noinspection SpellCheckingInspection
    @staticmethod
    def get_estaciones():
        with DataAccess.__candado: # type: ignore

            estaciones: list[Estacion] = []


            query = "SELECT * FROM estaciones"
            res = DataAccess.__conexion.execute_query(query) # type: ignore

            if res:
                estaciones = [Estacion(**row) for row in res]

            try:
                # Parseo de string a dict
                for estacion in estaciones:
                    estacion.pisos_estado = PisosEstado(estacion.pisos_estado) # type: ignore
                    estacion.servidor_acciones = json.loads((estacion.servidor_acciones or '{}').strip()) # type: ignore
                    estacion.amr_estado = json.loads((estacion.amr_estado or '{}').strip()) # type: ignore
                    estacion.coordenadas = json.loads((estacion.coordenadas or '{}').strip()) # type: ignore
                    estacion.pisos_configuracion = PisosConfig(estacion.pisos_configuracion) # type: ignore

            except Exception as e:
                raise Exception(f"Error al parsear estaciones: {e}")
            return estaciones

    # noinspection SpellCheckingInspection
    @staticmethod
    def get_estaciones_detectadas():
        with DataAccess.__candado: # type: ignore
            try:
                estaciones: list[Detectadas] = []
                query = "SELECT * FROM estaciones_detectadas"
                res = DataAccess.__conexion.execute_query(query) # type: ignore
                if res:
                    estaciones = [Detectadas(**row) for row in res]
                return estaciones
            except Exception as e:
                raise Exception(f"Error al parsear estaciones detectadas: {e}")


    @staticmethod
    def get_pisos_config() -> PisosConfig:
        # ESTO SI OBTIENE DATA DIRECTO DE LA BASE DE DATOS
        estaciones = DataAccess.get_estaciones()
        config = {}
        for estacion in estaciones:
            if estacion.alias == "WIP1":
                config = estacion.pisos_configuracion
        return config # pyright: ignore[reportReturnType]


    @staticmethod
    def save_pisos_config(configuracion: str) -> int:
        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET pisos_configuracion = %s WHERE alias = 'WIP1'"
            res = DataAccess.__conexion.execute_commit(query, (configuracion, )) # type: ignore
            return res

    @staticmethod
    def get_amr_config() -> list[AmrConfig]:
        with DataAccess.__candado: # type: ignore
            try:
                amr_config = {}
                query = "SELECT * FROM amr_config"
                res = DataAccess.__conexion.execute_query(query) # type: ignore
                if res:
                    amr_config = [AmrConfig(**row) for row in res]
                return amr_config # type: ignore
            except Exception as e:
                raise Exception(f"Error al parsear configuracion: {e}")

    @staticmethod
    def get_ultima_modificacion(alias:str) -> int:
        with DataAccess.__candado: # type: ignore
            query = "SELECT ultima_modificacion, TIMESTAMPDIFF(SECOND, ultima_modificacion, NOW()) AS segundos FROM estaciones WHERE alias = %s"
            [res] = DataAccess.__conexion.execute_query(query, (alias,)) # type: ignore
            res = res.get("segundos")
            return res # type: ignore



    @staticmethod
    def delete_amr_config(alias: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "DELETE FROM amr_config WHERE alias = %s"
            res = DataAccess.__conexion.execute_commit(query, (alias.strip().upper(),)) # type: ignore
            return bool(res)

    @staticmethod
    def save_amr_ip_puerto(alias: str, ip: str, port: int, password: str = ""):
        with DataAccess.__candado: # type: ignore
            cfg_alias = alias.strip().upper()
            cfg_ip = ip.strip()
            cfg_port = port
            cfg_password = password.strip()
            existe = DataAccess.__conexion.execute_query( # type: ignore
                "SELECT id FROM amr_config WHERE alias = %s", (cfg_alias,)
            )
            if existe:
                res = DataAccess.__conexion.execute_commit( # type: ignore
                    "UPDATE amr_config SET ip = %s, puerto = %s, password = %s WHERE alias = %s",
                    (cfg_ip, cfg_port, cfg_password, cfg_alias)
                )
                return bool(res)
            else:
                res = DataAccess.__conexion.execute_commit( # type: ignore
                    "INSERT INTO amr_config (alias, status, ip, puerto, password, config) VALUES (%s, %s, %s, %s, %s, %s)",
                    (cfg_alias, "", cfg_ip, cfg_port, cfg_password, "")
                )
                return bool(res)

    @staticmethod
    def set_servidor_acciones_entregar(piso: str, estacion: Estacion) -> bool:
        value = {piso:'ENTREGAR'}

        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET servidor_acciones = %s WHERE alias = 'WIP1' "
            params = (json.dumps(value),)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)


    @staticmethod
    def set_servidor_acciones_recibir(piso: str, estacion: Estacion) -> bool:
        value = {piso:'RECIBIR'}

        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET servidor_acciones = %s WHERE alias = 'WIP1' "
            params = (json.dumps(value),)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

    @staticmethod
    def limpiar_servidor_acciones():

        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET servidor_acciones = %s WHERE alias = 'WIP1' "
            params = ("",)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)


    @staticmethod
    def enviar_orden_amr_entrega(piso:str):
        value = {'P1':'','P2':''}
        value[f"{piso}"] = "RECIBIR"
        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET smema = %s WHERE alias = 'WIP1' "
            params = (json.dumps(value),)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            print(f"Ejecutada orden ENTREGAR AMR en {piso}")
            return bool(res)

    @staticmethod
    def enviar_orden_amr_recibe(piso:str):
        value = {'P1':'','P2':''}
        value[f"{piso}"] = "ENTREGAR"
        with DataAccess.__candado: # type: ignore
            query = "UPDATE estaciones SET smema = %s WHERE alias = 'WIP1' "
            params = (json.dumps(value),)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            print(f"Ejecutada orden RECIBIR AMR en {piso}")
            return bool(res)

    @staticmethod
    def limpiar_orden_amr():
        value = {'P1':'','P2':''}
        with DataAccess.__candado: # type: ignore 
            query = "UPDATE estaciones SET smema = %s WHERE alias = 'WIP1' "
            params = (json.dumps(value),)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            print("Ejecutada orden limpieza AMR")
            return bool(res) 


    @staticmethod
    def save_amr_config(alias: str, config: str):
        with DataAccess.__candado: # type: ignore
            alias_upper = alias.strip().upper()
            config_val = config.strip()
            existe = DataAccess.__conexion.execute_query( # type: ignore
                "SELECT id FROM amr_config WHERE alias = %s", (alias_upper,)
            )
            if existe:
                res = DataAccess.__conexion.execute_commit( # type: ignore
                    "UPDATE amr_config SET config = %s WHERE alias = %s",
                    (config_val, alias_upper)
                )
                return bool(res)
            else:
                res = DataAccess.__conexion.execute_commit( # type: ignore
                    "INSERT INTO amr_config (alias, status, config) VALUES (%s, %s, %s)",
                    (alias_upper,"",config_val)
                )
                return bool(res)

    # noinspection SpellCheckingInspection
    @staticmethod
    def update_estacion(estacion: dict) -> dict:
        with DataAccess.__candado: # type: ignore
            try:
                alias = estacion.get("alias")

                existe = DataAccess.__conexion.execute_query( # type: ignore
                    "SELECT id FROM estaciones WHERE alias = %s", (alias,)
                )

                if not existe:
                    query = """
                        INSERT INTO estaciones (alias, mac, smema, pisos_estado, servidor_acciones, amr_estado,
                                                tipo, habilitado, modo_operacion, recibe, coordenadas,
                                                pisos_configuracion, ultima_modificacion)
                        VALUES (%s, %s, %s, '{"P1": "", "P2": ""}', NULL, NULL, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        alias,
                        estacion.get("mac", "00:00:00:00:00"),
                        estacion.get("smema", ""),
                        estacion.get("tipo", ""),
                        estacion.get("habilitado", False),
                        estacion.get("modo_operacion", "Automatico"),
                        estacion.get("recibe", ""),
                        json.dumps(estacion.get("coordenadas", {}), ensure_ascii=False),
                        json.dumps(estacion.get("pisos_configuracion", {}), ensure_ascii=False),
                        estacion.get("ultima_modificacion"),
                    )
                else:
                    query = """
                        UPDATE estaciones SET
                            alias = %s,
                            mac = %s,
                            smema = %s,
                            tipo = %s,
                            habilitado = %s,
                            modo_operacion = %s,
                            recibe = %s,
                            coordenadas = %s,
                            pisos_configuracion = %s,
                            ultima_modificacion = %s
                        WHERE alias = %s
                    """
                    params = (
                        alias,
                        estacion.get("mac"),
                        estacion.get("smema"),
                        estacion.get("tipo"),
                        estacion.get("habilitado"),
                        estacion.get("modo_operacion"),
                        estacion.get("recibe"),
                        json.dumps(estacion.get("coordenadas", {}), ensure_ascii=False),
                        json.dumps(estacion.get("pisos_configuracion", {}), ensure_ascii=False),
                        estacion.get("ultima_modificacion"),
                        alias,
                    )

                rows = DataAccess.__conexion.execute_commit(query, params) # type: ignore
                return {"status": "ok", "rows": rows}
            except Exception as e:
                return {"status": "error", "error": str(e)}


    def revisar_version(self, table: str, version_var) -> tuple[bool,int]:
        with DataAccess.__candado: # type: ignore
            query = f"SELECT version FROM {table} WHERE id = 1"
            [res] = DataAccess.__conexion.execute_query(query) # type: ignore
            version = res.get("version")
            if version > version_var:
                return True, version # type: ignore
            else:
                return False, version_var

