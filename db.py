#!/usr/bin/env python

import sqlite3

conn = sqlite3.connect('by.db')
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
conn.commit()

# Closing connection
conn.close()
