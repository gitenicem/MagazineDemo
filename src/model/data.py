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
    def get_manager_config() -> list[ManagerConfig]:
        with DataAccess.__candado: # type: ignore
            try:
                config: list[ManagerConfig] = []
                query = "SELECT * FROM manager_config"
                res = DataAccess.__conexion.execute_query(query) # type: ignore
                if res:
                    config = [ManagerConfig(**row) for row in res]
                return config
            except Exception as e:
                raise Exception(f"Error al parsear configuracion: {e}")

    @staticmethod
    def get_estaciones_config() -> list[EstacionConfig]:
        with DataAccess.__candado: # type: ignore
            try:
                config: list[EstacionConfig] = []
                query = "SELECT * FROM estaciones_config"
                res = DataAccess.__conexion.execute_query(query) # type: ignore
                if res:
                    config = [EstacionConfig(**row) for row in res]
                return config
            except Exception as e:
                raise Exception(f"Error al parsear configuracion: {e}")

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
    def save_estaciones_config(values: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "UPDATE manager_config SET cfg_estaciones = %s WHERE id = 1"
            params = (values,)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

    @staticmethod
    def save_magazines_config(values: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "UPDATE manager_config SET cfg_magazine = %s WHERE id = 1"
            params = (values,)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

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

    def revisar_estaciones_version(self) -> bool:
        actualizado, version = self.revisar_version("estaciones_version", self.__estaciones_version)
        self.__estaciones_version = version
        return actualizado

    def revisar_arm_config_version(self):
        actualizado, version = self.revisar_version("amr_config_version", self.__amr_config_version)
        self.__amr_config_version = version
        return actualizado

    def revisar_estaciones_detectadas_version(self) -> bool:
        actualizado, version = self.revisar_version("estaciones_detectadas_version", self.__estaciones_detectadas_version)
        self.__estaciones_detectadas_version = version
        return actualizado

    def revisar_manager_config_version(self)-> bool:
        actualizado, version = self.revisar_version("manager_config_version", self.__manager_config_version)
        self.__manager_config_version = version
        return actualizado

    def revisar_estaciones_config_version(self) -> bool:
        actualizado, version = self.revisar_version("estaciones_config_version", self.__estaciones_config_version)
        self.__estaciones_config_version = version
        return actualizado

    def revisar_amr_config_version(self) -> bool:
        actualizado, version = self.revisar_version("amr_config_version", self.__amr_config_version)
        self.__amr_config_version = version
        return actualizado

    @staticmethod
    def get_estaciones_tipo():
        with DataAccess.__candado: # type: ignore
            query = "SELECT tipo, recibe FROM estaciones"
            res = DataAccess.__conexion.execute_query(query) # type: ignore
            return res

    def revisar_version(self, table: str, version_var) -> tuple[bool,int]:
        with DataAccess.__candado: # type: ignore
            query = f"SELECT version FROM {table} WHERE id = 1"
            [res] = DataAccess.__conexion.execute_query(query) # type: ignore
            version = res.get("version")
            if version > version_var:
                return True, version # type: ignore
            else:
                return False, version_var

    @staticmethod
    def obtener_usuarios() -> list:
        with DataAccess.__candado: # type: ignore
            query = "SELECT username FROM usuarios"
            res = DataAccess.__conexion.execute_query(query) # type: ignore
            return [r["username"] for r in res] if res else []

    def obtener_flujo(self) -> dict:
        with DataAccess.__candado: # type: ignore
            query = "SELECT * FROM flujos WHERE id = 1"
            [res] = DataAccess.__conexion.execute_query(query) # type: ignore
            return res


    @staticmethod
    def registrar_usuario(username: str, password: str, admin: bool) -> bool:
        password_hash = hash_password(password)

        with DataAccess.__candado: # type: ignore
            query = "INSERT INTO usuarios (username, password_hash, admin) VALUES (%s, %s, %s)"
            params = (username, password_hash, admin) # guardar como string
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            if res:
                return True
            else:
                return False


    @staticmethod
    def actualizar_usuario(username: str, password: str) -> bool:
        password_hash = hash_password(password)
        with DataAccess.__candado: # type: ignore
            query = "UPDATE usuarios SET password_hash = %s WHERE username = %s"
            params = (password_hash, username)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

    @staticmethod
    def actualizar_username(old_username: str, new_username: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "UPDATE usuarios SET username = %s WHERE username = %s"
            params = (new_username, old_username)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

    @staticmethod
    def eliminar_usuario(username: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "DELETE FROM usuarios WHERE username = %s"
            params = (username,)
            res = DataAccess.__conexion.execute_commit(query, params) # type: ignore
            return bool(res)

    @staticmethod
    def verificar_admin(username: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "SELECT admin FROM usuarios WHERE username = %s"
            params = (username,)
            res = DataAccess.__conexion.execute_query(query, params) # type: ignore
            return bool(res[0].get("admin")) if res else False

    @staticmethod
    def \
            verificar_login(username: str, password: str) -> bool:
        with DataAccess.__candado: # type: ignore
            query = "SELECT password_hash FROM usuarios WHERE username = %s"
            params = (username,)
            if username and password:
                res = DataAccess.__conexion.execute_query(query, params) # type: ignore
            else:
                return False

            if not res:
                return False

            hash_guardado_str = res[0].get("password_hash")

            # Verificar que el hash tiene formato bcrypt válido antes de comparar
            if not is_hashed(hash_guardado_str): # type: ignore
                return False

            hash_guardado = hash_guardado_str.encode("utf-8") # type: ignore


            return check_password(password, hash_guardado)



    @staticmethod
    def insertar_estacion(alias: str, mac: str, ip: str) -> dict:
        with DataAccess.__candado: # type: ignore
            hoy = datetime.now()
            alias_p1 = F"{alias}_P1"
            alias_p2 = F"{alias}_P2"

            piso1 = PisoConfig(tipo="",alias=alias_p1,altura=0,recibe=False,entregar=False,tipo_recibo="",tipo_entrega="",orientacion_magazine="",orientacion_permitida_amr="",recibe_de=[])
            piso2 = PisoConfig(tipo="",alias=alias_p2,altura=0,recibe=False,entregar=False,tipo_recibo="",tipo_entrega="",orientacion_magazine="",orientacion_permitida_amr="",recibe_de=[])
            pisos_configuracion = PisosConfig()

            piso1.alias = alias_p1
            piso2.alias = alias_p2

            pisos_configuracion.configs = {"piso1":piso1,"piso2":piso2}

            pisos_conf = json.dumps({
                "piso1": asdict(pisos_configuracion.piso1), # type: ignore
                "piso2": asdict(pisos_configuracion.piso2) # type: ignore
            }, ensure_ascii=False)


            try:

                query = """
                        INSERT INTO estaciones (alias,mac, smema, pisos_estado, servidor_acciones, amr_estado,
                                                tipo, habilitado, modo_operacion, recibe, coordenadas, \
                                                pisos_configuracion, ultima_modificacion)
                        VALUES (%s, %s,'', '{"P1": "", "P2": ""}', NULL, NULL, '', 0, 'Automatico',
                                '', '{"x": 0, "y": 0}', %s, %s) \
                        """


                rows = DataAccess.__conexion.execute_commit(query, (alias,mac, pisos_conf, hoy)) # type: ignore
                return {"status": "ok", "rows": rows}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    @staticmethod
    def eliminar_estacion(alias: str) -> dict:
        with DataAccess.__candado: # type: ignore
            try:
                query = "DELETE FROM estaciones WHERE alias = %s"
                rows = DataAccess.__conexion.execute_commit(query, (alias,)) # type: ignore
                return {"status": "ok", "rows": rows}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    # TODO Crear trigger en base de datos (revisar chat claude)

