import flet as ft
from model.data import DataAccess
from helpers.config import cargar_config


@ft.control
class Demo(ft.Column):
    def init(self):
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
        
    

@ft.control
class Settings(ft.Column):
    def init(self):
            self.controls = [
                ft.Container(
                    padding = 10,
                    content = ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Settings", size= 30)
                        ]
                    ),
                )
            ]


def main(page: ft.Page):

    page.title = "Demo"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()
    
    demo = Demo()
    settings = Settings()
    
    def on_navigation_change(e):
            selected_index = e.control.selected_index
            if selected_index == 0:
                show_home()
            elif selected_index == 1:
                show_settings()
            
            page.update()
            
    def show_home():
        page.controls.clear()
        page.add(demo)
        
    def show_settings():
        page.controls.clear()
        page.add(settings)

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings")
        ]
    )

    
    page.add(
        ft.SafeArea(
            demo
        ))

    
    

if __name__ == "__main__":
    cargar_config()
    data = DataAccess()
    ft.run(main)
