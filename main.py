import sqlite3

connection = sqlite3.connect('functions.data', check_same_thread=False)
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS DATAFUNC (
name TEXT NOT NULL,
func TEXT NOT NULL,
nickname TEXT NOT NULL
)''')

import flet as ft
import re
from PIL import ImageFont, ImageDraw, Image

def print_data(get=False):
    cursor.execute('SELECT * FROM DATAFUNC')
    users = cursor.fetchall()
    if get:
        return users
    else:
        print(users)

def check_data(column, string):
    cursor.execute(f'SELECT COUNT({column}) FROM DATAFUNC WHERE {column} = ?', (string,))
    count = cursor.fetchone()
    return int(count[0])

class FuncCard(ft.Column):
    name, func, nickname = (None,)*3

    def rewrite_func(self, func):
        def replace_match(match):
            if match.group(0).isalpha():
                number = match.group(1)  # Наше пустое число
                letters = match.group(4)  # Захваченные буквы
            else:
                number = match.group(2)  # Захваченное число
                letters = match.group(3)  # Захваченные буквы

            letters = '*'.join(letters)

            if number:
                return f'({number}*{letters})'
            else:
                return f'({letters})'

        func = f'({re.sub(r'((\d+)([a-z]+))|([a-z]{2,})', replace_match, func)})'  # 1, замена 4ac; ac
        func = func.replace(')(', ')*(')  # 2, замена )(
        func = func.replace('^', '**')  # 3, замена ^
        func = re.sub(r'(\d+)\(', r'\1*(', func)  # 4, замена 4(
        func = re.sub(r'([a-z])\(', r'\1*(', func)  # 5, замена b(
        self.rewrited_func = func

    def pre_solve(self, e):
        self.xyz = tuple(set(re.findall(r'[a-z]', self.rewrited_func)))
        self.xyz = sorted(self.xyz, key=ord)
        self.pre_solve_row.controls = []
        if self.xyz:
            for x in self.xyz:
                self.pre_solve_row.controls.append(ft.TextField(label=x, max_length=5, width=50, dense=True, input_filter=ft.InputFilter('^[0-9|-]{0,5}$')))
            self.pre_solve_row.controls += [self.final_count_button, self.to_menu_button]
            self.controls = [self.pre_solve_row]
            self.page.update()
        else:
            self.solve()
            self.page.update()

    def solve(self, e=None):
        if self.xyz:
            final_rewrited_func = self.rewrited_func
            for i in range(0, len(self.xyz)):
                final_rewrited_func = final_rewrited_func.replace(self.xyz[i], self.pre_solve_row.controls[i].value)
            self.xyz = None
            self.result_text.value = eval(final_rewrited_func)
        else:
            self.result_text.value = eval(self.rewrited_func)
        self.controls = [self.solved_row]
        self.page.update()

    def graph(self, e):
        pass

    def to_menu(self, e):
        self.xyz = None
        self.controls = [self.main_row]
        self.page.update()

    def save(self, e):
        name = self.edit_name_tf.value
        func = self.edit_func_tf.value
        nickname = self.edit_nickname_tf.value.upper()
        if name and func and nickname and ((not check_data('name',name) and self.name!=name) or (check_data('name', name) == 1 and self.name==name)) and ((not check_data('nickname',nickname) and self.nickname!=nickname) or (check_data('nickname', nickname) == 1 and self.nickname==nickname)):
            if check_data('name', name) and self.name==name:
                cursor.execute(f'DELETE FROM DATAFUNC WHERE name="{name}"')
            elif check_data('name', self.name) and self.name!=name and self.name:
                cursor.execute(f'DELETE FROM DATAFUNC WHERE name="{self.name}"')
            cursor.execute('INSERT INTO DATAFUNC (name, func, nickname) VALUES (?, ?,?)', (name, func, nickname))
            connection.commit()
            print_data()
            self.func_text.value = f'{name}: {func}'
            self.nickname_text.value = f'{nickname}()'
            self.controls = [self.main_row]
            self.text_width_func(self)
            self.rewrite_func(func)
            self.xyz = tuple(set(re.findall(r'[a-z]', self.rewrited_func)))
            exec(f'def {nickname}{str(self.xyz).replace('\'', '')}:\n\treturn {self.rewrited_func}', globals())
            self.name = name
            self.func = func
            self.nickname = nickname
            self.page.update()
        else:
            pass

    def edit(self, e):
        self.controls = [self.edit_row]
        name = self.func_text.value.split(': ')[0]
        func = self.func_text.value.split(': ')[1]
        nickname = self.nickname_text.value[0]
        self.edit_name_tf.value = name
        self.edit_func_tf.value = func
        self.edit_nickname_tf.value = nickname
        self.page.update()

    def final_delete(self, e):
        self.controls = []
        self.visible = False
        self.clean()
        cursor.execute(f'DELETE FROM DATAFUNC WHERE name="{self.name}"')
        connection.commit()
        print_data()
        self.page.update()

    def cancel_delete(self, e):
        self.controls = [self.edit_row]
        self.page.update()

    def delete(self, e):
        self.controls = [self.del_row]
        self.page.update()

    def __init__(self, text_width_func, name=None, func=None, nickname=None):
        super().__init__()
        self.xyz = None
        self.rewrited_func = None
        self.text_width_func = text_width_func
        self.horizontal_alignment = ft.MainAxisAlignment.CENTER

        self.func_text = ft.Text(value=self.func, text_align=ft.TextAlign.CENTER, selectable=True, size=20, max_lines=1, font_family='simple')
        self.nickname_text = ft.Text(value=self.nickname, width=30, text_align=ft.TextAlign.CENTER, size=20, font_family='simple')
        self.make_graph_button = ft.IconButton(icon=ft.Icons.AUTO_GRAPH_ROUNDED, tooltip=ft.Tooltip('Построить график', wait_duration=100))
        self.count_button = ft.IconButton(icon=ft.Icons.ARROW_RIGHT, tooltip=ft.Tooltip('Посчитать по формуле', wait_duration=100), on_click=self.pre_solve)
        self.edit_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=self.edit, tooltip=ft.Tooltip('Редактировать', wait_duration=100))

        self.edit_name_tf = ft.TextField(width=100, label='Имя', dense=True)
        self.edit_func_tf = ft.TextField(width=200, label='Функция', dense=True)
        self.edit_nickname_tf = ft.TextField(max_length=1, width=40, text_align=ft.TextAlign.CENTER, label='F', input_filter=ft.InputFilter(r'^[a-zA-Z]{0,1}$'))
        self.save_button = ft.IconButton(icon=ft.Icons.SAVE, on_click=self.save, tooltip=ft.Tooltip('Сохранить', wait_duration=100))
        self.del_button = ft.IconButton(icon=ft.Icons.DELETE, on_click=self.delete, tooltip=ft.Tooltip('Удалить', wait_duration=100))

        self.del_no_button = ft.Button('Нет', bgcolor=ft.Colors.RED, color=ft.Colors.BLACK, on_click=self.cancel_delete)
        self.del_text = ft.Text(value='Удалить?', size=17)
        self.del_yes_button = ft.Button(text='Да', bgcolor=ft.Colors.GREEN, color=ft.Colors.BLACK, on_click=self.final_delete)

        self.final_count_button = ft.IconButton(icon=ft.Icons.ARROW_RIGHT, tooltip=ft.Tooltip('Посчитать', wait_duration=100), on_click=self.solve)

        self.result_text = ft.Text(size=30, font_family='bold', text_align=ft.TextAlign.CENTER, selectable=True)
        self.to_menu_button = ft.IconButton(icon=ft.Icons.EXIT_TO_APP, on_click=self.to_menu, tooltip=ft.Tooltip('Вернуться в Меню', wait_duration=100))

        self.solved_row = ft.Row([self.result_text, self.to_menu_button], alignment=ft.MainAxisAlignment.CENTER)
        self.pre_solve_row = ft.Row([self.final_count_button, self.to_menu_button], alignment=ft.MainAxisAlignment.CENTER)
        self.main_row = ft.Row([ft.Row([self.func_text], scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER), self.nickname_text, self.make_graph_button, self.count_button, self.edit_button], visible=True, alignment=ft.MainAxisAlignment.CENTER, height=40)
        self.edit_row = ft.Row([self.edit_name_tf, self.edit_func_tf, self.edit_nickname_tf, self.save_button, self.del_button], visible=True, alignment=ft.MainAxisAlignment.CENTER, height=40)
        self.del_row = ft.Row([self.del_no_button, self.del_text, self.del_yes_button], visible=True, spacing=50, alignment=ft.MainAxisAlignment.CENTER, height=40)

        if name and func and nickname:
            self.name = name
            self.func = func
            self.nickname = nickname.upper()
            self.rewrite_func(func)
            self.xyz = tuple(set(re.findall(r'[a-z]', string=self.rewrited_func)))
            exec(f'def {self.nickname}{str(self.xyz).replace('\'', '')}:\n\treturn {self.rewrited_func}', globals())
            self.func_text.value = f'{self.name}: {self.func}'
            self.nickname_text.value = f'{self.nickname}()'
            self.controls = [self.main_row]
        else:
            self.controls = [self.edit_row]


def main(page:ft.Page):
    def measure_text_width(text, font_size, font_path='assets\\fonts\\simple.otf'):
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        width = draw.textlength(text, font=font)
        return width

    def add_new_function_card(event=None, name=None, func=None, nickname=None):
        if name and func and nickname:
            new_obj = FuncCard(text_width_func=make_func_text_width, name=name, func=func, nickname=nickname)
        else:
            new_obj = FuncCard(text_width_func=make_func_text_width)
        func_cards_column.controls.append(new_obj)
        make_func_text_width(new_obj)
        page.update()

    def make_func_text_width(el):
        if el.func_text.value:
            row = el.main_row.controls[0]
            text_width = measure_text_width(row.controls[0].value, row.controls[0].size)
            planned_width = page.width - 210
            if text_width >= planned_width - 15:
                row.width = planned_width
            else:
                row.width = text_width + 18

    def on_resize(e):
        for el in func_cards_column.controls:
            make_func_text_width(el)
        page.update()

    page.title = 'Калькулятор функций'

    page.fonts = {"simple":"fonts\\simple.otf", "bold":"fonts\\bold.otf", "baza": "fonts\\baza.ttf"}

    page.on_resized = on_resize
    page.window.width = 510
    page.window.height = 550
    page.window.min_width = 510
    page.window.min_height = 350
    page.theme = ft.Theme(font_family='simple')

    top_text = ft.Text(value='Калькулятор функций', size=40, text_align=ft.TextAlign.CENTER, font_family='baza')
    add_func_button = ft.IconButton(icon=ft.Icons.ADD_BOX, icon_size=35, icon_color=ft.Colors.GREEN, on_click=add_new_function_card)

    func_cards_column = ft.Column(expand=True, scroll=ft.ScrollMode('always'), spacing=15)

    page.add(
        ft.Row([top_text, add_func_button], alignment=ft.MainAxisAlignment.CENTER),
        func_cards_column
    )
    print_data()
    data = print_data(get=True)
    for piece in data:
        add_new_function_card(name=piece[0], func=piece[1], nickname=piece[2])
    page.update()

page = ft.app(target=main, assets_dir='assets')