from typing import TYPE_CHECKING
from model.data import DataAccess

# Importaciones solo como tipos
if TYPE_CHECKING:
    from model.dataclass_estacion import Estacion


class DataController:
    def __init__(self) -> None:
        self._data = DataAccess()


    def get_estacion(self, alias: str):
        estaciones = self.get_estaciones()
        e = next((e for e in estaciones if e.alias == alias), None)
        return e

    def get_estaciones(self):
        return self._data.get_estaciones()

    def get_amr_config(self):
        return self._data.get_amr_config()

    def get_pisos_config(self):
        return self._data.get_pisos_config()

    def save_pisos_config(self, config:str):
        return self._data.save_pisos_config(config)

    def save_amr_ip_puerto(self, alias:str, ip:str, puerto:int, password:str):
        return self._data.save_amr_ip_puerto(alias, ip, puerto, password)

    def set_servidor_acciones_entregar(self, piso:str, estacion: Estacion):
        return self._data.set_servidor_acciones_entregar(piso=piso, estacion=estacion)

    def set_servidor_acciones_recibir(self, piso:str, estacion: Estacion):
        return self._data.set_servidor_acciones_recibir(piso=piso, estacion=estacion)

    def limpiar_servidor_acciones(self, piso:str, estacion:Estacion):
        return self._data.limpiar_servidor_acciones(piso=piso, estacion=estacion)

    def enviar_orden_amr_entrega(self, piso:str):
        return self._data.enviar_orden_amr_entrega(piso=piso)

    def enviar_orden_amr_recibe(self, piso:str):
        return self._data.enviar_orden_amr_recibe(piso=piso)

    def limpiar_orden_amr(self):
        return self._data.limpiar_orden_amr()