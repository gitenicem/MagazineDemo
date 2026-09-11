from __future__ import annotations


import time
import threading
from datetime import datetime
from typing import Dict, TYPE_CHECKING
from enum import Enum

from model.dataclass_estacion import Estacion



# noinspection SpellCheckingInspection
class StateMachine:

    _error_state: type
    _cancel_state: type
    _finish_state: type
    
    def finish_machine(self):
        self._finish_machine = True

    def get_is_finished(self)-> bool:
        return self._finish_machine

    def __init__(self, args: Dict[str, any]): # type: ignore
        self.args = args
        self.action = None
        self.piso = self.args.get('piso', '')
        self.alias = self.args.get("alias", '')
        self._periodo_db = self.args.get("periodo", '') or 2.0
        self.estacion: Estacion = None # type: ignore


    def arrancar(self):
        """entra en el estado inicial de la máquina de estados."""
        try:
            self._current_state.on_enter()
        except Exception as e:
            self.error_flag = True
            print(self.alias,f'Error: {e} in init state')

    def _set_initial_state(self, initial_state:  type):
        """Establece el estado inicial de la máquina de estados."""
        self._current_state = initial_state(self)

    def set_cancel_state(self, cancel_state: type):
        self._cancel_state = cancel_state

    def set_error_state(self, error_state: type):
        self._error_state = error_state

    def set_finish_state(self, finish_state: type):
        self._error_state = finish_state

    def transition_to(self, next_state: type):

        """Realiza la transición a un nuevo estado."""
        try:
            transition_message = '▄▄ Transition '
            if self._current_state:
                if type(self._current_state) == next_state:
                    return

                self._current_state.on_exit()
                transition_message += f' from {self._current_state.name} '
            self._current_state = next_state(self)
            transition_message += f' to {self._current_state.name} ▄▄'
            print(self.piso, transition_message)
            self._current_state.on_enter()
        except Exception as e:
            self.error_flag = True
            print(self.piso,f'Error: {e} in transition to {next_state}')


    _ultima_actualizacion = datetime.now()

    def _ya_toca_actualizar(self, periodo: float):
        tiempo_trasncurrido = (datetime.now() - self._ultima_actualizacion)
        if tiempo_trasncurrido.total_seconds() >= periodo:
            self._ultima_actualizacion = datetime.now()
            return True
        return False



    def update(self):
        """Actualiza la máquina de estados, llamando el método update del estado actual."""
        # TODO check conditions antes de ir al siguiente estado

         #TODO funcion que acutualiza flujo desde base de server
        #EstacionController.get_estacion_model(self.alias)


        # ACTUALIZAMOS ESTACION DEL FLUJO
        # if self._tipo_maquina == StateMachine.TipoMaquina.FLUJO:
        #     if self.flujo_controller:
        #         [maquina] = self.flujo_controller.obtener_flujo_en_progreso()
        #         if self.flujo.estacion_origen.estacion.alias == maquina.flujo.estacion_origen.estacion.alias:
        #             self.estacion = self.flujo.estacion_origen.estacion
        #             # print(f"{maquina.flujo.estacion_origen.estacion.alias} : {maquina.flujo.estacion_origen.estacion.modo_operacion}")
        #         elif self.flujo.estacion_destino.estacion.alias == maquina.flujo.estacion_destino.estacion.alias:
        #             self.estacion = self.flujo.estacion_destino.estacion
        #             # print(f"{maquina.flujo.estacion_destino.estacion.alias} : {maquina.flujo.estacion_destino.estacion.modo_operacion}")

        # # ACTUALIZAMOS ESTACION DE LA ESTACION
        # elif self._tipo_maquina == StateMachine.TipoMaquina.ESTACION:
        #     if self._ya_toca_actualizar(periodo = self._periodo_db):
        #         if EstacionController.estaciones_actualizadas():
        #             self.estacion = EstacionController.get_estacion()




        state_name = 'check conditions'
        try:
            self._check_conditions()
            if self._current_state:
                state_name = self._current_state.name
                self._current_state.update()
        except Exception as e:
            self.error_flag = True
            # Todo en WaitActionExecution hay que abortar si se presenta una bandera de error y luego mandar a errorhandle
            print(self.piso,f'Error: {e.args} in update {state_name}')





    def _check_conditions(self):

        if self._finish_machine:
            self.transition_to(self._finish_state)
            return
