#!/usr/bin/env python

import wnck
import gtk
import time
from time import sleep
import datetime
import sqlite3

# Preparing database connection

conn = sqlite3.connect('by.db')
conn.text_factory = str
c = conn.cursor()

previous_active_window = None
app_names = []
app_pids = []

while True:
    default_screen = wnck.screen_get_default()
    current_active_window = default_screen.get_active_window()
    # If you changed window focus
    if current_active_window != previous_active_window:
        # Update list of windows
        window_list = default_screen.get_windows()
        if len(window_list) == 0:
            print("No Windows Found")
        # If there are windows opened
        else:
            for window in window_list:
                # Check if it is registered in applications table
                window_app_name = (window.get_application().get_name(),)
                sql_statement = c.execute("SELECT app_name FROM applications\
                                           WHERE app_name=?", window_app_name)
                # If is already registered
                if sql_statement.fetchone() is not None:
                    # Do nothing
                    pass
                # It is not yet registered
                else:
                    c.execute("INSERT INTO applications(app_name)\
                               VALUES (?)", window_app_name)
                    # Committing changes
                    conn.commit()
            active_window = new_active_window
    gtk.events_pending()
    gtk.main_iteration()
