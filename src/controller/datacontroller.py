from model.data import DataAccess


class DataController:
    def __init__(self) -> None:
        self._data = DataAccess()


    def get_estaciones(self):
        return self._data.get_estaciones()

    def get_amr_config(self):
        return self._data.get_amr_config()