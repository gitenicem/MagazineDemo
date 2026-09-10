from model.data import DataAccess


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

    def save_amr_ip_puerto(self, alias:str, ip:str, puerto:int, password:str):
        return self._data.save_amr_ip_puerto(alias, ip, puerto, password)