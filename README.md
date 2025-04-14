# S.Naming - Naming Generator for Civil 3D Files

#### Description:

S.Naming is a sophisticated program designed to streamline the generation of names for Civil 3D files and elements. It offers a user-friendly interface for selecting various parameters and ensures that names are generated in accordance with specified rules.

## Project Overview

This project was created to assist users in generating names for Civil 3D files based on a variety of project-specific parameters. The application uses a graphical user interface built with customtkinter, a modern alternative to Tkinter, and integrates with the pandas library for data manipulation.

## Features

- **Interactive Selection:** Users can select a project, phase, stage, building, discipline, and set from dropdown menus and checkboxes.
- **Automatic Name Generation:** Names are generated automatically when all fields are selected, ensuring consistency and accuracy.
- **Dynamic Updates:** Changes in selections update the names in real-time.
- **Export Functionality:** Generated names can be exported to a TXT file saved on the user's desktop.
- **Error Handling:** Comprehensive error handling ensures a smooth user experience even in the case of network or data issues.

## File Descriptions

- **main.py:** This is the main script that initializes the GUI, handles user interactions, and manages the name generation process.
- **constants.py:** This file contains various constants used throughout the application, such as URLs, font settings, and predefined values for dropdown menus.

## Design Choices

### GUI Framework
We chose customtkinter for its modern appearance and enhanced functionality compared to the traditional Tkinter. It provides a more intuitive and visually appealing interface, which is crucial for user interaction.

### Data Handling
The pandas library was selected for its powerful data manipulation capabilities. By using pandas, we can easily filter and process the data from Excel files, ensuring that the application remains efficient and responsive.

### Error Handling
Robust error handling is implemented to manage various scenarios, such as network errors or data inconsistencies. This ensures that users receive clear and informative messages when something goes wrong, enhancing the overall user experience.

### Modular Code
The project follows a modular design, with separate functions handling specific tasks. This not only makes the code easier to maintain and update but also improves readability and debugging.

## Usage Instructions

1. **Launch the Application:** Run the `main.py` script to start the application.
2. **Select Project:** Choose a project from the dropdown menu.
3. **Choose Phase, Stage, Building, Discipline, and Set:** Use the provided dropdown menus and checkboxes to make your selections.
4. **Generate Names:** The names will be automatically generated and displayed in the text boxes.
5. **Export to TXT:** Click the "Export to TXT" button to save the generated names to a TXT file on your desktop.
6. **Reset Selection:** Use the "Reset selection" button to clear all selections and start over.

## Future Improvements

- **Enhanced Data Source Integration:** Allowing integration with other data sources, such as databases or APIs, for more dynamic data handling.
- **User Preferences:** Implementing a system to save user preferences and selections for future sessions.
- **Advanced Error Reporting:** Providing more detailed error reports to help users troubleshoot issues.

By adhering to these design principles and functionalities, S.Naming ensures a robust and user-friendly solution for generating names for Civil 3D files, aiding in project management and organization.
