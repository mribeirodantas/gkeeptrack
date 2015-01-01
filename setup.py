#!/usr/bin/env python

import sqlite3
import os
import errno


def install(gkt_path):
    # Create gkeeptrack configuration directory
    try:
        os.makedirs(gkt_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gkeeptrack/
    try:
        os.chdir(gkt_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Creating data directory
    try:
        os.makedirs('data')
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    # Change to $HOME/.gkeeptrack/data/
    try:
        os.chdir('data')
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    if os.path.exists('gkt.db'):
        print("There is already a database configured. Override?[y/n]")
        choice = raw_input().lower()
        if choice == 'n':
            print("Leaving setup...")
            exit()

    if os.path.exists('gkt.db'):
        os.remove('gkt.db')
    print("Creating database...")
    conn = sqlite3.connect('gkt.db')
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
    gkt_path = os.getenv("HOME") + "/.gkeeptrack/"
    # Is GKeepTrack already installed?
    if os.path.isdir(gkt_path):
        print("It seems you already have a GKeepTrack installation in")
        print("in your system. Do you still want to proceed? (y/n)")
        choice = raw_input().lower()
        if choice == 'y':
            install(gkt_path)
        else:
            print("Leaving setup...")
            exit()
    else:
        install(gkt_path)
