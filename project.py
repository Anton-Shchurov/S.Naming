import requests
import pandas as pd
from io import BytesIO
import customtkinter as ctk
from PIL import Image
from typing import List, Union
import constants as ct
import os
from pathlib import Path

# Variables to store user selection
selected_project = None
selected_project_short_name = None
selected_phase = None
selected_stage = list()
selected_building = list()
selected_discipline = None
selected_set = None

# Welcome text
hello_text = "Hello! This program will help you get the names of Civil 3D files and elements. Start by selecting a project, then choose phase, stage, building, discipline, and set. Names will only be generated if all fields are selected. If you change your mind and make a different choice, the names will automatically update. If you decide to reset your selection, there is a button at the bottom of the program window. Names are generated according to the rules described on Confluence. The result can be exported to a TXT file on the desktop. Good luck and have a nice day!"

# Creating a class for a list with checkboxes
class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkbox_list = []
        self.checked_items = []
        for item in item_list:
            self.add_item(item)

    def add_item(self, item):
        checkbox = ctk.CTkCheckBox(self, text=item)
        # Update command to include state-saving logic
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
        self.checked_items.clear()
        for item in items:
            self.add_item(item)

    def get_checked_items(self):
        return self.checked_items

    def clear_checked_items(self):
        self.checked_items.clear()
        for checkbox in self.checkbox_list:
            checkbox.deselect()

def url_connect(url):
    try:
        # Send a GET request to the URL and automatically close the session after receiving the response
        with requests.get(url) as response:
            # Check response status and raise an exception for unsuccessful responses
            response.raise_for_status()

            # Use BytesIO to read from a byte string
            excel_data = BytesIO(response.content)

            # List of necessary columns
            columns = ['Project Name', 'Short Name', 'Phase', 'Stage', 'Building']

            # Read the Excel file, select the necessary sheet, and filter by columns
            df = pd.read_excel(excel_data, sheet_name="Summary Table", usecols=columns)

            return df
    except requests.HTTPError as e:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text=f"HTTP Error: {e}")
        message_textbox.configure(state="disabled")
    except requests.ConnectionError:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text="Connection error. Please check your internet connection.")
        message_textbox.configure(state="disabled")
    except Exception as e:
        message_textbox.configure(state="normal")
        message_textbox.delete("1.0", "end")
        message_textbox.insert("1.0", text=f"An unexpected error occurred: {e}")
        message_textbox.configure(state="disabled")

def project_choice(selected_project_value):

    # Ensure access to global variables
    global selected_project, selected_project_short_name, selected_stage, selected_building

    # Update variable with the latest user choice
    selected_project = selected_project_value

    # Filter DataFrame by the selected project
    filtered_df = dataframe[dataframe["Project Name"] == selected_project]

    selected_project_short_name = filtered_df["Short Name"].unique().tolist()

    # Get unique phases for the selected project
    phases = filtered_df["Phase"].unique().tolist()

    # Update the phase dropdown list
    phase_option_menu.configure(values=phases)

    # Clear the checkboxes for stages and buildings
    selected_stage = list()
    selected_building = list()

    generate_file_names()
    generate_element_names()

def phase_choice(selected_phase_value):
    global selected_phase, selected_stage, selected_building

    # Update variable with the latest user choice
    selected_phase = selected_phase_value

    # Reset stages and buildings when a new phase is selected
    selected_stage = list()
    selected_building = list()

    # Filter DataFrame by the selected phase and project
    selected_project = project_option_menu.get()
    filtered_df = dataframe[(dataframe["Phase"] == selected_phase) & (dataframe["Project Name"] == selected_project)]

    # Get unique stages for the selected phase and project
    stages = filtered_df["Stage"].unique().tolist()

    # Update the checkboxes for stages
    stage_checkboxes.update_items(stages)

    # Clear the checkboxes for buildings
    building_checkboxes.update_items([])

    generate_file_names()
    generate_element_names()

def stage_choice():
    global selected_stage, selected_building

    # Get the list of selected stages
    selected_stages = stage_checkboxes.get_checked_items()

    # Reset buildings when a new stage is selected
    selected_building = list()

    # Filter DataFrame by the selected stages, project, and phase
    selected_project = project_option_menu.get()
    selected_phase = phase_option_menu.get()

    filtered_df = dataframe[(dataframe["Stage"].isin(selected_stages)) &
                            (dataframe["Project Name"] == selected_project) &
                            (dataframe["Phase"] == selected_phase)]

    # Get unique buildings for the selected stages, project, and phase
    buildings = filtered_df["Building"].unique().tolist()

    # Update the building list
    building_checkboxes.update_items(buildings)

    # Save user choice to the variable
    selected_stage = stage_checkboxes.get_checked_items()

    generate_file_names()
    generate_element_names()

def building_choice():

    # Ensure access to global variable
    global selected_building

    # Save user choice to the variable
    selected_building = building_checkboxes.get_checked_items()

    generate_file_names()
    generate_element_names()

def discipline_choice(selected_discipline_value):

    # Ensure access to global variable
    global selected_discipline

    # Update variable with the latest user choice
    selected_discipline = selected_discipline_value

    generate_file_names()
    generate_element_names()

def set_choice(selected_set_value):

    # Ensure access to global variable
    global selected_set

    # Update variable with the latest user choice
    selected_set = selected_set_value

    generate_file_names()
    generate_element_names()

def create_phase_stage_name(phase, stages):
    # If phase is "nan", return "00"
    if phase == "nan":
        return "00"

    # Check for "nan" or "-" in stages
    if any(stage in ["nan", "-"] for stage in stages):
        return [phase.split(".")[0]]

    # Extract number before the dot from phase
    phase_number = phase.split(".")[0]

    # Combine the number from phase and the numbers from stages
    result = [f"{phase_number}.{stage}" for stage in stages]

    return result

def field_generator(elements):
    if "00" in elements:
        return "00"

    numeric_elements = []
    text_elements = []

    # Separate numeric and text elements
    for element in elements:
        try:
            float(element)
            numeric_elements.append(element)
        except ValueError:
            text_elements.append(element)

    # Sort numeric elements, converting them to float
    numeric_elements = sorted(numeric_elements, key=lambda x: float(x))

    result = []
    i = 0
    while i < len(numeric_elements):
        start = float(numeric_elements[i])
        end = start

        # Check for consecutive elements
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

    # Add text elements to the end of the result
    result.extend(text_elements)

    return "#".join(result)

def generate_file_names():
    # Check that necessary variables are set and lists are not empty
    if not(selected_project_short_name and selected_phase and selected_discipline and selected_set and
            selected_stage and selected_building):
        # Display file name in the text box
        file_name_textbox.configure(state="normal")
        file_name_textbox.delete("1.0", "end")
        file_name_textbox.insert("1.0", "Not all fields are filled")
        file_name_textbox.configure(state="disabled")

    else:
        # Create a string with the file name
        file_name_parts = [
            selected_project_short_name[0],
            field_generator(create_phase_stage_name(selected_phase, selected_stage)),
            field_generator(selected_building),
            selected_discipline,
            selected_set
        ]
        file_name = "_".join(file_name_parts)

        # Create text for model and sheet files
        model_files = "\n".join([f"{file_name}_{model_name}" for model_name in ct.MODEL_NAME])
        sheet_files = "\n".join([f"{file_name}_{sheet_name}" for sheet_name in ct.SHEET_NAME])

        final_text = f"Model files:\n\n{model_files}\n\nSheet files:\n\n{sheet_files}"

        # Display file name in the text box
        file_name_textbox.configure(state="normal")
        file_name_textbox.delete("1.0", "end")
        file_name_textbox.insert("1.0", final_text)
        file_name_textbox.configure(state="disabled")

def generate_element_names():
    if not(selected_project_short_name and selected_phase and selected_discipline and selected_set and
            selected_stage and selected_building):
        element_name_textbox.configure(state="normal")
        element_name_textbox.delete("1.0", "end")
        element_name_textbox.insert("1.0", "Not all fields are filled")
        element_name_textbox.configure(state="disabled")
    else:
        field1 = field_generator(create_phase_stage_name(selected_phase, selected_stage))
        field2 = field_generator(selected_building)

        # Examples for Field3 and Field4 (for surfaces)
        surface_descriptions = [
            {"Field3": "EG", "Field4": "Existing Ground", "Description": "Earth - existing terrain surface for the entire project, including all sections (II - engineering surveys)"},
            {"Field3": "MP", "Field4": "Proposal", "Description": "Project - overall project surface, including all composite design surfaces"},
            {"Field3": "LD", "Field4": "Earth-PRS", "Description": "Earth-PRS - surface for removal of natural vegetation layer"},
            {"Field3": "LD", "Field4": "Earth-IP", "Description": "Earth-IP - surface for engineering preparation (removal of unsuitable soil)"},
            {"Field3": "LD", "Field4": "Proposal", "Description": "Project - overall project surface, including all composite design surfaces"}
        ]

        elements = []
        for desc in surface_descriptions:
            field3 = desc["Field3"]
            field4 = desc["Field4"]
            description = desc["Description"]
            element_name = f'"{field1}_{field2}_{field3}_{field4}" - {description}'
            elements.append(element_name)

        # Create final text
        final_text = "Surface names:\n\n" + "\n\n".join(elements)

        # Display element names in the text box
        element_name_textbox.configure(state="normal")
        element_name_textbox.delete("1.0", "end")
        element_name_textbox.insert("1.0", final_text)
        element_name_textbox.configure(state="disabled")

def export_to_txt():
    file_name_text = file_name_textbox.get("1.0", "end").strip()  # Get text from the file_name_textbox
    element_name_text = element_name_textbox.get("1.0", "end").strip()  # Get text from the element_name_textbox

    # Define the path to the user's desktop
    desktop_path = str(Path.home() / "Desktop")

    # Create a string with the file name
    file_name_parts = [
            selected_project_short_name[0],
            field_generator(create_phase_stage_name(selected_phase, selected_stage)),
            field_generator(selected_building),
            selected_discipline,
            selected_set
        ]
    file_name = "_".join(file_name_parts)

    # Define the path to the file
    file_path = os.path.join(desktop_path, f"{file_name}_Names.txt")

    # Write text to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("File names:\n")
        file.write(file_name_text + "\n\n")
        file.write("Element names:\n")
        file.write(element_name_text + "\n")

    message_textbox.configure(state="normal")
    message_textbox.delete("1.0", "end")
    message_textbox.insert("1.0", text=f"The file was successfully saved to the desktop: {file_path}")
    message_textbox.configure(state="disabled")

def reset_selection():
    global selected_project, selected_project_short_name, selected_phase
    global selected_stage, selected_building, selected_discipline, selected_set

    # Reset variables
    selected_project = None
    selected_project_short_name = None
    selected_phase = None
    selected_stage = list()
    selected_building = list()
    selected_discipline = None
    selected_set = None

    # Reset interface components
    project_option_menu.set("Select project")
    phase_option_menu.set("Select phase")
    discipline_option_menu.set("Select discipline")
    set_option_menu.set("Select set")

    # Clear the checkboxes for stages and buildings
    stage_checkboxes.update_items([])
    stage_checkboxes.clear_checked_items()
    building_checkboxes.update_items([])
    building_checkboxes.clear_checked_items()

    # Clear text boxes
    file_name_textbox.configure(state="normal")
    file_name_textbox.delete("1.0", "end")
    file_name_textbox.insert("1.0", "Not all fields are filled")
    file_name_textbox.configure(state="disabled")

    element_name_textbox.configure(state="normal")
    element_name_textbox.delete("1.0", "end")
    element_name_textbox.insert("1.0", "Not all fields are filled")
    element_name_textbox.configure(state="disabled")

    message_textbox.configure(state="normal")
    message_textbox.delete("1.0", "end")
    message_textbox.insert("1.0", text=hello_text)
    message_textbox.configure(state="disabled")

def main():
    global dataframe, project_option_menu, phase_option_menu, discipline_option_menu, set_option_menu
    global stage_checkboxes, building_checkboxes, file_name_textbox, element_name_textbox, message_textbox

    # Get the list of fields from the Excel file
    dataframe = url_connect(ct.URL)

    # Convert all DataFrame columns to string type
    dataframe = dataframe.astype(str)

    # Get the names of all projects
    project_names = dataframe["Project Name"].unique().tolist()

    # Program color scheme settings
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Initialize the main window
    app = ctk.CTk()
    app.title("S.Naming")
    app.geometry("1080x720")
    app.minsize(1080, 720)

    # Configure the grid
    columns = 4
    rows = 5
    for i in range(rows):
        app.grid_rowconfigure(i, weight=1)
    for j in range(columns):
        app.grid_columnconfigure(j, weight=1, minsize=270)

    # Create a text box for messages
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

    # Text box to display file names
    file_name_textbox = ctk.CTkTextbox(master=app,
                                    height=150,
                                    font=ct.FONT,
                                    corner_radius=ct.CORNER_RADIUS,
                                    border_width=ct.BORDER_WIDTH,
                                    border_color=ct.BLUE_COLOR,
                                    wrap=ct.WRAP,
                                    )
    file_name_textbox.grid(row=3, column=0, columnspan=2, rowspan=2, sticky=ct.STICKY_ALL, padx=40, pady=(40, 10))

    # Text box to display element names
    element_name_textbox = ctk.CTkTextbox(master=app,
                                        height=150,
                                        font=ct.FONT,
                                        corner_radius=ct.CORNER_RADIUS,
                                        border_width=ct.BORDER_WIDTH,
                                        border_color=ct.BLUE_COLOR,
                                        wrap=ct.WRAP,
                                        )
    element_name_textbox.grid(row=3, column=2, columnspan=2, rowspan=2, sticky=ct.STICKY_ALL, padx=40, pady=(40, 10))

    # Insert image of Quokka 
    kwokka_image = ctk.CTkImage(Image.open("C:/Users/Shchurov/Хранилище/Документы/02_Программирование/CS50_Python/Final Project/Kwokka.png"), size=(171, 150))
    kwokka_image_label = ctk.CTkLabel(master=app, text="", image=kwokka_image)
    kwokka_image_label.grid(row=0, column=3, padx=(0, 80), pady=ct.PADY_LABEL)
    
    # Labels for various fields
    project_label = ctk.CTkLabel(master=app, text="Project", font=ct.FONT)
    project_label.grid(row=1, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    phase_label = ctk.CTkLabel(master=app, text="Phase", font=ct.FONT)
    phase_label.grid(row=1, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    stage_label = ctk.CTkLabel(master=app, text="Stage", font=ct.FONT)
    stage_label.grid(row=1, column=2, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    building_label = ctk.CTkLabel(master=app, text="Building", font=ct.FONT)
    building_label.grid(row=1, column=3, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    discipline_label = ctk.CTkLabel(master=app, text="Discipline", font=ct.FONT)
    discipline_label.grid(row=2, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    set_label = ctk.CTkLabel(master=app, text="Set", font=ct.FONT)
    set_label.grid(row=2, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_LABEL, pady=ct.PADY_LABEL)

    element_names_label = ctk.CTkLabel(master=app, text="Element names", font=ct.FONT)
    element_names_label.grid(row=3, column=2, columnspan=2, sticky=ct.STICKY_UP, padx=0, pady=0)

    file_names_label = ctk.CTkLabel(master=app, text="File names", font=ct.FONT)
    file_names_label.grid(row=3, column=0, columnspan=2, sticky=ct.STICKY_UP, padx=0, pady=0)

    # Dropdown menus
    project_option_menu = ctk.CTkOptionMenu(master=app, values=project_names, font=ct.FONT, command=project_choice)
    project_option_menu.grid(row=1, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

    phase_option_menu = ctk.CTkOptionMenu(master=app, values=["Select project"], font=ct.FONT, command=phase_choice)
    phase_option_menu.grid(row=1, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

    discipline_option_menu = ctk.CTkOptionMenu(master=app, values=ct.DISCIPLINE, font=ct.FONT, command=discipline_choice)
    discipline_option_menu.grid(row=2, column=0, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

    set_option_menu = ctk.CTkOptionMenu(master=app, values=ct.SET, font=ct.FONT, command=set_choice)
    set_option_menu.grid(row=2, column=1, sticky=ct.STICKY_UP, padx=ct.PADX_OPTMENU, pady=ct.PADY_OPTMENU)

    # Checkboxes in dropdown lists
    stage_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Select phase"], command=stage_choice)
    stage_checkboxes.grid(row=1, column=2, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

    building_checkboxes = ScrollableCheckBoxFrame(master=app, item_list=["Select stage"], command=building_choice)
    building_checkboxes.grid(row=1, column=3, rowspan=2, sticky=ct.STICKY_ALL, padx=ct.PADX_CHECKBOX, pady=ct.PADY_CHECKBOX)

    # Button "Export to TXT"
    export_txt = ctk.CTkButton(master=app, text="Export to TXT", font=("CoFo Sans Medium", 24), command=export_to_txt)
    export_txt.grid(row=5, column=0, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

    # Button "Reset selection"
    reset_button = ctk.CTkButton(master=app, text="Reset selection", font=("CoFo Sans Medium", 24), command=reset_selection)
    reset_button.grid(row=5, column=2, columnspan=2, sticky="EW", padx=150, pady=(10, 20))

    app.mainloop()

# Run the application
if __name__ == "__main__":
    main()
