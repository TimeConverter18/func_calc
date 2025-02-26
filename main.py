import flet as ft
import re

class FuncCard:
    def __init__(self):
        self.name = None
        self.func = None
        self.nickname = None

def main(page:ft.Page):
    def add_new_function_card(event):
        new_obj = FuncCard()
        func_cards_column.controls.append(new_obj)


    page.title = 'Калькулятор функций'

    page.fonts = {"simple":"fonts\\simple.otf", "bold":"fonts\\bold.otf"}

    page.window.width = 700
    page.window.height = 1000
    page.window.min_width = 480

    top_text = ft.Text(value='Калькулятор функций', size=35, text_align=ft.TextAlign.CENTER, font_family='simple')
    add_func_button = ft.IconButton(icon=ft.Icons.ADD_BOX, icon_size=35, icon_color=ft.Colors.GREEN, on_click=add_new_function_card)

    func_cards_column = ft.Column(alignment=ft.MainAxisAlignment.CENTER)

    page.add(
        ft.Row([ft.Container(), top_text, add_func_button], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        func_cards_column
    )
    page.update()


page = ft.app(target=main, assets_dir='assets')