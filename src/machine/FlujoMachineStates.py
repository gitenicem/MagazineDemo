from helpers.amr import AMR
from helpers.estados import EstadosPiso, EstadosAmr, EstadosServidor, OrientacionAmr, FlujoEstado
from controller.manager import ManagerController
from controller.amrs import AmrsController
from model.dataclass_amr import AMRs
from machine.state import State
#from Log import Log
import time

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
class Init(State):
    name = 'Init'

    def on_enter(self):
        # self.machine.set_error_state(ErrorCheck)
        print(self.machine.flujo.get_alias(), "Initializing...") # type: ignore
        self.machine.flujo.flujo_estado = FlujoEstado.INICIANDO # type: ignore

    def update(self):

        self.machine.transition_to(EnviarSolicitudEntrega)

"""------------------------------------------------------------------------------------------------------------------"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""ENVIAMOS SOLICITUD DE ENTREGA DE MAGAZINE A ESTACION ORIGEN"""
# noinspection SpellCheckingInspection
"""Escribimos P1 ENTREGAR ó P2 ENTREGAR en servidior_acciones"""

# noinspection SpellCheckingInspection
class EnviarSolicitudEntrega(State):
    name = 'EnviarSolicitudEntrega'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(),f'Enviando solicitud de recepcion en servidor_acciones de {self.machine.flujo.estacion_origen.alias}') # type: ignore

    def update(self):
        #res = ManagerController.avisar_a_piso_origen_del_flujo(self.machine.flujo, EstadosServidor.ENTREGAR.value) # type: ignore
        print(self.machine.flujo.get_alias(), f"Solicitud enviada") # type: ignore
        self.machine.transition_to(RevisarSolicitudEntregaAceptada)

"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
"""Servidor_acciones debe cambiar su estado a ENTREGAR"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""REVISAMOS SI LA ESTACION ORIGEN ACEPTO LA SOLICITUD DE ENTREGA"""
# noinspection SpellCheckingInspection
"""Revisamos pisos_estado P1 ó P2 sea ENTREGAR"""

# noinspection SpellCheckingInspection
class RevisarSolicitudEntregaAceptada(State):
    name = 'RevisarSolicitudEntregaAceptada'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Confirmando entrega en pisos_estado de {self.machine.flujo.estacion_origen.alias}') # type: ignore


    def update(self):
        """******************************************************************************************************************"""
        if ManagerController.revisar_estacion_en_piso_que_entrega(self.machine.flujo.estacion_origen,EstadosPiso.OCUPADO.value): # type: ignore
            self.machine.transition_to(CancelarPisoEntrega)
            return
        """******************************************************************************************************************"""

        self.res = ManagerController.revisar_que_el_pisos_que_entrega_acepte_el_flujo(self.machine.flujo.estacion_origen, EstadosPiso.ENTREGAR.value) # type: ignore
        self.machine.flujo.flujo_estado = FlujoEstado.CONFIRMANDO_ORIGEN # type: ignore

        if self.res:
            print(self.machine.flujo.get_alias(), f"Solicitud recibida en pisos_estado de {self.machine.flujo.estacion_origen.alias}") # type: ignore
            self.machine.transition_to(EnviarSolicitudRecepcion)

    time.sleep(0.5)
"""------------------------------------------------------------------------------------------------------------------"""


"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""ENVIAMOS SOLICITUD DE RECEPCION DE MAGAZINE A ESTACION DESTINO (SERVIDOR_ACCIONES)"""
# noinspection SpellCheckingInspection
"""Escribimos P1 RECIBIR ó P2 RECIBIR en servidior_acciones"""

# noinspection SpellCheckingInspection
class EnviarSolicitudRecepcion(State):
    name = 'EnviarSolicitudRecepcion'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Enviando solicitud de recepcion en servidor_acciones de {self.machine.flujo.estacion_destino.alias}') # type: ignore

    def update(self):
        res = ManagerController.avisar_a_piso_destino_del_flujo(self.machine.flujo, EstadosServidor.RECIBIR.value) # type: ignore
        print(self.machine.flujo.get_alias(), f"Solicitud enviada") # type: ignore
        self.machine.transition_to(RevisarSolicitudRecepcionAceptada)

"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
"""Servidor_acciones debe cambiar su estado a RECIBIR"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""REVISAMOS SI LA ESTACION DESTINO ACEPTO LA SOLICITUD DE RECEPCION (PISOS_ESTADO)"""
# noinspection SpellCheckingInspection
"""Revisamos pisos_estado P1 ó P2 sea RECIBIR"""

# noinspection SpellCheckingInspection
class RevisarSolicitudRecepcionAceptada(State):
    name = 'RevisarSolicitudRecepcionAceptada'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(),f'Confirmando recepcion en pisos_estado de {self.machine.flujo.estacion_destino.alias}') # type: ignore


    def update(self):
        """**********************************************************************************************************"""
        if ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_origen,EstadosPiso.CANCELAR.value): # type: ignore 
            self.machine.transition_to(CancelarPisoEntrega)
            return
        if ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosPiso.CANCELAR.value): # type: ignore
            self.machine.transition_to(CancelarPisoRecibe)
            return
        """**********************************************************************************************************"""
        self.res = ManagerController.revisar_que_el_pisos_que_recibe_acepte_el_flujo(self.machine.flujo.estacion_destino, EstadosPiso.RECIBIR.value) # type: ignore
        self.machine.flujo.flujo_estado = FlujoEstado.CONFIRMANDO_DESTINO # type: ignore

        if self.res:
            print(self.machine.flujo.get_alias(),f"Solicitud recibida en pisos_estado de {self.machine.flujo.estacion_destino.alias}") # type: ignore
            self.machine.transition_to(AvisoAmrOrigen)

        time.sleep(0.5)
"""------------------------------------------------------------------------------------------------------------------"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""ENVIAMOS AL AMR A LA ESTACION DE ORIGEN PARA RECIBIR EL MAGAZINE"""

# noinspection SpellCheckingInspection
# noinspection DuplicatedCode
class AvisoAmrOrigen(State):
    name = 'AvisoAmrOrigen'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), 'Enviando AMR a estación de origen') # type: ignore

    def update(self):
        # if f"Arrived at {self.machine.flujo.estacion_origen.estacion.alias + '_' + OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_origen)}" in AmrsController.get_amr_status_socket(AMRs[0].alias):
        #     objetivo = AmrsController.obtener_objetivo_seguro(self.machine.flujo.estacion_destino.estacion.alias)
        #     print(self.machine.flujo.get_alias(),f"Enviando AMR destino a punto seguro: {objetivo} en {self.machine.flujo.estacion_destino.estacion.alias}")
        #     AmrsController.enviar_amr_a_objetivo_seguro(AMRs[0].alias, objetivo)
        #     return

        # if f"Arrived at {AmrsController.obtener_objetivo_seguro(self.machine.flujo.estacion_destino.estacion.alias)}":
        print(self.machine.flujo.get_alias(), f"{self.machine.flujo.estacion_origen.estacion.alias}_{OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_origen)}") # type: ignore
        AmrsController.enviar_amr_a_objetivo(AMRs[0].alias, self.machine.flujo.estacion_origen.estacion.alias + '_' + OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_origen)) # type: ignore
        ##AmrsController.enviar_amr_a_estacion_origen(AMRs[0].alias, self.machine.flujo.estacion_origen.estacion.alias + '_' + OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_origen))
        self.machine.flujo.flujo_estado = FlujoEstado.YENDO_A_ORIGEN # type: ignore
        print(self.machine.flujo.get_alias(), f"Solicitud enviada al AMR") # type: ignore
        self.machine.transition_to(EsperarAmrSocketOrigen)


"""------------------------------------------------------------------------------------------------------------------"""

# TODO implementar un metodo que solicite confirmacion de parte del amr (TCP)

"""------------------------------------------------------------------------------------------------------------------"""
class EsperarAmrSocketOrigen(State):
    name = 'EsperarAmrSocketArribed'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), 'Esperando respuesta(tcp) llegada de AMR a estación de origen') # type: ignore

    def update(self):
        if "Failed to drive to Target" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(ReintentarAmrOrigen)

        if "Arrived at" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(EsperarAmrRecibiendoOrigen)


class ReintentarAmrOrigen(State):
    name = 'ReintentarAmrOrigen'

    def on_enter(self):
        objetivo = AmrsController.obtener_objetivo_seguro(self.machine.flujo.estacion_origen.estacion.alias) # type: ignore
        print(self.machine.flujo.get_alias(), f"Enviando AMR origen a punto seguro: {objetivo} en {self.machine.flujo.estacion_origen.estacion.alias}") # type: ignore
        AmrsController.enviar_amr_a_objetivo_seguro(AMRs[0].alias, objetivo)

    def update(self):
        if "Arrived at" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(AvisoAmrOrigen)



# noinspection SpellCheckingInspection
"""Estacion origen debe cambiar su estado a ENTREGANDO despues de recibir conformacion de AMR------------------------"""
# noinspection SpellCheckingInspection
"""AMR debe actualizar su estado a RECIBIENDO------------------------------------------------------------------------"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""BORRAMOS LAS ACCIONES DE SERVIDOR_ACIONES"""
"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
class EsperarAmrRecibiendoOrigen(State):
    name = 'EsperarAmrRecibiendoOrigen'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que AMR cambie estado a {EstadosAmr.RECIBIENDO.value} en {self.machine.flujo.estacion_origen.alias}') # type: ignore
        pass

    def update(self):

        """**********************************************************************************************************"""
        if ManagerController.revisar_estacion_en_piso_que_entrega(self.machine.flujo.estacion_origen,EstadosPiso.CANCELAR.value): # type: ignore
            self.machine.transition_to(CancelarPisoEntrega)
            return
        if ManagerController.revisar_estacion_en_piso_que_entrega(self.machine.flujo.estacion_destino,EstadosPiso.CANCELAR.value): # type: ignore
            self.machine.transition_to(CancelarPisoEntrega)
            return
        """**********************************************************************************************************"""
        if ManagerController.revisar_amr_en_piso_que_entrega(self.machine.flujo.estacion_origen,EstadosAmr.RECIBIENDO.value): # type: ignore
            self.machine.flujo.flujo_estado = FlujoEstado.EN_ORIGEN # type: ignore
            self.machine.transition_to(EsperarAmrFinalizadoOrigen)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
"""ESPERAMOS A QUE EL AMR CAMBIE SU ESTADO A FINALIZADO"""

# noinspection SpellCheckingInspection
class EsperarAmrFinalizadoOrigen(State):
    name = 'EsperarAmrFinalizadoOrigen'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando AMR finalizado en {self.machine.flujo.estacion_origen.alias}') # type: ignore
        # print(f'{self.machine.flujo.get_alias()} Esperando AMR finalizado')
    def update(self):

        """**********************************************************************************************************"""
        if ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_origen,EstadosPiso.CANCELAR.value): # type: ignore
            self.machine.transition_to(CancelarPisoRecibe)
            return
        if ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosPiso.CANCELAR.value): # type: ignore
            self.machine.transition_to(CancelarPisoRecibe)
            return
        """**********************************************************************************************************"""

        if not self.res:
            self.res = ManagerController.revisar_amr_en_piso_que_entrega(self.machine.flujo.estacion_origen,EstadosAmr.FINALIZADO.value) # type: ignore

        else:
            print(self.machine.flujo.get_alias(), 'AMR Orogen Finalizado OK') # type: ignore
            # print(f'{self.machine.flujo.get_alias()} AMR Finalizado')
            self.machine.transition_to(LimpezaServidorAccionesOrigen)

        time.sleep(0.5)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class LimpezaServidorAccionesOrigen(State):
    name = 'LimpezaServidorAccionesOrigen'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(), 'Limpiando servidor acciones (origen)') # type: ignore

        # print(f'{self.machine.flujo.get_alias()} Limpiando servidor acciones')

    def update(self):
        ManagerController.borrar_instruccion_de_estacion_que_entrega(self.machine.flujo.estacion_origen) # type: ignore
        self.machine.transition_to(EsperarAmrSiguienteEnOrigen)

        #Finalizado
        #Siguiente
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
"""AMR debe actualizar su estado a SIGUIENTE-------------------------------------------------------------------------"""

"""------------------------------------------------------------------------------------------------------------------"""
# noinspection SpellCheckingInspection
"""ESPERAMOS A QUE EL AMR CAMBIE SU ESTADO A SIGUIENTE"""

# noinspection SpellCheckingInspection
class EsperarAmrSiguienteEnOrigen(State):
    name = 'EsperarAmrSiguienteEnOrigen'
    res = False

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando AMR siguiente en {self.machine.flujo.estacion_origen.alias}') # type: ignore
        # print(f'{self.machine.flujo.get_alias()} Esperando AMR siguiente')

    def update(self):

        if not self.res:
            self.res = ManagerController.revisar_amr_en_piso_que_entrega(self.machine.flujo.estacion_origen,EstadosAmr.SIGUIENTE.value) # type: ignore

        else:
            print(self.machine.flujo.get_alias(), 'AMR Origen Siguiente OK') # type: ignore
            # print(f'{self.machine.flujo.get_alias()} AMR Preparado')
            self.machine.transition_to(AvisoAmrDestino)

        time.sleep(0.5)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
# noinspection DuplicatedCode
class AvisoAmrDestino(State):
    name = 'AvisoAmrDestino'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Enviando AMR a {self.machine.flujo.estacion_destino.alias}') # type: ignore
        # print(f'{self.machine.flujo.get_alias()} Enviando AMR a estación de destino')

    def update(self):
        # if "Arrived at" in AmrsController.get_amr_status_socket(AMRs[0].alias):
        #     objetivo = AmrsController.obtener_objetivo_seguro(self.machine.flujo.estacion_destino.estacion.alias)
        #     print(self.machine.flujo.get_alias(),f"Enviando AMR destino a punto seguro: {objetivo} en {self.machine.flujo.estacion_destino.estacion.alias}")
        #     AmrsController.enviar_amr_a_objetivo_seguro(AMRs[0].alias, objetivo)
        #     return

        print(self.machine.flujo.get_alias(),f"{self.machine.flujo.estacion_destino.estacion.alias}_{OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_destino)}") # type: ignore
        AmrsController.enviar_amr_a_objetivo(AMRs[0].alias, self.machine.flujo.estacion_destino.estacion.alias + '_' + OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_destino)) # type: ignore
        ##AmrsController.enviar_amr_a_estacion_destino(AMRs[0].alias, self.machine.flujo.estacion_destino.estacion.alias + '_' + OrientacionAmr.a_texto(self.machine.flujo.solucion_de_giro.orientacion_amr_destino))
        self.machine.flujo.flujo_estado = FlujoEstado.YENDO_A_DESTNO # type: ignore
        print(self.machine.flujo.get_alias(), f"Solicitud enviada al AMR") # type: ignore
        # print(f'{self.machine.flujo.get_alias()} Solicitud enviada')
        self.machine.transition_to(EsperarAmrSocketDestino) #LimpezaServidorAccionesDestino
"""------------------------------------------------------------------------------------------------------------------"""

# TODO implementar un metodo que solicite confirmacion de parte del amr (TCP)

"""------------------------------------------------------------------------------------------------------------------"""

class EsperarAmrSocketDestino(State):
    name = 'EsperarAmrSocketDestino'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), 'Esperando respuesta(tcp) llegada de AMR a estación de destino') # type: ignore

    def update(self):
        if "Failed to drive to Target" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(ReintentarAmrOrigen)

        if "Arrived at" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(LimpezaServidorAccionesDestino)


class ReintentarAmrDestino(State):
    name = 'ReintentarAmrDestino'

    def on_enter(self):

        objetivo = AmrsController.obtener_objetivo_seguro(self.machine.flujo.estacion_destino.estacion.alias) # type: ignore
        print(self.machine.flujo.get_alias(), f"Enviando AMR destino a punto seguro: {objetivo} en {self.machine.flujo.estacion_destino.estacion.alias}") # type: ignore
        AmrsController.enviar_amr_a_objetivo_seguro(AMRs[0].alias, objetivo)

    def update(self):
        if "Arrived at" in AmrsController.get_amr_status_socket(AMRs[0].alias):
            self.machine.transition_to(LimpezaServidorAccionesDestino)

# noinspection SpellCheckingInspection
class LimpezaServidorAccionesDestino(State):
    name = 'LimpezaServidorAccionesDestino'

    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Limpiando servidor_acciones en {self.machine.flujo.estacion_destino.alias}') # type: ignore
        # print(f'{self.machine.flujo.get_alias()} Limpiando servidor acciones')

    def update(self):
        ManagerController.borrar_instruccion_de_piso_que_recibe(self.machine.flujo.estacion_destino) # type: ignore
        self.machine.transition_to(EsperarAmrDestino)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class EsperarAmrDestino(State):
    name = 'EsperarAmrEntregaDestino'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que AMR cambie estado a {EstadosAmr.PREPARADO.value} en {self.machine.flujo.estacion_destino.alias}') # type: ignore
        pass

    def update(self):
        if ManagerController.revisar_amr_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosAmr.PREPARADO.value): # type: ignore
            self.machine.flujo.flujo_estado = FlujoEstado.EN_DESTNO # type: ignore
            self.machine.transition_to(EsperarEstacionRecibiendo)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class EsperarEstacionRecibiendo(State):
    name = 'EsperarEstacionRecibiendo'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que estacion cambie estado a {EstadosPiso.RECIBIENDO.value} en {self.machine.flujo.estacion_destino.alias}') # type: ignore

    def update(self):
        res = ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosPiso.RECIBIENDO.value) # type: ignore
        if res:
            self.machine.flujo.flujo_estado = FlujoEstado.ESTACION_RECIBIENDO # type: ignore
            self.machine.transition_to(EsperarEstacionFinalizado)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class EsperarEstacionFinalizado(State):
    name = 'EsperarEstacionFinalizado'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que estacion cambie estado a {EstadosPiso.FINALIZADO.value} en {self.machine.flujo.estacion_destino.alias}') # type: ignore
        pass

    def update(self):
        if ManagerController.revisar_estacion_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosPiso.FINALIZADO.value): # type: ignore
            self.machine.flujo.flujo_estado = FlujoEstado.ESTACION_RECIBIENDO # type: ignore
            self.machine.transition_to(EsperarAmrDestinoFinalizado)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class CancelarPisoRecibe(State):
    name = 'CancelarPisoRecibe'

    def on_enter(self):
        AmrsController.send(AMRs[0].alias, "stop") # type: ignore
        print(self.machine.flujo.get_alias(), f"Cancelando solicitur de recepcion: {ManagerController.cancelar_instruccion_piso_que_recibe(self.machine.flujo.estacion_destino, EstadosServidor.CANCELAR.value)}") # type: ignore

    def update(self):
        # TODO Cambiar transition to FinishMachine
        self.machine.transition_to(Init)
        ManagerController.borrar_servidor_acciones()
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class CancelarPisoEntrega(State):
    name = 'CancelarPisoEntrega'

    def on_enter(self):
        AmrsController.send(AMRs[0].alias,"stop")
        print(self.machine.flujo.get_alias(), f"Cancelando solicitur de entrega: {ManagerController.cancelar_instruccion_piso_que_entrega(self.machine.flujo.estacion_origen, EstadosServidor.CANCELAR.value)}") # type: ignore

    def update(self):
        # TODO Cambiar transition to FinishMachine
        self.machine.transition_to(Init)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class EsperarAmrDestinoFinalizado(State):
    name = 'EsperarAmrDestinoFinalizado'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que AMR cambie estado a {EstadosAmr.FINALIZADO.value} en {self.machine.flujo.estacion_destino.alias}') # type: ignore
        pass

    def update(self):
        if ManagerController.revisar_amr_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosAmr.FINALIZADO.value): # type: ignore
            self.machine.flujo.flujo_estado = FlujoEstado.FINALIZADO # type: ignore
            self.machine.transition_to(EsperarAmrDestinoVacio)
"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class EsperarAmrDestinoVacio(State):
    name = 'EsperarAmrEntregaDestinoVacio'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Esperando a que AMR cambie estado a {EstadosAmr.NONE.value} en {self.machine.flujo.estacion_destino.alias}') # type: ignore
        pass

    def update(self):
        if ManagerController.revisar_amr_en_piso_que_recibe(self.machine.flujo.estacion_destino,EstadosAmr.NONE.value): # type: ignore
            self.machine.transition_to(FinishMachine)

"""------------------------------------------------------------------------------------------------------------------"""

# noinspection SpellCheckingInspection
class FinishMachine(State):
    name = 'FinishMachine'
    def on_enter(self):
        print(self.machine.flujo.get_alias(), f'Finalizando...') # type: ignore
        self.machine.finish_machine()
        pass
"""------------------------------------------------------------------------------------------------------------------"""







# noinspection SpellCheckingInspection







