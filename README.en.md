# Python Planner - Task Management Application

Python Planner is a desktop application for managing your tasks. It enables you to:
- **Add, edit, and delete tasks** – efficiently manage your task list.
- **Calendar integration** – visualize task deadlines using an integrated calendar.
- **Mark tasks as completed** – easily indicate finished tasks.
- **Sort tasks by date** – organize tasks in chronological order.
- **Notifications and system tray support** – receive reminders and quickly access key features via a system tray icon.

## Features

- **User Interface:**  
  Built with `tkinter` and `ttk` for a clean, intuitive interface.
  
- **Calendar:**  
  Integrated with `tkcalendar`, allowing users to view tasks in the context of a calendar for improved planning.
  
- **System Tray:**  
  The application minimizes to the system tray, offering quick access to upcoming tasks and notifications.

- **Task Storage:**  
  Tasks are saved to and loaded from a `tasks.json` file, ensuring data persists between sessions.

## Technologies

- **Python 3**
- **Tkinter** – for building the graphical user interface.
- **tkcalendar** – for calendar integration.
- **pystray** – for system tray support.
- **Pillow (PIL)** – for image processing.
- **JSON** – for data storage.

## How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Gulwe/Python-Planner
    ```
2. **Install the required libraries:**
    ```bash
    pip install tkcalendar pystray pillow
    ```
3. **Run the application:**
    ```bash
    python planner.py
    ```

![image](https://github.com/user-attachments/assets/201fc253-d2a3-45e0-85ca-d0dfef06ad1b)
