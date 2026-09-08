import flet as ft
from model.data import DataAccess
from helpers.config import cargar_config


@ft.control
class Demo(ft.Column):
    def init(self):
        self.controls = [
            ft.Container(
                bgcolor=ft.Colors.AMBER_100,
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



def main(page: ft.Page):

    page.title = "Demo"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    demo = Demo()
    page.add(
        ft.SafeArea(
            demo,
            expand=True
        ))

    
    

if __name__ == "__main__":
    cargar_config()
    data = DataAccess()
    ft.run(main)
