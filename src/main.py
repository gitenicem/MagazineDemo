import flet as ft
from config.db_config import cargar_config
from helpers.timer import Timer
from controller.amrs import AmrsController
from controller.datacontroller import DataController


#@ft.control
class Home(ft.Column):
    def __init__(self):
        super().__init__()
        
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
                            #width=100,
                            height=100,
                            fit=ft.BoxFit.CONTAIN,
                        )
                    ]
                ),
            ),
            ft.Container(
                # border=ft.Border.all(1, ft.Colors.BLACK),
                # border_radius = 10,
                padding = 10,
                #bgcolor=ft.Colors.AMBER_100,

                content = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Button(icon=ft.Icons.OUTBOX,content="Entregar", on_click=self.entregar_clicked),
                        ft.Button(icon=ft.Icons.INBOX,content="Recibir", on_click=self.recibir_clicked)
                    ]
                )
            )

            
            
        ]

    def entregar_clicked(self, e):
        print("Ajecuta acción de entregar magazine")

    def recibir_clicked(self, e):
        print("Ejecuta acción de recibir magazine")
        
    

#@ft.control
class Settings(ft.Column):

    def check_pass(self,e):
         self.txtpassword.password = not e.control.value
         self.txtpassword.update()

    def save_amr_config(self, e):
         pass
    
    def __init__(self, data: DataController):
            super().__init__()
            amrconfig = dict(enumerate(data.get_amr_config()))
            self.txtpassword = ft.TextField(amrconfig[0].password, password=True)

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
                        border=ft.Border.all(2, ft.Colors.BLACK),
                        border_radius = 10,
                        padding=20,
                        bgcolor=ft.Colors.GREY_100,
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
                                        ft.TextField(amrconfig[0].alias)
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("IP", weight=ft.FontWeight.W_700),
                                        ft.TextField(amrconfig[0].ip)
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("PUERTO", weight=ft.FontWeight.W_700),
                                        ft.TextField(amrconfig[0].puerto) # type: ignore
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
                                        ft.Checkbox("Show password", on_change=self.check_pass)
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    controls=[
                                        ft.Button(icon=ft.Icons.SAVE,content="Guardar", on_click=self.save_amr_config)
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
    AmrsController.iniciar()

    page.title = "Demo"
    #await page.window.center()
    #page.window.full_screen=True
    page.update()

    # Vistas dsiponibles
    home = Home()
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
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings")
        ]
    )

    
    page.add(ft.SafeArea(home))

    
    

if __name__ == "__main__":
    ft.run(main)
