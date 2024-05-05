import customtkinter as ctk
from PIL import Image
import data_base as db
import constants as ct

# Получение списка полей из файла Excel
dataframe = db.url_connect(ct.URL)

# Преобразование всех столбцов DataFrame в строковый тип
dataframe = dataframe.astype(str)

# Получение названий всех объектов
project_names = dataframe["Название объекта"].unique().tolist()

# Переменне, в которые записывается выбор пользователя
selected_project = None
selected_project_short_name = None
selected_phase = None
selected_stage = list()
selected_building = list()
selected_discipline = None
selected_set = None

# Создание класса списка с чек-боксами
class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkbox_list = []
        self.checked_items = []  # список для сохранения выбранных элементов
        for item in item_list:
            self.add_item(item)

    def add_item(self, item):
        checkbox = ctk.CTkCheckBox(self, text=item)
        # Обновление command для включения логики сохранения состояния
        checkbox.configure(command=lambda cb=checkbox: self.on_checkbox_select(cb))
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 0))
        self.checkbox_list.append(checkbox)

    def on_checkbox_select(self, checkbox):
        if checkbox.get():
            if checkbox.cget("text") not in self.checked_items:
                self.checked_items.append(checkbox.cget("text"))
        else:
            if checkbox.cget("text") in self.checked_items:
                self.checked_items.remove(checkbox.cget("text"))
        if self.command:
            self.command()

    def update_items(self, items):
        for checkbox in self.checkbox_list:
            checkbox.destroy()
        self.checkbox_list.clear()
        for item in items:
            self.add_item(item)
            
    def get_checked_items(self):
        return self.checked_items

def project_choice(selected_project_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_project
    global selected_project_short_name
    
    # Обновляем переменную последним выбором пользователя
    selected_project = selected_project_value
    
    # Фильтрация DataFrame по выбранному проекту
    filtered_df = dataframe[dataframe['Название объекта'] == selected_project]
    
    
    selected_project_short_name = filtered_df['Краткое наименование'].unique().tolist()
    
    # Получение уникальных очередей для выбранного проекта
    phases = filtered_df['Очередь'].unique().tolist()
    
    # Обновление выпадающего списка очередей
    phase_option_menu.configure(values=phases)

def phase_choice(selected_phase_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_phase  
    
    # Обновляем переменную последним выбором пользователя
    selected_phase = selected_phase_value  
    
    # Фильтрация DataFrame по выбранной очереди и выбранному проекту
    selected_project = project_option_menu.get()
    filtered_df = dataframe[(dataframe['Очередь'] == selected_phase) & (dataframe['Название объекта'] == selected_project)]
    
    # Получение уникальных этапов для выбранной очереди и проекта
    stages = filtered_df['Этап'].unique().tolist()
    
    # Обновление чекбоксов этапов
    stage_checkboxes.update_items(stages)
    
def stage_choice():
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_stage
    
    # Получаем список выбранных этапов
    selected_stages = stage_checkboxes.get_checked_items()
    
    # Фильтрация DataFrame по выбранным этапам, выбранному проекту и выбранной очереди
    selected_project = project_option_menu.get()
    selected_phase = phase_option_menu.get()
    
    filtered_df = dataframe[(dataframe['Этап'].isin(selected_stages)) &
                            (dataframe['Название объекта'] == selected_project) &
                            (dataframe['Очередь'] == selected_phase)]
    
    # Получение уникальных объектов для выбранных этапов, проекта и очереди
    objects = filtered_df['Дом'].unique().tolist()
    
    # Обновление списка объектов
    building_checkboxes.update_items(objects)
    
    # Запись выбора пользователя в переменную
    selected_stage = stage_checkboxes.get_checked_items()
    
def building_choice():
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_building
    
    # Запись выбора пользователя в переменную
    selected_building = building_checkboxes.get_checked_items()
    
def discipline_choice(selected_discipline_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_discipline
    
    # Обновляем переменную последним выбором пользователя
    selected_discipline = selected_discipline_value
    
def set_choice(selected_set_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_set
    
    # Обновляем переменную последним выбором пользователя
    selected_set = selected_set_value


# Настройки цветовой схемы программы
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Инициализация главного окна
app = ctk.CTk()
app.title("S.Naming")
app.geometry("1080x720")
app.minsize(1080, 720)

# Настройка сетки
columns = 4
rows = 5
for i in range(rows):
    app.grid_rowconfigure(i, weight=1)
for j in range(columns):
    app.grid_columnconfigure(j, weight=1, minsize=270)

# Создание текстового поля для сообщений
message_textbox = ctk.CTkTextbox(master=app,
                                 height=150,
                                 font=ct.FONT,
                                 corner_radius=ct.CORNER_RADIUS,
                                 border_width=ct.BORDER_WIDTH,
                                 border_color=ct.BLUE_COLOR,
                                 wrap=ct.WRAP,
                                 )
message_textbox.grid(row=0, column=0, columnspan=3, sticky=ct.STICKY_ALL, padx=(100, 40), pady=(25, 10))
message_textbox.insert('1.0', text='Hello, world!')
message_textbox.configure(state='disabled')

# Текстовое поле для отображения названий файлов
file_name_textbox = ctk.CTkTextbox(master=app,
                                   height=150,
                                   font=ct.FONT,
                                   corner_radius=ct.CORNER_RADIUS,
                                   border_width=ct.BORDER_WIDTH,
                                   border_color=ct.BLUE_COLOR,
                                   wrap=ct.WRAP,
                                   )
file_name_textbox.grid(row=3, column=0, columnspan=2, rowspan=2, sticky=ct.STICKY_ALL, padx=40, pady=(40, 10))

# Текстовое поле для отображения названий элементов
element_name_textbox = ctk.CTkTextbox(master=app,
                                      height=150,
                                      font=ct.FONT,
                                      corner_radius=ct.CORNER_RADIUS,
                                      border_width=ct.BORDER_WIDTH,
                                      border_color=ct.BLUE_COLOR,
                                      wrap=ct.WRAP,
                                      )
element_name_textbox.grid(row=3, column=2, columnspan=2, rowspan=2, sticky=ct.STICKY_ALL, padx=40, pady=(40, 10))

# Вставка изображения Квокки
kwokka_image = ctk.CTkImage(Image.open("Kwokka.png"), size=(171, 150))
kwokka_image_label = ctk.CTkLabel(master=app, text="", image=kwokka_image)
kwokka_image_label.grid(row=0, column=3, padx=(0, 80), pady=ct.PADY_LABEL)

# Метки для различных полей
project_label = ctk.CTkLabel(master=app, text="Проект", font=ct.FONT)
project_label.grid(row=1, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

phase_label = ctk.CTkLabel(master=app, text="Очередь", font=ct.FONT)
phase_label.grid(row=1, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

stage_label = ctk.CTkLabel(master=app, text="Этап", font=ct.FONT)
stage_label.grid(row=1, column=2, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

building_label = ctk.CTkLabel(master=app, text="Объект", font=ct.FONT)
building_label.grid(row=1, column=3, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

discipline_label = ctk.CTkLabel(master=app, text="Раздел", font=ct.FONT)
discipline_label.grid(row=2, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

set_label = ctk.CTkLabel(master=app, text="Комплект", font=ct.FONT)
set_label.grid(row=2, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

element_names_label = ctk.CTkLabel(master=app, text="Названия элементов", font=ct.FONT)
element_names_label.grid(row=3, column=2, columnspan=2, sticky=ct.STICKY_UP, padx=0, pady=0)

file_names_label = ctk.CTkLabel(master=app, text="Названия файлов", font=ct.FONT)
file_names_label.grid(row=3, column=0, columnspan=2, sticky=ct.STICKY_UP, padx=0, pady=0)

# Выпадающие списки
project_option_menu = ctk.CTkOptionMenu(master=app, values=project_names, font=ct.FONT, command=project_choice)
project_option_menu.grid(row=1, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

phase_option_menu = ctk.CTkOptionMenu(master=app, values=["Выберите проект"], font=ct.FONT, command=phase_choice)
phase_option_menu.grid(row=1, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

discipline_option_menu = ctk.CTkOptionMenu(master=app, values=ct.DISCIPLINE, font=ct.FONT, command=discipline_choice)
discipline_option_menu.grid(row=2, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

set_option_menu = ctk.CTkOptionMenu(master=app, values=ct.SET, font=ct.FONT, command=set_choice)
set_option_menu.grid(row=2, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

# Чекбоксы в выпадающих списках
stage_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Выберите очередь"], command=stage_choice)
stage_checkboxes.grid(row=1, column=2, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

building_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Выберите этап"], command=building_choice)
building_checkboxes.grid(row=1, column=3, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

# Кнопка "Сбросить выбор"
reset_button = ctk.CTkButton(master=app, text="Сбросить выбор", font=('CoFo Sans Medium', 24), command=None)
reset_button.grid(row=5, column=1, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

# Запуск приложения
if __name__ == "__main__":
    app.mainloop()