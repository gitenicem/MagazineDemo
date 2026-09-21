from dataclasses import asdict
import json
import asyncio

import flet as ft
from typing import TYPE_CHECKING
from config.db_config import cargar_config
from helpers.estados import EstadosPiso, EstadosAmr
from controller.amrs import AmrsController
from controller.datacontroller import DataController
from controller.manager import ManagerController as manager

# Importaciones solo como tipos
if TYPE_CHECKING:
    from model.dataclass_estacion import Estacion

data: DataController = None # type: ignore
wip: Estacion = None # type: ignore

class flujo():
    __running = False
    _origen = {'piso':'','estado':''}
    _destino = {'piso':'','estado':''}
    origen_creado = False
    destino_creado = False

    @classmethod
    def set_origen(cls, piso:str, estado:str):
        cls._origen['piso'] = piso
        cls._origen['estado'] = estado
        cls.origen_creado = True

    @classmethod
    def set_destino(cls, piso:str, estado:str):
        cls._destino['piso'] = piso
        cls._destino['estado'] = estado
        cls.destino_creado = True
        cls.__running = True

    @classmethod
    def running(cls) -> bool:
        return cls.__running

    @classmethod
    def clear(cls):
        cls._origen = {'piso':'','estado':''}
        cls._destino = {'piso':'','estado':''}
        cls.origen_creado = False
        cls.destino_creado = False
        cls.__running = False
        

    

class Secuencia():
    paso: int=0
    piso: str = ""
    origen: bool = True # Determina si es piso de origen
    home = None  # referencia a la instancia de Home
    

    @classmethod
    def set_home(cls, home_instance):
        cls.home = home_instance

    @classmethod
    def init(cls, origen: bool, piso:str):
        print("Iniciando proceso de netrega" if origen else "Iniciando proceso de recepcion")
        cls.origen = origen
        cls.piso = piso
        cls.paso = 1

    @classmethod
    def next(cls):
        cls.paso+=1

    @classmethod
    def finish(cls):
        print("Finish")
        if cls.origen: # Es el origen
            flujo._origen['estado'] = "IDDLE"
        
        # FINALIZACION DEL FLUJO EN LOS DOS PISOS CUANDO EL DESTINO TERMINA DE RECIBIR
        else: # Es el destino

            # Reinicio del flujo
            flujo.clear()

        cls.paso = 0

    @classmethod
    def running(cls):
        return cls.paso!=0

    @classmethod
    def loop(cls):
        global wip
        global data

        # print(wip.amr_estado.get(f"{cls.piso}"))

        # SECUENCIA DE ENTREGA*********************
        # SERVIDOR -> servidor_acciones = ENTREGAR
        # 1.- AMR --> RECIBIENDO
        # 2.- SERVIDOR -> servidor_acciones = "" ( ESTACION INICIA PROCESO DE ENTREGA)
        # 3.- AMR -> PISO ORIGEN = FINALIZADO
        # 4.- AMR -> PISO ORIGEN = SIGUIENTE
        # 5.- AMR -> PISO ORIGEN = ""

        # SECUENCIA DE RECEPCION******************
        # SERVIDOR -> servidor_acciones = RECIBIR
        # 1.- AMR -> PISO DESTINO = PREPARADO
        # 2.- SERVER -> servidor acciones = "" (ESTACION INICIA PROCESO DE RECEPCION)
        # 3.- AMR -> PISO DESTINO = FINALIZADO
        # 4.- AMR -> PISO DESTINO = ""

        match cls.paso:
            case 1:
                if cls.origen:
                    #print(f"[ORIGEN {cls.piso}] Esperando amr_estado RECIBIENDO")
                    if wip.amr_estado.get(f"{cls.piso}") == EstadosAmr.RECIBIENDO.value:
                        data.limpiar_servidor_acciones(cls.piso, wip)
                        data.limpiar_orden_amr()
                        cls.next()
                else:
                    #print(f"[DESTINO {cls.piso}] Esperando amr_estado PREPARADO")
                    if wip.amr_estado.get(f"{cls.piso}") == EstadosAmr.PREPARADO.value:
                        data.limpiar_servidor_acciones(cls.piso, wip)
                        data.limpiar_orden_amr()
                        cls.next()
            case 2:
                #print(f"servidor_acciones = {wip.servidor_acciones.get(f"P{cls.piso}")}")
                if cls.origen:
                    print(f"[ORIGEN {cls.piso}] Esperando servidor_acciones NONE")
                    if wip.servidor_acciones.get(f"{cls.piso}") == None:
                        cls.next()
                else:
                    print(f"[DESTINO {cls.piso}] Esperando servidor_acciones NONE")
                    if wip.servidor_acciones.get(f"{cls.piso}") == None:
                        cls.next()
            case 3:
                #print(f"amr_estado = {wip.servidor_acciones.get(f"P{cls.piso}")}")
                if cls.origen:
                    print(f"[ORIGEN {cls.piso}] Esperando amr_estado FINALIZADO")
                    if wip.amr_estado.get(f"{cls.piso}") == EstadosAmr.FINALIZADO.value:
                        cls.next()
                else:
                    print(f"[DESTINO {cls.piso}] Esperando amr_estado FINALIZADO")
                    if wip.amr_estado.get(f"{cls.piso}") == EstadosAmr.FINALIZADO.value:
                        cls.next()
            case 4:
                #print(f"amr_estado = {wip.servidor_acciones.get(f"P{cls.piso}")}")
                if cls.origen:
                    print(f"[ORIGEN {cls.piso}] Esperando amr_estado SIGUIENTE")
                    if wip.amr_estado.get(f"{cls.piso}") == EstadosAmr.SIGUIENTE.value:
                        cls.next()
                else:
                    print(f"[DESTINO {cls.piso}] Esperando amr_estado NONE")
                    if wip.amr_estado.get(f"{cls.piso}") == None:
                        cls.next()
            case 5:
                #print(f"amr_estado = {wip.amr_estado.get(f"P{cls.piso}")}")
                if cls.origen:
                    print(f"[ORIGEN {cls.piso}] Esperando amr_estado NONE")
                    if wip.amr_estado.get(f"{cls.piso}") == None:
                        cls.next()
                else:
                    cls.next()
            case _:
                if cls.home:
                    cls.home.conveyor.visible = False
                    cls.home.conveyor.update() 
                cls.finish()



#@ft.control
class Home(ft.Column):
    #db_data = None
    automatico_activo = False
    conveyor = None


    def __init__(self):
        super().__init__()
        #global conveyor

        #self.db_data=data
        #self.automatico_activo = False

        self.dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text("Primero debe seleccionar un piso."),
            actions=[
                ft.TextButton("Aceptar",on_click= lambda e: self.page.pop_dialog())
            ],
            open=True,
        )

        self.conveyor = ft.Image(
            src="conveyoroff.png",
            visible=False,
            height=200,
            fit=ft.BoxFit.CONTAIN,
        )

        self.group = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value="1", label="PISO 1"),
                    ft.Radio(value="2", label="PISO 2")
                ]
            )
        )

        self.btnEntregar = ft.Button(
            icon=ft.Icons.OUTBOX,
            content="Entregar",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=self.entregar_clicked
        )

        self.btnRecibir = ft.Button(
            icon=ft.Icons.INBOX,
            content="Recibir",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=self.recibir_clicked
        )

        self.btnAutomatico = ft.Button(
            icon=ft.Icons.AUTO_AWESOME,
            content="Automático",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=self.automatico_clicked
        )
        
        self.controls = [
            ft.Container(
                #border=ft.Border.all(1, ft.Colors.BLACK),
                #border_radius = 10,
                padding = 10,
                content = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Image(
                            src="ENICEM.png",
                            height=100,
                            fit=ft.BoxFit.CONTAIN,
                        )
                    ]
                ),
            ),
            ft.Container(
                padding = 10,
                content = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.conveyor
                    ]
                )
            ),
            ft.Container(
                padding = 1,

                content = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.group
                    ]
                )
            ),

            ft.Container(
                # border=ft.Border.all(1, ft.Colors.BLACK),
                # border_radius = 10,
                padding = 1,
                #bgcolor=ft.Colors.AMBER_100,

                content = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.btnEntregar,
                        self.btnRecibir
                    ]
                )
            ),
            ft.Container(
                 padding=1,
                 content=ft.Row(
                      alignment=ft.MainAxisAlignment.CENTER,
                      controls=[
                           self.btnAutomatico
                      ]
                 )
            )

            
            
        ]

    def entregar_clicked(self, e):
        global wip
        global data
        if not self.group.value is None:
            piso = int(self.group.value)
        else:
            piso = 0
            self.page.show_dialog(self.dialog)

        wip = data.get_estacion("WIP1") # type: ignore
        estadoP1, estadoP2 = wip.pisos_estado.pisos.values() # type: ignore

        if piso == 1:
            if estadoP1 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value:
                data.set_servidor_acciones_entregar(piso="P1", estacion=wip) # type: ignore
                Secuencia.init(origen=True, piso="P1")
                assert self.conveyor is not None
                self.conveyor.src = "conveyorout.gif"
                self.conveyor.visible = True
            else:
                self.dialog.content=ft.Text(f"P{piso} No está preparado para entregar")
                self.page.show_dialog(self.dialog)

        if piso == 2:
            if estadoP2 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value:
                data.set_servidor_acciones_entregar(piso="P2", estacion=wip) # type: ignore
                Secuencia.init(origen=True, piso="P2")
                assert self.conveyor is not None
                self.conveyor.src = "conveyorout.gif"
                self.conveyor.visible = True
            else:
                self.dialog.content=ft.Text(f"P{piso} No está preparado para entregar")
                self.page.show_dialog(self.dialog)

        print("Ejecuta acción de entregar magazine")


    def recibir_clicked(self, e):
        global wip
        global data
        if not self.group.value is None:
            piso = int(self.group.value)
        else:
            piso = 0
            self.page.show_dialog(self.dialog)

        wip = data.get_estacion("WIP1") # type: ignore
        estadoP1, estadoP2 = wip.pisos_estado.pisos.values() # type: ignore

        if piso == 1:
            if estadoP1 == EstadosPiso.PREPARADO_RECIBIR.value:
                data.set_servidor_acciones_recibir(piso="P1", estacion=wip) # type: ignore
                Secuencia.init(origen=False, piso="P1")
                assert self.conveyor is not None
                self.conveyor.src = "conveyorin.gif"
                self.conveyor.visible = True
            else:
                self.dialog.content=ft.Text(f"P{piso} No está preparado para recibir")
                self.page.show_dialog(self.dialog)

        if piso == 2:
            if estadoP2 == EstadosPiso.PREPARADO_RECIBIR.value:
                data.set_servidor_acciones_recibir(piso="P2", estacion=wip) # type: ignore
                Secuencia.init(origen=False, piso="P2")
                assert self.conveyor is not None
                self.conveyor.src = "conveyorin.gif"
                self.conveyor.visible = True
            else:
                self.dialog.content=ft.Text(f"P{piso} No está preparado para recibir")
                self.page.show_dialog(self.dialog)

        print("Ejecuta acción de recibir magazine")

    def automatico_clicked(self, e):
        if self.automatico_activo:
            self.automatico_activo = False
            self.btnEntregar.disabled = False
            self.btnRecibir.disabled = False
        else:
            assert self.conveyor is not None
            self.conveyor.visible = False
            self.automatico_activo = True
            self.btnEntregar.disabled = True
            self.btnRecibir.disabled = True

        #print(self.automatico_activo)


    def did_mount(self):
        Secuencia.set_home(self)
        self.page.run_task(self.pooling) # Orquestador de flujos
        self.page.run_task(self.update)  # Mantiene fresca la data durante la ejecución de un flujo

    #def will_unmount(self):
    #    self.automatico_activo = False

    
    def amr_ejecutar_entrega(self, piso:str, origen:bool):
        print(f"{piso} ENTREGAR")
        Secuencia.init(origen, piso=piso)

    def amr_ejecutar_recepcion(self, piso:str, origen:bool):
        print(f"{piso} RECIBIR")
        Secuencia.init(origen, piso=piso)
        

    async def pooling(self):
        global wip
        global data

        while True:
            if self.automatico_activo:
                try:
                    # Actualiza variable global con los ultimos cambios
                    wip = data.get_estacion("WIP1") # type: ignore
                    estadoP1, estadoP2 = wip.pisos_estado.pisos.values() # type: ignore

                    #print(f"EstadoP1:{estadoP1} EstadoP2:{estadoP2}")

                    # CREACION DEL FLUJO
                    # Si los dos solo pueden recibir no se crea flujo
                    if not (estadoP1 == EstadosPiso.PREPARADO_RECIBIR and estadoP2 == EstadosPiso.PREPARADO_RECIBIR):

                        if not Secuencia.running() and not flujo.running():
                            if estadoP1 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value: # TIENE UN MAGAZINE (POSIBLE ORIGEN)
                                if not flujo.origen_creado:
                                    flujo.set_origen('P1','NONE')

                        if not Secuencia.running() and not flujo.running():
                            if estadoP2 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value: # TIENE UN MAGAZINE (POSIBLE ORIGEN)
                                if not flujo.origen_creado:
                                    flujo.set_origen('P2','NONE')



                        if not Secuencia.running() and not flujo.running():
                            if estadoP1 == EstadosPiso.PREPARADO_RECIBIR.value: # NO TIENE MAGAZINE (POSIBLE DESTINO)
                                if not flujo.destino_creado:
                                    flujo.set_destino('P1','NONE')
                        
                        if not Secuencia.running() and not flujo.running():
                            if estadoP2 == EstadosPiso.PREPARADO_RECIBIR.value: # NO TIENE MAGAZINE (POSIBLE DESTINO)
                                if not flujo.destino_creado:
                                    flujo.set_destino('P2','NONE')


                    # INICIO DEL FLUJO
                    if flujo.running():

                        #print(f"Origen: {flujo._origen.get('estado')} Destino: {flujo._destino.get('estado')}")

                        if flujo._origen.get('estado') == "NONE":
                            flujo._origen['estado'] = "RUNNING"
                            if data:
                                data.set_servidor_acciones_entregar(piso = str(flujo._origen.get('piso')), estacion = wip)
                                data.enviar_orden_amr_recibe(piso=str(flujo._origen.get('piso')))
                                self.amr_ejecutar_entrega(piso = str(flujo._origen.get('piso')), origen = True)

                        if flujo._destino.get('estado') == "NONE" and flujo._origen.get('estado') == "IDDLE":
                            flujo._destino['estado'] = "RUNNING"
                            if data:
                                data.set_servidor_acciones_recibir(piso = str(flujo._destino.get('piso')), estacion = wip)
                                data.enviar_orden_amr_entrega(piso=str(flujo._destino.get('piso')))
                                self.amr_ejecutar_entrega(str(flujo._destino.get('piso')), origen = False )
                                    


                except Exception as e:
                    print(f"Error: {e}")

            # Si automático esta detenido y un flujo ya exitia se detiene
            else:
                flujo.clear()

            await asyncio.sleep(1)



    # Ejecuta la secuencia
    async def update(self):
        global wip
        global data
        while True:
            if Secuencia.running():
                wip = data.get_estacion("WIP1") # type: ignore
                # print(wip.amr_estado)
                Secuencia.loop()
                
            await asyncio.sleep(1)

            
            


class Settings(ft.Column):
    global data

    def check_pass(self,e):
         self.txtpassword.password = not e.control.value
         self.txtpassword.update()

    def handle_banner_close(self, e: ft.Event[ft.TextButton]):
        self.page.pop_dialog()

    def save_pisos_config(self, e):
        self.page._remove_dialog(self.banner)
        p1 = self.alturap1.value
        p2 = self.alturap2.value
        self.pisosconfig.piso1.altura = int(p1) # type: ignore
        self.pisosconfig.piso2.altura = int(p2) # type: ignore
        

        pisos_conf = json.dumps({
            "piso1": asdict(self.pisosconfig.piso1), # type: ignore
            "piso2": asdict(self.pisosconfig.piso2) # type: ignore
            }, ensure_ascii=False)
        
        res = data.save_pisos_config(pisos_conf)
        if res:
             self.banner.content = "Configuración guardada correctamente"
             self.page.show_dialog(self.banner)
        else:
            self.banner.content = ft.Text(value="Sin cambios")
            self.page.show_dialog(self.banner)

    def save_amr_config(self, e):
        self.page._remove_dialog(self.banner)
        alias = self.txtalias.value
        ip = self.txtip.value
        puerto = int(self.txtpuerto.value)
        password = self.txtpassword.value
        res = data.save_amr_ip_puerto(alias,ip,puerto,password) # type: ignore
        
        if res:
             self.banner.content = "Configuración guardada correctamente"
             self.page.show_dialog(self.banner)
        else:
            self.banner.content = ft.Text(value="Sin cambios")
            self.page.show_dialog(self.banner)



    def __init__(self):
        super().__init__()
        self.scroll=ft.ScrollMode.AUTO
        self.expand=True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER # type: ignore
        amrconfig = dict(enumerate(data.get_amr_config()))
        self.pisosconfig = data.get_pisos_config()
        self.alturap1 = ft.TextField(str(self.pisosconfig.piso1.altura), bgcolor=ft.Colors.WHITE) # type: ignore
        self.alturap2 = ft.TextField(str(self.pisosconfig.piso2.altura), bgcolor=ft.Colors.WHITE) # type: ignore
        self.txtalias = ft.TextField(amrconfig[0].alias, bgcolor=ft.Colors.WHITE)
        self.txtip = ft.TextField(amrconfig[0].ip, bgcolor=ft.Colors.WHITE)
        self.txtpuerto = ft.TextField(amrconfig[0].puerto, bgcolor=ft.Colors.WHITE) # type: ignore
        self.txtpassword = ft.TextField(amrconfig[0].password, password=True, bgcolor=ft.Colors.WHITE)
        self.banner = ft.Banner(
            leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.PRIMARY),
            content = "",
            actions=[
                ft.TextButton(
                    content = "Ocultar",
                    on_click=self.handle_banner_close # type: ignore
                )
            ],
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            open=True,
        )


        
        self.controls = [

            # ROW o COLUMN PARA INVERTIR DIRECCION
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=50,
                controls=[
                    ft.Card(
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                        elevation=20,
                        content=ft.Container(
                            padding=20,
                            width=420,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text('PISO CONFIG', weight=ft.FontWeight.W_700)
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text('ALTURA P1', weight=ft.FontWeight.W_500),
                                            self.alturap1
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text('ALTURA P2', weight=ft.FontWeight.W_500),
                                            self.alturap2
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Button(
                                                icon=ft.Icons.SAVE,
                                                content="Guardar",
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10)
                                                ),
                                                on_click=self.save_pisos_config
                                            )
                                        ]
                                    ),
                                ]
                            )
                        )

                    ),
                    ft.Card(
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                        elevation=20,
                        content=ft.Container(
                            padding=ft.Padding(right=20, left=0, top=20, bottom=20),
                            width=420,
                            content=ft.Column(
                                #alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text('AMR CONFIG', weight=ft.FontWeight.W_700)
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Text('ALIAS', weight=ft.FontWeight.W_500),
                                            self.txtalias
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Text('IP', weight=ft.FontWeight.W_500),
                                            self.txtip
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Text('PUERTO', weight=ft.FontWeight.W_500),
                                            self.txtpuerto
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Text('PASSWORD', weight=ft.FontWeight.W_500),
                                            self.txtpassword
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Checkbox("Mostrar password", on_change=self.check_pass)
                                        ]
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.Button(
                                                icon=ft.Icons.SAVE,
                                                content="Guardar",
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10)
                                                ),
                                                on_click=self.save_amr_config
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    
                    )
                ]

            )


        ]


# border=ft.Border.all(5, "#C3C6C6"),
# border_radius=10,
# padding=20,


class ventana():
    global data
    data = DataController()
    page: ft.Page
    home = Home()
    settings = Settings()

    def __init__(self, page: ft.Page):
        self.page = page
        self.window_settings()
        self.center()
        self.build()

    def window_settings(self):
        self.page.title = 'Demo'
        self.page.window.width = 1100
        self.page.window.height = 500
        self.page.window.resizable = True
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def center(self):
        page_width = self.page.width or 0
        page_height = self.page.height or 0
        window_width = self.page.window.width or 0
        window_height = self.page.window.height or 0

        self.page.window.left = (page_width // 2) - (window_width // 2)
        self.page.window.top = (page_height // 2) - (window_height // 2)

    def on_navigation_change(self,e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            self.show_home()
        elif selected_index == 1:
            self.show_settings()
        self.page.update()
            
    def show_home(self):
        self.page.controls.clear()
        self.page.add(self.home)
        
    def show_settings(self):
        self.page.controls.clear()
        self.page.add(self.settings)
    

    def build(self):
        self.page.navigation_bar = ft.NavigationBar(
                selected_index=0,
                on_change=self.on_navigation_change,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
                    ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Configuración")
                ]
            )
        self.page.add(ft.SafeArea(self.home))





if __name__ == "__main__":
    ft.run(ventana)
    
