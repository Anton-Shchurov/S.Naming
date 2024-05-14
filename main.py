import requests
import pandas as pd
from io import BytesIO
import customtkinter as ctk
from PIL import Image
from typing import List, Union
import constants as ct
import os  
from pathlib import Path

# Переменные, в которые записывается выбор пользователя
selected_project = None
selected_project_short_name = None
selected_phase = None
selected_stage = list()
selected_building = list()
selected_discipline = None
selected_set = None

# Приветственный текст
hello_text = "Привет! Это программа поможет тебе получить названия файлов и элементов Civil 3D. Начни с выбора проекта, затем выбери очередь, этап, объект, раздел и комплект. Названия сформируются только если все поля выбраны. Если ты передумаешь и изменишь выбор, названия изменятся автоматически. Если решишь сбросить выбор, для этого есть кнопка внизу окна программы. Наименования формируются в соответствии с правилами, описанными на Confluence. Удачи и хорошего дня!"

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

def url_connect(url):
    try:
        # Отправляем GET-запрос к URL и автоматически закрываем сессию после получения ответа
        with requests.get(url) as response:
            # Проверяем статус ответа и генерируем исключение при неуспешном ответе
            response.raise_for_status()
            
            # Используем BytesIO для чтения из байтовой строки
            excel_data = BytesIO(response.content)
            
            # Список необходимых столбцов
            columns = ['Название объекта', 'Краткое наименование', 'Очередь', 'Этап', 'Дом']
            
            # Читаем Excel-файл, выбираем необходимую вкладку и фильтруем по столбцам
            df = pd.read_excel(excel_data, sheet_name="Сводная таблица", usecols=columns)
            
            return df
    except requests.HTTPError as e:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text=f"Ошибка HTTP: {e}")
        message_textbox.configure(state="disabled")
    except requests.ConnectionError:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text="Ошибка подключения. Пожалуйста, проверьте ваше соединение с интернетом.")
        message_textbox.configure(state="disabled")
    except Exception as e:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text=f"Произошла непредвиденная ошибка: {e}")
        message_textbox.configure(state="disabled")

def project_choice(selected_project_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_project
    global selected_project_short_name
    
    # Обновляем переменную последним выбором пользователя
    selected_project = selected_project_value
    
    # Фильтрация DataFrame по выбранному проекту
    filtered_df = dataframe[dataframe["Название объекта"] == selected_project]
    
    
    selected_project_short_name = filtered_df["Краткое наименование"].unique().tolist()
    
    # Получение уникальных очередей для выбранного проекта
    phases = filtered_df["Очередь"].unique().tolist()
    
    # Обновление выпадающего списка очередей
    phase_option_menu.configure(values=phases)
    
    generate_file_names()
    generate_element_names()

def phase_choice(selected_phase_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_phase  
    
    # Обновляем переменную последним выбором пользователя
    selected_phase = selected_phase_value  
    
    # Фильтрация DataFrame по выбранной очереди и выбранному проекту
    selected_project = project_option_menu.get()
    filtered_df = dataframe[(dataframe["Очередь"] == selected_phase) & (dataframe["Название объекта"] == selected_project)]
    
    # Получение уникальных этапов для выбранной очереди и проекта
    stages = filtered_df["Этап"].unique().tolist()
    
    # Обновление чекбоксов этапов
    stage_checkboxes.update_items(stages)
    
    generate_file_names()
    generate_element_names()
    
def stage_choice():
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_stage
    
    # Получаем список выбранных этапов
    selected_stages = stage_checkboxes.get_checked_items()
    
    # Фильтрация DataFrame по выбранным этапам, выбранному проекту и выбранной очереди
    selected_project = project_option_menu.get()
    selected_phase = phase_option_menu.get()
    
    filtered_df = dataframe[(dataframe["Этап"].isin(selected_stages)) &
                            (dataframe["Название объекта"] == selected_project) &
                            (dataframe["Очередь"] == selected_phase)]
    
    # Получение уникальных объектов для выбранных этапов, проекта и очереди
    objects = filtered_df["Дом"].unique().tolist()
    
    # Обновление списка объектов
    building_checkboxes.update_items(objects)
    
    # Запись выбора пользователя в переменную
    selected_stage = stage_checkboxes.get_checked_items()
    
    generate_file_names()
    generate_element_names()
    
def building_choice():
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_building
    
    # Запись выбора пользователя в переменную
    selected_building = building_checkboxes.get_checked_items()
    
    generate_file_names()
    generate_element_names()
    
def discipline_choice(selected_discipline_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_discipline
    
    # Обновляем переменную последним выбором пользователя
    selected_discipline = selected_discipline_value
    
    generate_file_names()
    generate_element_names()
    
def set_choice(selected_set_value):
    
    # Обеспечиваем доступ к глобальной переменной
    global selected_set
    
    # Обновляем переменную последним выбором пользователя
    selected_set = selected_set_value
    
    generate_file_names()
    generate_element_names()

def create_phase_stage_name(phase, stages):
    # Если phase является "nan", возвращаем "00"
    if phase == "nan":
        return "00"
    
    # Проверяем наличие "nan" или "-" в stages
    if any(stage in ["nan", "-"] for stage in stages):
        return [phase.split(".")[0]]
    
    # Извлекаем число до точки из phase
    phase_number = phase.split(".")[0]
    
    # Соединяем число из phase и числа из stages
    result = [f"{phase_number}.{stage}" for stage in stages]
    
    return result
    
def field_generator(elements):
    if "00" in elements:
        return "00"
    
    numeric_elements = []
    text_elements = []
    
    # Разделяем числовые и текстовые элементы
    for element in elements:
        try:
            float(element)
            numeric_elements.append(element)
        except ValueError:
            text_elements.append(element)
    
    # Сортируем числовые элементы, преобразуя их в float
    numeric_elements = sorted(numeric_elements, key=lambda x: float(x))
    
    result = []
    i = 0
    while i < len(numeric_elements):
        start = float(numeric_elements[i])
        end = start
        
        # Проверяем последовательные элементы
        while i + 1 < len(numeric_elements):
            next_number = float(numeric_elements[i + 1])
            if next_number == end + 1 or round(next_number, 1) == round(end + 0.1, 1):
                end = next_number
                i += 1
            else:
                break
        
        if start == end:
            result.append(f"{int(start)}" if start.is_integer() else f"{start}")
        elif end == start + 1 or round(end, 1) == round(start + 0.1, 1):
            result.append(f"{int(start)}" if start.is_integer() else f"{start}")
            result.append(f"{int(end)}" if end.is_integer() else f"{end}")
        else:
            start_str = f"{int(start)}" if start.is_integer() else f"{start}"
            end_str = f"{int(end)}" if end.is_integer() else f"{end}"
            result.append(f"{start_str}-{end_str}")
        
        i += 1
    
    # Добавляем текстовые элементы в конец результата
    result.extend(text_elements)
    
    return "#".join(result)    
    
def generate_file_names():
    # Проверка, что необходимые переменные заданы и списки не пусты
    if not(selected_project_short_name and selected_phase and selected_discipline and selected_set and
            selected_stage and selected_building):
        # Отображение имени файла в текстовом поле
        file_name_textbox.configure(state="normal")
        file_name_textbox.delete("1.0", "end")  # Очистка текущего текста
        file_name_textbox.insert("1.0", "Не все поля заполнены")  # Вставка нового имени файла
        file_name_textbox.configure(state="disabled")
                
    else: 
        # Создание строки с именем файла
        file_name_parts = [
            selected_project_short_name[0],
            field_generator(create_phase_stage_name(selected_phase, selected_stage)),
            field_generator(selected_building),
            selected_discipline,
            selected_set
        ]
        file_name = "_".join(file_name_parts)
        
        # Создание текста для файлов модели и листов
        model_files = "\n".join([f"{file_name}_{model_name}" for model_name in ct.MODEL_NAME])
        sheet_files = "\n".join([f"{file_name}_{sheet_name}" for sheet_name in ct.SHEET_NAME])
        
        final_text = f"Файлы модели:\n\n{model_files}\n\nФайлы листов:\n\n{sheet_files}"
        
        # Отображение имени файла в текстовом поле
        file_name_textbox.configure(state="normal")
        file_name_textbox.delete("1.0", "end")  # Очистка текущего текста
        file_name_textbox.insert("1.0", final_text)  # Вставка нового текста
        file_name_textbox.configure(state="disabled")
       
def generate_element_names():
    if not(selected_project_short_name and selected_phase and selected_discipline and selected_set and
            selected_stage and selected_building):
        element_name_textbox.configure(state="normal")
        element_name_textbox.delete("1.0", "end")
        element_name_textbox.insert("1.0", "Не все поля заполнены")
        element_name_textbox.configure(state="disabled")
    else:
        field1 = field_generator(create_phase_stage_name(selected_phase, selected_stage))
        field2 = field_generator(selected_building)
        
        # Примеры для Поле3 и Поле4 (для поверхностей)
        surface_descriptions = [
            {"Поле3": "ИИ", "Поле4": "Земля", "Описание": "Земля - существующая поверхность рельефа на весь объект, включающая в себя все участки (ИИ - инженерные изыскания)"},
            {"Поле3": "МП", "Поле4": "Проект", "Описание": "Проект - общая проектная поверхность, включающая в себя все составные поверхности проектных решений"},
            {"Поле3": "ГП", "Поле4": "Земля-ПРС", "Описание": "Земля-ПРС - поверхность снятия природно-растительного слоя"},
            {"Поле3": "ГП", "Поле4": "Земля-ИП", "Описание": "Земля-ИП - поверхность по инженерной подготовке (снятие непригодного грунта)"},
            {"Поле3": "ГП", "Поле4": "Проект", "Описание": "Проект - общая проектная поверхность, включающая в себя все составные поверхности проектных решений"}
        ]
        
        elements = []
        for desc in surface_descriptions:
            field3 = desc["Поле3"]
            field4 = desc["Поле4"]
            description = desc["Описание"]
            element_name = f'"{field1}_{field2}_{field3}_{field4}" - {description}'
            elements.append(element_name)
        
        # Создание финального текста
        final_text = "Наименования поверхностей:\n\n" + "\n\n".join(elements)
        
        # Отображение имен элементов в текстовом поле
        element_name_textbox.configure(state="normal")
        element_name_textbox.delete("1.0", "end")
        element_name_textbox.insert("1.0", final_text)
        element_name_textbox.configure(state="disabled")

def export_to_txt():
    file_name_text = file_name_textbox.get("1.0", "end").strip()  # Получаем текст из текстового поля file_name_textbox
    element_name_text = element_name_textbox.get("1.0", "end").strip()  # Получаем текст из текстового поля element_name_textbox
    
    # Определяем путь к рабочему столу пользователя
    desktop_path = str(Path.home() / "Desktop")
    
    # Создание строки с именем файла
    file_name_parts = [
            selected_project_short_name[0],
            field_generator(create_phase_stage_name(selected_phase, selected_stage)),
            field_generator(selected_building),
            selected_discipline,
            selected_set
        ]
    file_name = "_".join(file_name_parts)
    
    # Определяем путь к файлу
    file_path = os.path.join(desktop_path, f"{file_name}_Названия.txt")
    
    # Записываем текст в файл
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Названия файлов:\n")
        file.write(file_name_text + "\n\n")
        file.write("Названия элементов:\n")
        file.write(element_name_text + "\n")
    
    message_textbox.configure(state="normal")
    message_textbox.delete("1.0", "end")
    message_textbox.insert("1.0", text=f"Файл успешно сохранен на рабочий стол: {file_path}")
    message_textbox.configure(state="disabled")

def reset_selection():
    global selected_project, selected_project_short_name, selected_phase
    global selected_stage, selected_building, selected_discipline, selected_set
    
    # Сброс переменных
    selected_project = None
    selected_project_short_name = None
    selected_phase = None
    selected_stage = list()
    selected_building = list()
    selected_discipline = None
    selected_set = None

    # Сброс интерфейсных компонентов
    project_option_menu.set("Выберите проект")
    phase_option_menu.set("Выберите проект")
    discipline_option_menu.set("Выберите раздел")
    set_option_menu.set("Выберите комплект")
    stage_checkboxes.update_items(["Выберите очередь"])
    building_checkboxes.update_items(["Выберите этап"])

    # Очистка текстовых полей
    file_name_textbox.configure(state="normal")
    file_name_textbox.delete("1.0", "end")
    file_name_textbox.insert("1.0", "Не все поля заполнены")
    file_name_textbox.configure(state="disabled")

    element_name_textbox.configure(state="normal")
    element_name_textbox.delete("1.0", "end")
    element_name_textbox.insert("1.0", "Не все поля заполнены")
    element_name_textbox.configure(state="disabled")
    
    message_textbox.configure(state="normal")
    message_textbox.delete("1.0", "end")
    message_textbox.insert("1.0", text=hello_text)
    message_textbox.configure(state="disabled")

# Получение списка полей из файла Excel
dataframe = url_connect(ct.URL)

# Преобразование всех столбцов DataFrame в строковый тип
dataframe = dataframe.astype(str)

# Получение названий всех объектов
project_names = dataframe["Название объекта"].unique().tolist()

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
message_textbox.insert("1.0", text=hello_text)
message_textbox.configure(state="disabled")

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

# Кнопка "Выгрузить в файл TXT"
export_txt = ctk.CTkButton(master=app, text="Выгрузить в TXT", font=("CoFo Sans Medium", 24), command=export_to_txt)
export_txt.grid(row=5, column=0, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

# Кнопка "Сбросить выбор"
reset_button = ctk.CTkButton(master=app, text="Сбросить выбор", font=("CoFo Sans Medium", 24), command=reset_selection)
reset_button.grid(row=5, column=2, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

# Запуск приложения
if __name__ == "__main__":
    app.mainloop()