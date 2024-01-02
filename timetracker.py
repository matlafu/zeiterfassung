import time
import datetime
import psutil
import win32gui
import win32process
import tkinter as tk
from threading import Thread
import pandas as pd
import os

#TODO: make the GUI better
#TODO: group activities in a better way than just saying "keep everything above 5 minutes"
'''
 Tne problem with this approach is that if you open a lot of shit for a brief amount of time (lets say i work on this file and I open ms teams
for  a quick chat that lasts less than 5 min and then I open my emails and chatgpt before returning to my initial project, the logger should only log the project
and not everything else inbetween unless it´s longer than 5 mins, but then the script should only have one line that encompasses the script im working on and
it should contain the amount of minutes spent in ms teams and chatgpt idk man)'''


# Global flag to control logging
logging_active = False

# Function to get the current active window
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        app_name = psutil.Process(pid).name()
        window_title = win32gui.GetWindowText(hwnd)
        return app_name, window_title
    except Exception as e:
        print(e)
        return None, None

# Data Structure to Store Activity Logs
activity_log = []
current_activity = None
start_time = None

# Function to handle logging
def handle_logging():
    global current_activity, start_time, logging_active
    while logging_active:
        app_name, window_title = get_active_window_title()
        if app_name is not None and (current_activity != app_name):
            end_time = datetime.datetime.now()
            if current_activity is not None:
                activity_log.append({
                    'Start': start_time.strftime("%H:%M"),
                    'End': end_time.strftime("%H:%M"),
                    'Activity': current_activity,
                    'Name': window_title_prev
                })

            current_activity = app_name
            window_title_prev = window_title
            start_time = datetime.datetime.now()

        time.sleep(1)

# Function to start logging
def start_logging():
    global logging_active
    logging_active = True
    logging_thread = Thread(target=handle_logging)
    logging_thread.start()

# Function to stop logging and save file
def stop_logging_and_save():
    global logging_active
    logging_active = False

    # Convert activity log into DataFrame
    df = pd.DataFrame(activity_log)
    if not df.empty:
        # Calculate Duration and convert to minutes
        df['Start'] = pd.to_datetime(df['Start'], format='%H:%M')
        df['End'] = pd.to_datetime(df['End'], format='%H:%M')
        df['Duration'] = (df['End'] - df['Start']).dt.total_seconds() / 60

        # Filter out activities less than 5 minutes and reset index
        df = df[df['Duration'] >= 5].reset_index(drop=True)

        # Adjusting the time slots
        for i in range(len(df) - 1, 0, -1):  # Iterate backwards
            if df.loc[i, 'Start'] < df.loc[i - 1, 'End']:
                df.loc[i - 1, 'End'] = df.loc[i, 'Start']

        # Remove the Duration column and revert datetime format
        df.drop(columns=['Duration'], inplace=True)
        df['Start'] = df['Start'].dt.strftime('%H:%M')
        df['End'] = df['End'].dt.strftime('%H:%M')

    # Save the processed DataFrame
    filename = filename_entry.get()
    filepath = f"C:/Users/{os.getlogin()}/Desktop/{filename}.xlsx"  # Modify path if necessary
    df.to_csv(filepath, index=False)
    print(f"Saved log to {filepath}")


# Setting up the GUI
root = tk.Tk()
root.title("Activity Logger")

# Filename entry
filename_label = tk.Label(root, text="Enter filename:")
filename_label.pack()
filename_entry = tk.Entry(root)
filename_entry.pack()

# Start button
start_button = tk.Button(root, text="Start Logging", command=start_logging)
start_button.pack()

# Stop and Save button
stop_button = tk.Button(root, text="Stop and Save", command=stop_logging_and_save)
stop_button.pack()

root.mainloop()

