import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, PhotoImage
from tkcalendar import Calendar
from datetime import datetime, timedelta
import json
import os

import pystray
from PIL import Image, ImageDraw
import threading

class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planner")
        self.root.geometry('1000x700')
        
        img = PhotoImage(file='app.png')
        self.root.iconphoto(False, img)
        
        # Initialize system tray related attributes
        self.icon = None
        self.tray_thread = None
        self.upcoming_tasks = []
        self.last_notification_time = datetime.now()
        
        # Add window close handler
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background='#f0f0f0')
        self.style.configure('Custom.TButton', padding=5, font=('Verdana', 10))
        
        # Create main container
        self.main_container = ttk.Frame(root, style='Custom.TFrame')
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create task section
        self.create_task_section()
        
        # Create calendar section
        self.create_calendar_section()
        
        # Create bottom button panel
        self.create_button_panel()
        
        # Load saved tasks
        self.load_tasks()
        
        # Start system tray
        self.setup_system_tray()
        
        self.sort_tasks()            
        
        # Schedule periodic task updates
        self.update_upcoming_tasks()
        self.root.after(1000, self.update_upcoming_tasks)
        self.root.after(300000, self.update_upcoming_tasks)  # Update every 5 minutes
        
        # Schedule notifications check
        self.check_notifications()
        self.root.after(1000, self.check_notifications) #Check after turning on the program
        self.root.after(60000, self.check_notifications)  # Check every minute
        
        self.root.after(5000, self.show_today_tasks)
    
        # Add these new methods for system tray functionality
    def create_tray_icon(self):
        # Load PNG file using PIL
        image = Image.open('app.png')
        # Optionally resize if needed
        image = image.resize((64, 64))
        return image
    
    def get_upcoming_tasks(self):
        tasks = []
        today = datetime.now().date()
        
        for i in range(self.listbox_tasks.size()):
            task = self.listbox_tasks.get(i)
            try:
                date_str = task.split(" - ")[0]
                try:
                    task_date = datetime.strptime(date_str, "%d/%m/%y").date()
                except ValueError:
                    task_date = datetime.strptime(date_str, "%d/%m/%YY").date()
                
                # Only include non-completed tasks within the next 7 days
                if today <= task_date <= today + timedelta(days=7) and "[Done]" not in task:
                    tasks.append((task_date, task))  # Return tuple with date and task
            except Exception as e:
                print(f"Error parsing task date: {e}")
        
        # Sort tasks by date
        return sorted(tasks, key=lambda x: x[0])


    
    def check_notifications(self):
        if self.icon and (datetime.now() - self.last_notification_time).total_seconds() > 3600:  # Check once per hour
            upcoming = self.get_upcoming_tasks()
            today = datetime.now().date()
            
            notifications = []
            
            # Check for tasks due today
            today_tasks = [task for date, task in upcoming if date == today]
            if today_tasks:
                notifications.append(f"You have {len(today_tasks)} task(s) due today!")
            
            # Check for tasks due tomorrow
            tomorrow = today + timedelta(days=1)
            tomorrow_tasks = [task for date, task in upcoming if date == tomorrow]
            if tomorrow_tasks:
                notifications.append(f"You have {len(tomorrow_tasks)} task(s) due tomorrow!")
            
            # Show notification if there are any messages
            if notifications:
                notification_text = "\n".join(notifications)
                self.icon.notify(
                    title="Upcoming Tasks Reminder",
                    message=notification_text,
                    icon=self.icon.icon
                )
                self.last_notification_time = datetime.now()

        # Schedule next check
        self.root.after(60000, self.check_notifications)  # Check every minute

    
    def create_tray_menu(self):
        upcoming = self.get_upcoming_tasks()
        menu_items = []
        
        # Add upcoming tasks to menu
        for _, task in upcoming[:5]:  # Limit to 5 tasks to avoid too long menu
            # Truncate task text if too long
            truncated_task = task[:50] + "..." if len(task) > 50 else task
            menu_items.append(pystray.MenuItem(truncated_task, lambda: None, enabled=False))
        
        if not upcoming:
            menu_items.append(pystray.MenuItem("No upcoming tasks", lambda: None, enabled=False))
        
        # Add separator and standard menu items
        menu_items.extend([
            #pystray.MenuItem("separator", None),
            pystray.MenuItem("Show Tasks Due Today", self.show_today_tasks),
            pystray.MenuItem("Show Planner", self.show_window),
            pystray.MenuItem("Exit", self.quit_app)
        ])
        
        return menu_items
    
    def show_today_tasks(self):
        today = datetime.now().date()
        upcoming = self.get_upcoming_tasks()
        today_tasks = [task for date, task in upcoming if date == today]
        
        if today_tasks:
            formatted_tasks = []
            for task in today_tasks:
                # Extract time if it exists
                if "(" in task:
                    time_str = task[task.rfind("(")+1:task.rfind(")")]
                    task_without_time = task[:task.rfind("(")].strip()
                    formatted_tasks.append(f"{time_str} - {task_without_time}")
                else:
                    formatted_tasks.append(task)
                    
            message = "Tasks due today:\n\n" + "\n".join(formatted_tasks)
        else:
            message = "No tasks due today"
            
        self.icon.notify(
            title="Today's Tasks",
            message=message
        )
    
    def setup_system_tray(self):
        def run_icon():
            self.icon = pystray.Icon(
                "PlannerApp",
                self.create_tray_icon(),
                "Planner",
                menu=pystray.Menu(*self.create_tray_menu())
            )
            self.icon.run()
        
        self.tray_thread = threading.Thread(target=run_icon)
        self.tray_thread.daemon = True
        self.tray_thread.start()
    
    def update_upcoming_tasks(self):
        if self.icon:
            # Update the menu with new upcoming tasks
            self.icon.menu = pystray.Menu(*self.create_tray_menu())
    
        # Schedule next update
        self.root.after(300000, self.update_upcoming_tasks)  # Every 5 minutes
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_app(self):
        self.root.quit()
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            if self.icon:
                self.icon.stop()
            self.root.quit()
    
    def create_task_section(self):
        # Task frame
        self.frame_tasks = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.frame_tasks.pack(side="left", fill="both", expand=True, padx=10)
        
        # Task header
        label_tasks = ttk.Label(self.frame_tasks, text="Tasks", font=('Verdana', 12, 'bold'))
        label_tasks.pack(pady=5)
        
        # Search frame
        search_frame = ttk.Frame(self.frame_tasks)
        search_frame.pack(fill="x", pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tasks)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Task list with scrollbar
        self.listbox_tasks = tk.Listbox(self.frame_tasks, width=40, height=20, 
                                      font=('Verdana', 10), selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(self.frame_tasks, orient="vertical", 
                                command=self.listbox_tasks.yview)
        self.listbox_tasks.configure(yscrollcommand=scrollbar.set)
        
        self.listbox_tasks.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.listbox_tasks.bind('<Double-Button-1>', lambda e: self.edit_task())

    def create_calendar_section(self):
        # Calendar frame
        self.frame_calendar = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.frame_calendar.pack(side="right", fill="both", expand=True, padx=10)
        
        # Calendar header
        label_calendar = ttk.Label(self.frame_calendar, text="Calendar", 
                                 font=('Verdana', 12, 'bold'))
        label_calendar.pack(pady=5)
        
        # Calendar widget
        self.calendar = Calendar(self.frame_calendar, selectmode='day', 
                               year=2025, month=1, day=3,
                               style='Custom.TCalendar',
                               date_pattern='dd/mm/yy')
        self.calendar.pack(fill="both", expand=True)     
        
        # Bind calendar selection
        self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)

    def create_button_panel(self):
        button_frame = ttk.Frame(self.root, style='Custom.TFrame')
        button_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="Add Task", command=self.add_task, 
                  style='Custom.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Task", command=self.edit_task, 
                  style='Custom.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task, 
                  style='Custom.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Mark Complete", command=self.mark_complete, 
                  style='Custom.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sort by Date", command=self.sort_tasks, 
                  style='Custom.TButton').pack(side="left", padx=5)

    def add_task(self):
        selected_date = self.calendar.get_date()
        
        # Custom dialog for task details
        dialog = TaskDialog(self.root, "Add Task")
        if dialog.result:
            title, description, priority, hour, minute = dialog.result
            
            # Create task entry
            task_text = f"{selected_date} - {title} [{priority}]: {description} ({hour}:{minute})"
            index = self.listbox_tasks.size()
            self.listbox_tasks.insert("end", task_text)
            self.apply_priority_color(index, priority)
            
            self.save_tasks()
            self.highlight_tasks()

    def edit_task(self):
        selected_idx = self.listbox_tasks.curselection()
        if not selected_idx:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return
            
        current_task = self.listbox_tasks.get(selected_idx)
        date, rest = current_task.split(" - ", 1)
        title = rest.split("[")[0].strip()
        priority = rest.split("[")[1].split("]")[0] 
        desc = rest.split("]: ")[1].strip()
        
        # Extract hour and minute if they exist
        hour = "12"  # default values
        minute = "00"
        if "(" in desc:
            time_str = desc[desc.rfind("(")+1:desc.rfind(")")]
            if ":" in time_str:
                hour, minute = time_str.split(":")
            desc = desc[:desc.rfind("(")].strip()
        #print(hour)
        #print(minute)
        
        
        dialog = TaskDialog(self.root, "Edit Task", title, desc, priority, hour, minute)
        if dialog.result:
            new_title, description, priority, hour, minute = dialog.result
            task_text = f"{date} - {new_title} [{priority}]: {description} ({hour}:{minute})"
            self.listbox_tasks.delete(selected_idx)
            self.listbox_tasks.insert(selected_idx, task_text)
            self.apply_priority_color(selected_idx, priority)
            
            self.save_tasks()
            self.highlight_tasks()

    def delete_task(self):
        selected_idx = self.listbox_tasks.curselection()
        if not selected_idx:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.listbox_tasks.delete(selected_idx)
            self.save_tasks()
            self.highlight_tasks()

    def mark_complete(self):
        selected_idx = self.listbox_tasks.curselection()
        if not selected_idx:
            messagebox.showwarning("Warning", "Please select a task to mark complete")
            return
                   
        current_task = self.listbox_tasks.get(selected_idx)
        
                # Get the task date and update calendar highlight
        try:
            task_date_str = current_task.split(" - ")[0]
            try:
                task_date = datetime.strptime(task_date_str, "%d/%m/%y").date()
            except ValueError:
                task_date = datetime.strptime(task_date_str, "%d/%m/%YY").date()
                
            # Create a completed event with gray color
            self.calendar.calevent_create(task_date, "Completed", "completed")
            self.calendar.tag_config("completed", background="gray", foreground="white")
                    
            #date, rest = current_task.split(" - ", 1)
            #title = rest.split("[")[0].strip()
            #desc = rest.split("]: ")[1].strip()
            
            date, rest = current_task.split(" - ", 1)
            title = rest.split("[")[0].strip()
            priority = rest.split("[")[1].split("]")[0] 
            desc = rest.split("]: ")[1].strip()
            
            # Extract hour and minute if they exist
            hour = "12"  # default values
            minute = "00"
            if "(" in desc:
                time_str = desc[desc.rfind("(")+1:desc.rfind(")")]
                if ":" in time_str:
                    hour, minute = time_str.split(":")
                desc = desc[:desc.rfind("(")].strip()
        
            priority = 'Done'
            
            task_text = f"{date} - {title} [{priority}]: {desc} ({hour}:{minute})"

            self.listbox_tasks.delete(selected_idx)
            print(task_text)
            self.listbox_tasks.insert(selected_idx, task_text)
            self.apply_priority_color(selected_idx, priority)
            
            self.save_tasks()
            self.highlight_tasks()
            
        except Exception as e:
            print(f"Error updating calendar for completed task: {e}")
        
        if not current_task.endswith("✓"):
            self.listbox_tasks.delete(selected_idx)
            completed_task = current_task + " ✓" 
            self.listbox_tasks.insert(selected_idx, completed_task)
            self.listbox_tasks.itemconfig(selected_idx, fg='gray')       
            
            self.save_tasks()

    def filter_tasks(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox_tasks.delete(0, tk.END)
        
        # Load all tasks and filter
        with open('tasks.json', 'r') as f:
            tasks = json.load(f)
            
        for task in tasks:
            if search_term in task.lower():
                index = self.listbox_tasks.size()
                self.listbox_tasks.insert(tk.END, task)
                # Re-apply colors based on priority
                if '[High]' in task:
                    self.apply_priority_color(index, 'High')
                elif '[Medium]' in task:
                    self.apply_priority_color(index, 'Medium')
                elif '[Low]' in task:
                    self.apply_priority_color(index, 'Low')
                elif '[Done]' in task:
                    self.apply_priority_color(index, 'Done')

    def apply_priority_color(self, index, priority):
        colors = {
            'High': '#ffcdd2',
            'Medium': '#FFFFC5',
            'Low': '#c8e6c9',
            'Done': '#D3D3D3'
        }
        self.listbox_tasks.itemconfig(index, bg=colors.get(priority, '#ffffff'))

    # Override the original save_tasks method to update tray after saving
    def save_tasks(self):
        tasks = list(self.listbox_tasks.get(0, tk.END))
        with open('tasks.json', 'w') as f:
            json.dump(tasks, f)
        
        # Update tray menu after saving
        if self.icon:
            self.icon.menu = pystray.Menu(*self.create_tray_menu())

    def load_tasks(self):
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r') as f:
                tasks = json.load(f)
                for task in tasks:
                    index = self.listbox_tasks.size()
                    self.listbox_tasks.insert(tk.END, task)
                    # Apply colors based on priority
                    if '[High]' in task:
                        self.apply_priority_color(index, 'High')
                    elif '[Medium]' in task:
                        self.apply_priority_color(index, 'Medium')
                    elif '[Low]' in task:
                        self.apply_priority_color(index, 'Low')
                    elif '[Done]' in task:
                        self.apply_priority_color(index, 'Done')
        self.highlight_tasks()

    def highlight_tasks(self):
        tasks = self.listbox_tasks.get(0, "end")
        self.calendar.calevent_remove("all")
        
        today = datetime.now().date()
        self.calendar.calevent_create(today, "Today", "highlight")  
        self.calendar.tag_config("highlight", background='lightgreen', foreground='darkgreen')
        
        for task in tasks:
            try:
                task_date_str = task.split(" - ")[0]  # Get the date part
                parts = task.split("[")
                status = parts[1].split("]")[0]
                #print(status)
                # First try to parse the shorter format (MM/DD/YY)
                try:
                    task_date = datetime.strptime(task_date_str, "%d/%m/%y").date()
                except ValueError:
                    # If that fails, try the full format (DD/MM/YYYY)
                    task_date = datetime.strptime(task_date_str, "%d/%m/%YY").date()
                
                if status == 'Done':
                    #print(task)
                    self.calendar.calevent_create(task_date, "Completed task", "completed")
                    self.calendar.tag_config("completed", background="gray", foreground="white")
                elif status == 'High':
                    self.calendar.calevent_create(task_date, "Task High", "task_high")
                    self.calendar.tag_config("task_high", background="#ffcdd2", foreground="black")
                elif status == 'Low':
                    self.calendar.calevent_create(task_date, "Task Low", "task_low")
                    self.calendar.tag_config("task_low", background="#c8e6c9", foreground="black")
                else:
                    self.calendar.calevent_create(task_date, "Task Medium", "task_medium")
                    self.calendar.tag_config("task_medium", background="#FFFFC5", foreground="black")
                       
            except Exception as e:
                print(f"Error highlighting date for task '{task}': {e}")

    def on_date_selected(self, event):
        selected_date = self.calendar.get_date()
        # Highlight tasks for selected date
        for i in range(self.listbox_tasks.size()):
            task = self.listbox_tasks.get(i)
            if task.startswith(selected_date):
                self.listbox_tasks.selection_clear(0, tk.END)
                self.listbox_tasks.selection_set(i)
                self.listbox_tasks.see(i)
                break

    def sort_tasks(self):
        # Get all tasks
        tasks = list(self.listbox_tasks.get(0, tk.END))
        
        # Sort tasks based on date
        def get_task_date(task):
            date_str = task.split(" - ")[0]
            try:
                # Try both date formats
                try:
                    return datetime.strptime(date_str, "%d/%m/%y").date()
                except ValueError:
                    return datetime.strptime(date_str, "%d/%m/%YY").date()
            except Exception:
                # Return a far future date for invalid dates
                return datetime.max.date()

        # Sort the tasks
        sorted_tasks = sorted(tasks, key=get_task_date)
        
        # Clear and reinsert tasks
        self.listbox_tasks.delete(0, tk.END)
        for task in sorted_tasks:
            index = self.listbox_tasks.size()
            self.listbox_tasks.insert(tk.END, task)
            # Reapply colors based on priority
            if '[High]' in task:
                self.apply_priority_color(index, 'High')
            elif '[Medium]' in task:
                self.apply_priority_color(index, 'Medium')
            elif '[Low]' in task:
                self.apply_priority_color(index, 'Low')
            elif '[Done]' in task:
                self.apply_priority_color(index, 'Done')
        
        # Update calendar highlights
        self.highlight_tasks()

class TaskDialog:
    def __init__(self, parent, title, default_title="", desc="", prio="Medium", h="12", m="00"):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('400x400')
        
        # Title entry
        ttk.Label(self.dialog, text="Title:").pack(pady=5)
        self.title_entry = ttk.Entry(self.dialog, width=40)
        self.title_entry.insert(0, default_title)
        self.title_entry.pack(side=tk.TOP,pady=5)
        
        # Description entry
        ttk.Label(self.dialog, text="Description:").pack(pady=5)
        self.desc_entry = tk.Text(self.dialog, width=40, height=5)
        self.desc_entry.insert("1.0", desc)  # Wypełnienie pola opisem
        self.desc_entry.pack(side=tk.TOP, pady=5)
        
        # Checklist entry
        checklist_frame = ttk.Frame(self.dialog)
        checklist_frame.pack(pady=5)
        ttk.Label(checklist_frame, text="Deadline time:").pack(side=tk.TOP, pady=5)
        
        # Hour Spinbox
        self.hour_var = tk.StringVar(value="12")
        self.hour_spinbox = ttk.Spinbox(checklist_frame, from_=0, to=23, wrap=True, textvariable=self.hour_var, width=5, format='%02.0f')
        
        self.hour_spinbox.pack(side="left", padx=5)
        
        # Minute Spinbox
        self.minute_var = tk.StringVar(value="00")
        self.minute_spinbox = ttk.Spinbox(checklist_frame, from_=0, to=59, wrap=True, textvariable=self.minute_var, width=5, format='%02.0f')
        self.minute_spinbox.pack(side="left", padx=5)
        
        self.hour_var.set(h)
        self.minute_var.set(m)
        
        # Priority selection
        ttk.Label(self.dialog, text="Priority:").pack(pady=5)
        self.priority_var = tk.StringVar(value=prio)
        for priority in ["High", "Medium", "Low"]:
            ttk.Radiobutton(self.dialog, text=priority, value=priority, 
                          variable=self.priority_var).pack()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)

    def submit_time(self):
        selected_time = f"{self.hour_var.get()}:{self.minute_var.get()}"
        print(f"Selected time: {selected_time}")

    def ok(self):
        self.result = (
            self.title_entry.get(),
            self.desc_entry.get("1.0", tk.END).strip(),
            self.priority_var.get(),
            self.hour_var.get(),
            self.minute_var.get()
        )
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

        
if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()
