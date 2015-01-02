#!/usr/bin/env python

import os
import errno
import sqlite3
from settings import GKT_PATH, VERSION, DB_NAME


def install(GKT_PATH):
    print("Installing GKeepTrack " + VERSION + "...")
    # Create gkeeptrack configuration directory
    try:
        os.makedirs(GKT_PATH)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gkeeptrack/
    try:
        os.chdir(GKT_PATH)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Creating projects directory
    try:
        os.makedirs("projects")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Creating data directory
    try:
        os.makedirs("data")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gkeeptrack/data/
    try:
        os.chdir("data")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    if os.path.exists(DB_NAME):
        print("There is already a database configured. Override?[y/n]")
        choice = raw_input().lower()
        if choice == "y":
            os.remove(DB_NAME)
    if not os.path.exists(DB_NAME):
        print("Creating database...")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Create tables
        print("Creating tables...")
        # Projects
        c.execute("""
            CREATE TABLE projects(
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name NOT NULL
            )""")
        # Inserting project 'default' for when there is no project specified
        c.execute("INSERT INTO projects(project_name) VALUES ('default')")
        # Applications
        c.execute("""
            CREATE TABLE applications(
                app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id_fk INTEGER NOT NULL,
                app_name TEXT NOT NULL,
                FOREIGN KEY(project_id_fk) REFERENCES projects(project_id)
            )""")
        # Actions
        c.execute("""
            CREATE TABLE actions(
                app_id_fk INTEGER NOT NULL,
                project_id_fk INTEGER NOT NULL,
                action NOT NULL,
                timestamp integer(4) NOT NULL default (strftime('%s','now')),
                FOREIGN KEY(app_id_fk) REFERENCES applications(app_id),
                FOREIGN KEY(project_id_fk) REFERENCES projects(project_id)
            )""")
        # Saving (committing) the changes
        print("Saving changes...")
        conn.commit()
        # Closing connection
        conn.close()
    print("Finished database configuration.")
    print("Do you want to create a project now?")
    print("You can still do it later. [y/n]")
    choice = raw_input().lower()
    if choice == "y":
        print("What is the name of your project?")
        project_name = raw_input().lower()
        add_new_project(project_name)
    print("Installation is done.")


def add_new_project(project_name):
    print("Creating %s...") % project_name
    # Change to $HOME/.gkeeptrack/
    try:
        os.chdir(GKT_PATH)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Isn't the project already created?
    if os.path.exists("projects/" + project_name):
        print("Project " + project_name + " already exists. Skipping...")
    else:
        # Create the project file configuration
        try:
            expression = "touch " + "projects/" + project_name
            os.system(expression)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        conn = sqlite3.connect(GKT_PATH + 'data/' + DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO projects(project_name) VALUES (?)", [project_name])
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Is GKeepTrack already installed?
    if os.path.isdir(GKT_PATH):
        print("It seems you already have a GKeepTrack installation in")
        print("in your system. Do you still want to proceed? (y/n)")
        choice = raw_input().lower()
        if choice == "y":
            install(GKT_PATH)
        else:
            print("Leaving setup...")
            exit()
    else:
        install(GKT_PATH)
