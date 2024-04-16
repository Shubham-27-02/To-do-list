import tkinter as tk
import pickle
from datetime import datetime
import requests
import json

# Initialize the main window
root = tk.Tk()
root.title("To-Do List App")
root.configure(bg='SkyBlue1')

# Load tasks from a file (if available)
try:
    with open("tasks.pkl", "rb") as file:
        tasks = pickle.load(file)
except FileNotFoundError:
    tasks = []

def get_weather(location):
    # Make a get request to get the latest weather data
    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid=480fdb78724487835d2acd4095ef1c00")

    # Load JSON data from the response
    weather_data = json.loads(response.text)

    # Get temperature in Kelvin and convert it to Celsius
    temperature_k = weather_data['main']['temp']
    temperature_c = temperature_k - 273

    temperature_c = int(temperature_c)

    # Get weather description
    weather = weather_data['weather'][0]['description']

    return temperature_c, weather

def get_weekday():
    # Get the current date
    now = datetime.now()

    # Return the weekday
    return now.strftime("%A")

# Function to add a task
def addTask():
    task = input_task.get()
    if task.strip():  # Only add the task if it's not empty
        tasks.append(task)
        task_list.insert(tk.END, task)
        saveTasks()
        update_tasks()

# Function to delete a task
def deleteTask():
    selected_task = task_list.curselection()
    if selected_task:
        task_index = selected_task[0]
        tasks.pop(task_index)
        task_list.delete(task_index)
        saveTasks()
        update_tasks()
    popup.destroy()

# Function to mark a task as completed
def markAsCompleted():
    selected_task = task_list.curselection()
    if selected_task:
        task_index = selected_task[0]
        task = tasks[task_index]
        # Check if the task is already marked as completed
        if not task.endswith("(completed)"):
            tasks[task_index] = f"{task} (completed)"
            task_list.delete(task_index)
            task_list.insert(task_index, f"{task} (completed)")
            task_list.itemconfig(task_index, {'bg':'light grey'})
            saveTasks()
            update_tasks()
    popup.destroy()

# Save tasks to a file
def saveTasks():
    with open("tasks.pkl", "wb") as file:
        pickle.dump(tasks, file)

# Function to update the sidebar
def update_time():
    # Get the current time
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M")

    # Get the weather and weekday
    temperature, weather = get_weather("Wagholi")
    weekday = get_weekday()

    # Update the time and number of pending tasks in the upper part of the sidebar
    upper_sidebar.config(state=tk.NORMAL)
    upper_sidebar.delete("1.0", tk.END)
    upper_sidebar.insert("1.0", f" Date and Time: {date_time}\n\n")
    pending_tasks = len([task for task in tasks if not task.endswith("(completed)")])
    upper_sidebar.insert(tk.END, f" Number of Pending Tasks: {pending_tasks}\n")
    upper_sidebar.tag_config("highlight", background="Turquoise", foreground="black")
    upper_sidebar.tag_add("highlight", "1.0", "1.14")
    upper_sidebar.config(state=tk.DISABLED)

    # Update the weekday and weather information in the lower part of the sidebar
    lower_sidebar.config(state=tk.NORMAL)
    lower_sidebar.delete("1.0", tk.END)
    lower_sidebar.insert("1.0", f" Weekday: {weekday}\n\n")
    lower_sidebar.insert(tk.END, f" Weather: {temperature}°C, {weather}\n")
    lower_sidebar.config(state=tk.DISABLED)

    # Schedule the function to be called again after 1 second
    root.after(1000, update_time)

# Function to update the number of pending tasks
def update_tasks():
    # Display the number of pending tasks
    pending_tasks = len([task for task in tasks if not task.endswith("(completed)")])
    upper_sidebar.config(state=tk.NORMAL)
    upper_sidebar.delete("2.0", "3.0")
    upper_sidebar.insert("2.0", f" Number of Pending Tasks: {pending_tasks}\n\n")
    upper_sidebar.tag_config("highlight", background="Turquoise", foreground="black")
    upper_sidebar.tag_add("highlight", "2.0", "2.24")
    upper_sidebar.config(state=tk.DISABLED)

# Function to select a task on hover
def selectTask(event):
    task_list.selection_clear(0, tk.END)
    task_list.selection_set(task_list.nearest(event.y))

# Function to create a popup window
def createPopup(event):
    global popup
    # Check if popup already exists
    if popup is not None:
        # If it does, destroy it
        popup.destroy()
    popup = tk.Toplevel(root)
    popup.title("Options")
    complete_button = tk.Button(popup, text="Mark as completed", command=markAsCompleted, font=("Helvetica", 10), bg='darkgray')
    complete_button.pack(fill=tk.X)
    delete_button = tk.Button(popup, text="Delete Task", command=deleteTask, font=("Helvetica", 10), bg='darkgray')
    delete_button.pack(fill=tk.X)
    # Position the popup window near the cursor
    popup.geometry(f"+{popup.winfo_pointerx()}+{popup.winfo_pointery()}")

# Create widgets
input_task = tk.Entry(root, font=("Helvetica", 20))
add_button = tk.Button(root, text="Add Task", command=addTask, font=("Helvetica", 20), bg='darkgray')
task_list = tk.Listbox(root, font=("Helvetica", 20), bg='SkyBlue1')
upper_sidebar = tk.Text(root, width=30, height=5, font=("Helvetica", 15), bg='MediumPurple1')
lower_sidebar = tk.Text(root, width=30, height=5, font=("Helvetica", 15), bg='MediumPurple1')
input_task.bind('<Return>', lambda event: addTask())
update_tasks()

# Use grid to place widgets
input_task.grid(row=0, column=0, columnspan=2, sticky='ew')
add_button.grid(row=1, column=0, columnspan=2, sticky='ew')
task_list.grid(row=2, column=0, rowspan=2, sticky='nsew')
upper_sidebar.grid(row=2, column=1, sticky='nsew')
lower_sidebar.grid(row=3, column=1, sticky='nsew')

# Configure weight to allow resizing
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Load existing tasks into the listbox
for task in tasks:
    task_list.insert(tk.END, task)

# Initialize popup as None
popup = None

# Bind right click event to the listbox
task_list.bind("<Button-3>", createPopup)

# Bind motion event to the listbox
task_list.bind("<Motion>", selectTask)

# Update the sidebar
update_time()

# Run the main loop
root.mainloop()
