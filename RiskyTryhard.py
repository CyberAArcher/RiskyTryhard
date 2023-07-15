# Import the necessary modules
import time
import pickle
import win32gui
import win32api
from tkinter import Tk, Label, Button, Toplevel

# Define the applications to track
productive_apps = ['youtube', 'usmle step 1']
non_productive_apps = ['nothing', 'telegram', 'discord', 'minecraft', 'sublime text', 'other']
sub_categories = ['premiere pro', 'photoshop', 'scripting', 'gpt']
all_apps = productive_apps + non_productive_apps + sub_categories

# Define the weekly goals (in seconds)
weekly_goals = {
    'youtube': 6 * 60 * 60 * 7,  # 6 hours a day, 7 days a week
    'usmle step 1': 2 * 60 * 60 * 7,  # 2 hours a day, 7 days a week
    'premiere pro': 3 * 60 * 60 * 7,  # 3 hours a day, 7 days a week
    'photoshop': 3 * 60 * 60 * 7,  # 3 hours a day, 7 days a week
    'scripting': 2 * 60 * 60 * 7,  # 2 hours a day, 7 days a week
    'nothing': 1 * 60 * 60 * 7  # 1 hour a day, 7 days a week
}

# Define the importance for each category
importance = {
    'youtube': 1,
    'usmle step 1': 2,
    'premiere pro': 3,
    'photoshop': 3,
    'scripting': 2,
    'nothing': 0,
    'telegram': 0,
    'discord': 0,
    'minecraft': 0,
    'sublime text': 1,
    'gpt': 1,
    'other': 0
}

# Initialize a dictionary to store the usage times and the last time the application was running
try:
    with open('usage_times.pkl', 'rb') as f:
        data = pickle.load(f)
    if isinstance(data, tuple) and len(data) == 2:
        usage_times, last_time = data
        # Calculate the difference between the current time and the last time, and add it to the 'nothing' time
        difference = int(time.time() - last_time)
        usage_times['nothing'] += difference
    else:
        raise ValueError("Invalid data in pickle file.")
except (FileNotFoundError, ValueError):
    usage_times = {app: 0 for app in all_apps}
    usage_times['nothing'] = 0

# Initialize the last mouse position and idle time
last_mouse_pos = win32api.GetCursorPos()
idle_time = 0

# Initialize the time unit
time_unit = 'seconds'

def get_active_window_title():
    window_handle = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(window_handle)
    return window_title.lower()

def update_usage_times():
    global last_mouse_pos, idle_time

    # Get the current mouse position
    current_mouse_pos = win32api.GetCursorPos()

    # Check if the mouse has moved
    if current_mouse_pos != last_mouse_pos:
        # Update the last mouse position and reset the idle time
        last_mouse_pos = current_mouse_pos
        idle_time = 0
    else:
        # Increment the idle time
        idle_time += 1

    # If the idle time is less than 10 minutes, update the usage times
    if idle_time < 600:
        active_window_title = get_active_window_title()

        found = False
        for app in all_apps:
            if app == 'usmle step 1' and 'lecturio' in active_window_title:
                usage_times[app] = usage_times.get(app, 0) + 1
                found = True
                break
            elif app == 'scripting' and 'chat.openai.com/c' in active_window_title:
                usage_times[app] = usage_times.get(app, 0) + 1
                usage_times['youtube'] = usage_times.get('youtube', 0) + 1
                found = True
                break
            elif app in active_window_title:
                usage_times[app] = usage_times.get(app, 0) + 1
                found = True
                break

        if not found:
            usage_times['nothing'] += 1

        # Update the labels
        for app, label in labels.items():
            time_value = usage_times.get(app, 0)
            if time_unit == 'minutes':
                time_value /= 60
            elif time_unit == 'hours':
                time_value /= 3600
            label.config(text=f'{app}: {round(time_value, 2)} {time_unit}')

    # Save the usage times and the current time to a file
    with open('usage_times.pkl', 'wb') as f:
        pickle.dump((usage_times, time.time()), f)

    # Schedule the next update
    root.after_id = root.after(1000, update_usage_times)

def calculate_score():
    # Calculate the total goal and actual time for the productive tasks
    total_goal = sum(weekly_goals[app] * importance[app] for app in all_apps)
    total_actual = sum(usage_times.get(app, 0) * importance[app] for app in all_apps)

    # Calculate and return the score
    return (total_actual / total_goal) * 100

def show_schedule():
    # Create a new window
    schedule_window = Toplevel(root)

    # Display the schedule and the current score
    for i, app in enumerate(all_apps):
        goal = weekly_goals[app] / (60 * 60)
        actual = usage_times.get(app, 0) / (60 * 60)
        Label(schedule_window, text=f'{app}: {goal} hours goal, {actual} hours actual').pack()
    Label(schedule_window, text=f'Score: {calculate_score()}').pack()

def change_time_unit():
    global time_unit
    if time_unit == 'seconds':
        time_unit = 'minutes'
    elif time_unit == 'minutes':
        time_unit = 'hours'
    else:
        time_unit = 'seconds'

def show_more():
    # Toggle the visibility of the sub categories
    for app in sub_categories:
        if labels[app].winfo_ismapped():
            labels[app].grid_remove()
        else:
            labels[app].grid(row=labels[app].row, column=1, padx=20)

def on_exit():
    # Cancel the next update
    root.after_cancel(root.after_id)
    # Destroy the window
    root.destroy()

# Create the main window
root = Tk()
root.geometry('450x600')  # Increase the height of the window
root.configure(bg='#263D42')  # Dark blue background

# Set the function to call when the window is closed
root.protocol('WM_DELETE_WINDOW', on_exit)

# Create labels to display the usage times
labels = {}
for i, app in enumerate(all_apps):
    if app in productive_apps:
        labels[app] = Label(root, font=('Minecraft', 16), bg='#263D42', fg='white')
    elif app in non_productive_apps:
        labels[app] = Label(root, font=('Minecraft', 10), fg='red', bg='#263D42')
    else:
        labels[app] = Label(root, font=('Minecraft', 24), bg='#263D42', fg='white')

    if app not in sub_categories:
        labels[app].grid(row=i+3, column=1, padx=20)  # Offset the row numbers by 3 to leave space for the buttons
    labels[app].config(text=f'{app}: {usage_times.get(app, 0)} {time_unit}')
    labels[app].row = i+3  # Store the row number in the label object

# Create a button to display the schedule
Button(root, text='Show Schedule', command=show_schedule, bg='#114E60', fg='white').grid(row=0, column=1, padx=20, pady=10)

# Create a button to change the time unit
Button(root, text='Change Time Unit', command=change_time_unit, bg='#457B9D', fg='white').grid(row=1, column=1, padx=20, pady=10)

# Create a button to display more apps
Button(root, text='MORE', command=show_more, bg='#1D3557', fg='white').grid(row=2, column=1, padx=20, pady=10)

# Start the usage time update loop
root.after_id = root.after(1000, update_usage_times)

# Start the main event loop
root.mainloop()
