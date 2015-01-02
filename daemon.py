#!/usr/bin/env python

from settings import GKT_PATH, DB_NAME
import datetime
import sqlite3
import wnck
import time
import gtk
import sys
import os

# Preparing database connection
conn = sqlite3.connect(GKT_PATH+'data/'+DB_NAME)
conn.text_factory = str
c = conn.cursor()

previous_active_window = None

if len(sys.argv) > 1:
    project_name = sys.argv[1]
    sql_statement = c.execute("SELECT project_id FROM projects\
                              WHERE project_name=?", [project_name])
    project_id = sql_statement.fetchone()[0]
    # If it exists
    if project_id is None:
        print("There is no project named %s") % project_name
        exit()
else:
    project_id = 1
    project_name = "default"

while True:
    default_screen = wnck.screen_get_default()
    current_active_window = default_screen.get_active_window()
    # If you changed window focus
    if current_active_window != previous_active_window:
        # Update list of windows
        window_list = default_screen.get_windows()
        # If no windows are opened
        if len(window_list) == 0:
            print("No Windows Found")
        # If there are windows opened
        else:
            for window in window_list:
                # Check if it is registered in applications table
                window_app_name = window.get_application().get_name()
                sql_statement = c.execute("SELECT app_name FROM applications\
                                          WHERE app_name=? AND project_id_fk=?",
                                          (window_app_name, str(project_id)))
                returned_app_name = sql_statement.fetchone()
                # If is already registered
                if returned_app_name is not None:
                    # Is this window the previous one?
                    if window == previous_active_window:
                        # Get previous window name
                        previous_window_app_name = window.get_application().get_name()
                        # Get app id
                        sql_statement = c.execute("SELECT app_id FROM\
                                                  applications\
                                                  WHERE app_name=?",
                                                  [previous_window_app_name])
                        app_id = sql_statement.fetchone()
                        # Register unfocus action
                        action = "Unfocus"
                        c.execute("INSERT INTO actions(app_id_fk, project_id_fk,\
                                  action) VALUES (?, ?, ?)", (app_id[0],
                                                              str(project_id),
                                                              action))
                    # Or is this the current one?
                    elif window == current_active_window:
                        # Get app id
                        sql_statement = c.execute("SELECT app_id FROM\
                                                  applications\
                                                  WHERE app_name=?",
                                                  [window_app_name])
                        app_id = sql_statement.fetchone()
                        # Register focus action
                        action = "Focus"
                        c.execute("INSERT INTO actions(app_id_fk, project_id_fk,\
                                  action) VALUES (?, ?, ?)", (app_id[0],
                                                              str(project_id),
                                                              action))
                    else:
                        pass  # Do nothing
                # It is not yet registered
                else:
                    c.execute("INSERT INTO applications(app_name,\
                              project_id_fk) VALUES (?, ?)", [window_app_name,
                                                              str(project_id)])
                    # Committing changes
            conn.commit()
            previous_active_window = current_active_window
    gtk.events_pending()
    gtk.main_iteration()
