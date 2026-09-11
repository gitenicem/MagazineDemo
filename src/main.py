import asyncio

import flet as ft
from config.db_config import cargar_config
from helpers.estados import EstadosPiso, EstadosAmr
from controller.amrs import AmrsController
from controller.datacontroller import DataController
from controller.manager import ManagerController as manager


class Secuencia():
    paso: int=0
    origen: bool # Determina si es piso de origen

    @classmethod
    def init(cls, origen: bool):
        cls.origen = origen
        cls.paso = 1

    @classmethod
    def next(cls):
        cls.paso+=1

    @classmethod
    def finish(cls):
        cls.paso = 0

    @classmethod
    def running(cls):
        return cls.paso!=0

    @classmethod
    def loop(cls):
        match cls.paso:
            case 1:
                if cls.origen:
                    print("[ORIGEN] Paso 1")
                    cls.next()
                else:
                    print("[DESTINO] Paso 1")
                    cls.next()
            case 2:
                if cls.origen:
                    print("[ORIGEN] Paso 2")
                    cls.next()
                else:
                    print("[DESTINO] Paso 2")
                    cls.next()
            case 3:
                if cls.origen:
                    print("[ORIGEN] Paso 3")
                    cls.next()
                else:
                    print("[DESTINO] Paso 3")
                    cls.next()
            case 4:
                if cls.origen:
                    print("[ORIGEN] Paso 4")
                    cls.next()
                else:
                    print("[DESTINO] Paso 4")
                    cls.next()
            case 5:
                if cls.origen:
                    print("[ORIGEN] Paso 5")
                    cls.next()
                else:
                    print("[DESTINO] Paso 5")
                    cls.next()
            case _:
                print("Finish")
                cls.finish()



#@ft.control
class Home(ft.Column):
    db_data = None
    automatico_activo = False

    def __init__(self, data: DataController):
        super().__init__()

        self.db_data=data
        #self.automatico_activo = False


        self.conveyor = ft.Image(
            src="conveyoroff.png",
            visible=False,
            height=200,
            fit=ft.BoxFit.CONTAIN,
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
                padding = 50,
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
        self.conveyor.src = "conveyorout.gif"
        self.conveyor.visible = True
        print("Ajecuta acción de entregar magazine")

    def recibir_clicked(self, e):
        self.conveyor.src = "conveyorin.gif"
        self.conveyor.visible = True
        print("Ejecuta acción de recibir magazine")

    def automatico_clicked(self, e):
        if self.automatico_activo:
            self.automatico_activo = False
            self.btnEntregar.disabled = False
            self.btnRecibir.disabled = False
        else:
            self.conveyor.visible = False
            self.automatico_activo = True
            self.btnEntregar.disabled = True
            self.btnRecibir.disabled = True

        #print(self.automatico_activo)


    def did_mount(self):
        self.page.run_task(self.pooling)
        self.page.run_task(self.update)

    #def will_unmount(self):
    #    self.automatico_activo = False

    
    def amr_ejecutar_entrega(self, accion:EstadosAmr, piso: int, origen: bool):
        # TODO Envía instrucción a amr
        print(f"P{piso} {accion}")
        Secuencia.init(origen)

    def amr_ejecutar_recepcion(self, accion:EstadosAmr, piso: int, origen: bool):
        # TODO Envía instrucción a amr
        print(f"P{piso} {accion}")
        Secuencia.init(origen)

    async def pooling(self):
        while True:
            if self.automatico_activo:
                try:
                    wip = self.db_data.get_estacion("WIP1") # type: ignore
                    estadoP1, estadoP2 = wip.pisos_estado.pisos.values() # type: ignore

                    if not Secuencia.running():
                        if estadoP1 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value:
                            if not Secuencia.running():
                                self.amr_ejecutar_recepcion(accion=EstadosAmr.RECIBIR.value, piso=1, origen=True) # type: ignore

                        if estadoP1 == EstadosPiso.NONE.value:
                            if not Secuencia.running():
                                self.amr_ejecutar_entrega(accion=EstadosAmr.ENTREGAR.value, piso=1, origen=False) # type: ignore

                        if estadoP2 == EstadosPiso.PREPARADO_ENTREGAR_RECIBIR.value:
                            if not Secuencia.running():
                                self.amr_ejecutar_recepcion(accion=EstadosAmr.RECIBIR.value, piso=2, origen=True) # type: ignore

                        if estadoP2 == EstadosPiso.NONE.value:
                            if not Secuencia.running():
                                self.amr_ejecutar_entrega(accion=EstadosAmr.ENTREGAR.value, piso=2, origen=False) # type: ignore

                except Exception as e:
                    print(f"Error en la consulta de BD: {e}")

            await asyncio.sleep(5)



    # Ejecuta la secuencia
    async def update(self):
        while True:
            if Secuencia.running():
                Secuencia.loop()
                await asyncio.sleep(4)
            await asyncio.sleep(1)

            
        
    

#@ft.control
class Settings(ft.Column):

    amr_config_data = None

    def check_pass(self,e):
         self.txtpassword.password = not e.control.value
         self.txtpassword.update()

    def save_amr_config(self, e):
             
        self.page._remove_dialog(self.banner)
        
        alias = self.txtalias.value
        ip = self.txtip.value
        puerto = int(self.txtpuerto.value)
        password = self.txtpassword.value
        res = self.amr_config_data.save_amr_ip_puerto(alias,ip,puerto,password) # type: ignore
        
        if res:
             self.banner.content = "Configuración guardada correctamente"
             self.page.show_dialog(self.banner)
        else:
            self.banner.content = ft.Text(value="Sin cambios")
            self.page.show_dialog(self.banner)

    def handle_banner_close(self, e: ft.Event[ft.TextButton]):
        self.page.pop_dialog()
             
    
    def __init__(self, data: DataController):
            super().__init__()
            self.amr_config_data = data
            amrconfig = dict(enumerate(data.get_amr_config()))
            self.txtalias = ft.TextField(amrconfig[0].alias, bgcolor=ft.Colors.WHITE)
            self.txtip = ft.TextField(amrconfig[0].ip, bgcolor=ft.Colors.WHITE)
            self.txtpuerto = ft.TextField(amrconfig[0].puerto, bgcolor=ft.Colors.WHITE) # type: ignore
            self.txtpassword = ft.TextField(amrconfig[0].password, password=True, bgcolor=ft.Colors.WHITE)
            self.banner = ft.Banner(
                leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.PRIMARY),
                content = "",
                actions=[
                    ft.TextButton(
                        content = "Dismiss",
                        on_click=self.handle_banner_close # type: ignore
                    )
                ],
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                open=True,
            )

            self.controls = [
                 ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Container(
                         content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            spacing=15,
                            controls=[
                                 ft.Text("AMR_CONFIG", weight=ft.FontWeight.W_700)
                            ]
                         )
                    )
                 ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),  # Centrado absoluto válido en Flet moderno (0,0 es el centro)
                    content=ft.Container(
                        border=ft.Border.all(1, ft.Colors.SECONDARY),
                        border_radius = 10,
                        padding=20,
                        #bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        width=450,
                        content=ft.Column(
                            # SOLUCIÓN: El alineamiento horizontal correcto para Columnas en la nueva versión
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            spacing=15,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("ALIAS", weight=ft.FontWeight.W_700),
                                        self.txtalias
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("IP", weight=ft.FontWeight.W_700),
                                        self.txtip
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("PUERTO", weight=ft.FontWeight.W_700),
                                        self.txtpuerto
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("PASSWORD", weight=ft.FontWeight.W_700),
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
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
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
            




async def main(page: ft.Page):
    cargar_config()
    data = DataController()
    #AmrsController.iniciar()

    page.title = "Demo"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.SECONDARY)
    #await page.window.center()
    #page.window.full_screen=True
    page.update()

    # Vistas dsiponibles
    home = Home(data=data)
    settings = Settings(data=data)
    
    def on_navigation_change(e):
            selected_index = e.control.selected_index
            if selected_index == 0:
                show_home()
            elif selected_index == 1:
                show_settings()
            page.update()
            
    def show_home():
        page.controls.clear()
        page.add(home)
        
    def show_settings():
        page.controls.clear()
        page.add(settings)

    page.navigation_bar = ft.NavigationBar(
        selected_index=1,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Configuración")
        ]
    )

    page.add(ft.SafeArea(home))

    
    

if __name__ == "__main__":
    ft.run(main)
    
