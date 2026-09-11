from model.dataclass_coincidencias import EstacionPisoConfig, FlujoPiso
from model.dataclass_estacion import Estacion, PisosConfig, PisoConfig, PisosEstado
#from model.manager import ManagerModel
from typing import Tuple

# noinspection PyProtectedMember
# noinspection SpellCheckingInspection
class ManagerController:
    __manager : ManagerModel = None # type: ignore
    __has_error = False

    @staticmethod
    def __error_on(e : Exception ):
        ManagerController.__has_error = True


    @staticmethod
    def __error_off():
        ManagerController.__has_error = False


    @staticmethod
    def has_error():
        return ManagerController.__has_error

    @staticmethod
    def recovery():
        try:

            ManagerController.__error_off()

        except Exception as e:
            ManagerController.__error_on(e)
        finally:
            pass



    @staticmethod
    def init():
        #ManagerController.__manager = ManagerModel()
        pass

    @staticmethod
    def actualizar_flujo_en_db(machine)-> int:
        res = ManagerController.__manager._actualizar_flujo_en_db(machine)
        return res

    @staticmethod
    def get_ultima_modificacion(alias: str):
        res = ManagerController.__manager._get_ultima_modificacion(alias)
        return res

    @staticmethod
    def get_estacion_preparado() -> Estacion:
        res = ManagerController.__manager._get_estacion_preparado()
        return res

    @staticmethod
    def get_estacion_preparado_entregar() -> Estacion:
        res = ManagerController.__manager._get_estacion_preparado_entregar()
        return res

    @staticmethod
    def get_estacion_preparado_recibir() -> Estacion:
        res = ManagerController.__manager._get_estacion_preparado_recibir()
        return res

    @staticmethod
    def get_pisos_configuracion() -> list[PisosConfig]:
        res = ManagerController.__manager._get_pisos_configuracion()
        return res

    @staticmethod
    def estaciones_actualizadas() -> bool:
        res = ManagerController.__manager._estaciones_actualizadas()
        return res

    @staticmethod
    def get_pisos_estado() -> list[PisosEstado]:
        res = ManagerController.__manager._get_pisos_estado()
        return res

    @staticmethod
    def get_piso_configuracion( alias:str, piso:str) -> PisoConfig:
        res = ManagerController.__manager._get_piso_configuracion(alias, piso)
        return res

    # servidor_acciones
    @staticmethod
    def avisar_a_piso_origen_del_flujo(flujo: FlujoPiso, estado:str) -> bool:
        #le ponemos la instruccion en servidor_acciones a cada piso segun si es el que recibe o el que entrega
        res = ManagerController.__manager._avisar_a_piso_origen_del_flujo(flujo, estado)
        return res

    # pisos_estado
    @staticmethod
    def revisar_que_el_pisos_que_entrega_acepte_el_flujo(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._revisar_que_el_pisos_que_entrega_acepte_el_flujo(piso_config, estado)
        return res

    # servidor_acciones
    @staticmethod
    def avisar_a_piso_destino_del_flujo(flujo: FlujoPiso, estado: str) -> bool:
        # le ponemos la instruccion en servidor_acciones a cada piso segun si es el que recibe o el que entrega
        res = ManagerController.__manager._avisar_a_piso_destino_del_flujo(flujo, estado)
        return res

    @staticmethod
    def revisar_que_el_pisos_que_recibe_acepte_el_flujo(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._revisar_que_el_pisos_que_recibe_acepte_el_flujo(piso_config, estado)
        return res

    @staticmethod
    def revisar_estacion_en_piso_que_entrega(piso_config: EstacionPisoConfig, estado: str) -> bool:
        res = ManagerController.__manager._revisar_estacion_en_piso_que_entrega(piso_config, estado)
        return res

    @staticmethod
    def revisar_estacion_en_piso_que_recibe(piso_config: EstacionPisoConfig, estado: str) -> bool:
        res = ManagerController.__manager._revisar_estacion_en_piso_que_recibe(piso_config, estado)
        return res

    @staticmethod
    def revisar_amr_en_piso_que_entrega(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._revisar_amr_en_piso_que_entrega(piso_config, estado)
        return res

    @staticmethod
    def borrar_instruccion_de_estacion_que_entrega(piso_config: EstacionPisoConfig) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._borrar_instruccion_de_estacion_que_entrega(piso_config)
        return res

    @staticmethod
    def borrar_servidor_acciones()-> bool:
        res = ManagerController.__manager._borrar_servidor_acciones()
        return res

    @staticmethod
    def _borrar_amr_estado()-> bool:
        res = ManagerController.__manager._borrar_amr_estado()
        return res

    @staticmethod
    def revisar_amr_en_piso_que_recibe(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._revisar_amr_en_piso_que_recibe(piso_config, estado)
        return res

    @staticmethod
    def resvisar_amr_preparado(piso_config: EstacionPisoConfig, estado: str) -> bool:
        res = ManagerController.__manager._revisar_amr_preparado(piso_config, estado)
        return res

    @staticmethod
    def borrar_instruccion_de_piso_que_recibe(piso_config: EstacionPisoConfig) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que
        res = ManagerController.__manager._borrar_instruccion_de_piso_que_recibe(piso_config)
        return res

    @staticmethod
    def cancelar_instruccion_piso_que_recibe(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._cancelar_instruccion_piso_que_recibe(piso_config, estado)
        return res

    @staticmethod
    def cancelar_instruccion_piso_que_entrega(piso_config: EstacionPisoConfig, estado: str) -> bool:
        # revisar en  pisos_estatus que cada piso recina la instruccion segun si es el que recibe o el que entrega
        res = ManagerController.__manager._cancelar_instruccion_piso_que_entrega(piso_config, estado)
        return res

    @staticmethod
    def obtener_estaciones_filtradas()-> Tuple[list[EstacionPisoConfig], list[EstacionPisoConfig]]:
        res = ManagerController.__manager._obtener_estaciones_filtradas()
        return res

    @staticmethod
    def obtener_todas_las_estaciones() -> Tuple[list[EstacionPisoConfig], list[EstacionPisoConfig]]:
        res = ManagerController.__manager._obtener_todas_las_estaciones()
        return res

    @staticmethod
    def generar_posibles_flujos( piso_entrega: list[EstacionPisoConfig], piso_recibe: list[EstacionPisoConfig]) -> list[FlujoPiso]:
        res = ManagerController.__manager._generar_posibles_flujos(piso_entrega, piso_recibe)
        return res

    @staticmethod
    def estaciones_detectadas_actualizadas() -> bool:
        res = ManagerController.__manager.estaciones_detectadas_actualizadas()
        return res

    @staticmethod
    def revisar_estaciones_detectadas(alias:str, mac: str) -> bool:
        res = ManagerController.__manager.revisar_estaciones_detectadas(alias,mac)
        return res

    @staticmethod
    def eliminar_estacion_detectada(mac: str):
        res = ManagerController.__manager.eliminar_estacion_detectada(mac)
        return res

    @staticmethod
    def obtener_ultima_modificacion(mac: str):
        res = ManagerController.__manager.obtener_ultima_modificacion(mac)
        return res

    @staticmethod
    def obtener_estaciones_detectadas():
        res = ManagerController.__manager.obtener_estaciones_detectadas()
        return res
