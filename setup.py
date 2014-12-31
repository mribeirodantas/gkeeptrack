#!/usr/bin/env python

import sqlite3
import os
import errno


def install(gtt_path):
    # Create gtimetracker configuration directory
    try:
        os.makedirs(gtt_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gtimetracker/
    try:
        os.chdir(gtt_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Creating data directory
    try:
        os.makedirs('data')
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gtimetracker/data/
    try:
        os.chdir('data')
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    if os.path.exists('gtt.db'):
        print("There is already a database configured. Override?[y/n]")
        choice = raw_input().lower()
        if choice == 'n':
            print("Leaving setup...")
            exit()

    if os.path.exists('gtt.db'):
        os.remove('gtt.db')
    print("Creating database...")
    conn = sqlite3.connect('gtt.db')
    c = conn.cursor()

    # Create tables
    print("Creating tables...")
    c.execute("""
        CREATE TABLE applications(
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT
        )""")

    c.execute("""
        CREATE TABLE actions(
            app_id_fk INTEGER,
            action,
            timestamp integer(4) not null default (strftime('%s','now')),
            FOREIGN KEY(app_id_fk) REFERENCES applications(app_id)
        )""")
    # Saving (committing) the changes
    print("Saving changes...")
    conn.commit()

    # Closing connection
    conn.close()
    print("Installation is done.")

if __name__ == "__main__":
    gtt_path = os.getenv("HOME") + "/.gtimetracker/"
    # Is GTimeTracker already installed?
    if os.path.isdir(gtt_path):
        print("It seems you already have a GTimeTracker installation in")
        print("in your system. Do you still want to proceed? (y/n)")
        choice = raw_input().lower()
        if choice == 'y':
            install(gtt_path)
        else:
            print("Leaving setup...")
            exit()
    else:
        install(gtt_path)
