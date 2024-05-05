import customtkinter as ctk
from PIL import Image
import data_base as db
import constants as ct

# Создание класса списка с чек-боксами
class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkbox_list = []
        for item in item_list:
            self.add_item(item)

    def add_item(self, item):
        checkbox = ctk.CTkCheckBox(self, text=item)
        checkbox.configure(command=self.command)  # Привязываем команду к чекбоксу
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 0))
        self.checkbox_list.append(checkbox)

    def update_items(self, items):
        for checkbox in self.checkbox_list:
            checkbox.destroy()
        self.checkbox_list.clear()
        for item in items:
            self.add_item(item)
            
    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]

def update_phase_options(selected_project):
    # Фильтрация DataFrame по выбранному проекту
    filtered_df = dataframe[dataframe['Название объекта'] == selected_project]
    
    # Получение уникальных очередей для выбранного проекта
    phases = filtered_df['Очередь'].unique().tolist()
    
    # Обновление выпадающего списка очередей
    phase_option_menu.configure(values=phases)

def update_stage_options(selected_phase):
    # Фильтрация DataFrame по выбранной очереди и выбранному проекту
    selected_project = project_option_menu.get()
    filtered_df = dataframe[(dataframe['Очередь'] == selected_phase) & (dataframe['Название объекта'] == selected_project)]
    
    # Получение уникальных этапов для выбранной очереди и проекта
    stages = filtered_df['Этап'].unique().tolist()
    
    # Обновление чекбоксов этапов
    stage_checkboxes.update_items(stages)
    
def update_objects_by_selected_stages():
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
 
# Получение списка полей из файла Excel
dataframe = db.url_connect(ct.URL)

# Преобразование всех столбцов DataFrame в строковый тип
dataframe = dataframe.astype(str)

project_names = dataframe["Название объекта"].unique().tolist()
short_project_names = dataframe["Краткое наименование"].unique().tolist()
phase_numbers = dataframe["Очередь"].unique()
stage_numbers = dataframe["Этап"].unique().tolist()
building_numbers = dataframe["Дом"].unique().tolist()

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
project_option_menu = ctk.CTkOptionMenu(master=app, values=project_names, font=ct.FONT, command=update_phase_options)
project_option_menu.grid(row=1, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

phase_option_menu = ctk.CTkOptionMenu(master=app, values=["Выберите проект"], font=ct.FONT, command=update_stage_options)
phase_option_menu.grid(row=1, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

discipline_option_menu = ctk.CTkOptionMenu(master=app, values=ct.DISCIPLINE, font=ct.FONT)
discipline_option_menu.grid(row=2, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

set_option_menu = ctk.CTkOptionMenu(master=app, values=ct.SET, font=ct.FONT)
set_option_menu.grid(row=2, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

# Чекбоксы в выпадающих списках
stage_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Выберите очередь"], command=update_objects_by_selected_stages)
stage_checkboxes.grid(row=1, column=2, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

building_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Выберите этап"], command=None)
building_checkboxes.grid(row=1, column=3, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

# Кнопка "Сбросить выбор"
reset_button = ctk.CTkButton(master=app, text="Сбросить выбор", font=('CoFo Sans Medium', 24), command=None)
reset_button.grid(row=5, column=1, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

# Запуск приложения
if __name__ == "__main__":
    app.mainloop()
