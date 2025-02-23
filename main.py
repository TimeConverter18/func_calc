import flet as ft
import re

def main(page:ft.Page):
    page.title = 'Калькулятор функций'
    page.window.width = 800
    page.window.height = 1000
    page.update()

page = ft.app(target=main)