#!/usr/bin/env python

import os
import sys
import gtk
import time
import dbus
import wnck
import sqlite3
import datetime
import platform
import dbus.service
from daemon import DaemonClass
from settings import GKT_PATH, DB_NAME
from dbus.mainloop.glib import DBusGMainLoop


SETTINGS_LINUX = {
    'APP':      'gkeeptrack',
    'PIDFILE':  '/tmp/gkeeptrack.pid',
    'LOG':  '/tmp/gkeeptrack.log'
}
FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
__version__ = '1.0'


class MyDBUSService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.gkeeptrack.daemon',
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/gkeeptrack/daemon')

    @dbus.service.method('org.gkeeptrack.daemon')
    def is_running(self):
        if os.path.exists(SETTINGS_LINUX['PIDFILE']):
            try:
                pf = file(SETTINGS_LINUX['PIDFILE'],'r')
                pid = int(pf.read().strip())
                pf.close()
                return True
            except IOError:
                sys.stdout.write('It is running but couldn\'t read pidfile')
                return True
        else:
            return False

    @dbus.service.method('org.gkeeptrack.daemon')
    def stop_daemon(self):
        global app
        try:
            app = GKeepTrackDaemon(SETTINGS_LINUX)
            sys.stdout.write("Stopping the daemon...\n")
            app.stop()
            return True
        except Exception:
            return False


class GKeepTrackDaemon(DaemonClass):
    def __init__(self, settings):
        # Initialise the parent class
        DaemonClass.__init__(self, settings)

    def run(self):
        """
            Runs after the process has been demonised.
            Overrides the run method provided by the class.
            When this method exits, the application exits.
        """

        # Preparing database connection
        conn = sqlite3.connect(GKT_PATH+'data/'+DB_NAME)
        conn.text_factory = str
        c = conn.cursor()

        previous_active_window = 'None'  # Window that has just lost focus
        # daemon.py [project-name]
        if len(sys.argv) > 2:
            project_name = sys.argv[2]
            # Is there a project named project-name?
            sql_expr = c.execute("SELECT project_id FROM projects\
                                      WHERE project_name=?", [project_name])
            project_id = sql_expr.fetchone()
            # If there is no project named project-name
            if project_id is None:
                print("There is no project named %s") % project_name
                exit()
        # No project name was informed
        else:
            project_id = 1
            project_name = "default"

        while app.alive:
            default_screen = wnck.screen_get_default()
            current_active_window = default_screen.get_active_window()
            # Changed window focus
            if current_active_window != previous_active_window:
                # Update list of windows (maybe a new window?)
                window_list = default_screen.get_windows()
                # If no windows are opened
                # if len(window_list) == 0:
                #     pass
                # # If there are windows opened
                # else:
                if True:
                    for window in window_list:
                        # Check if it is registered in applications table
                        window_app_name = window.get_application().get_name()
                        sql_expr = c.execute("SELECT app_name FROM\
                                             applications WHERE app_name=?\
                                             AND project_id_fk=?",
                                             (window_app_name,
                                              str(project_id)))
                        returned_app_name = sql_expr.fetchone()
                        # If is already registered
                        if returned_app_name is not None:
                            # Insert "unfocus" action for the previous window
                            if window == previous_active_window:
                                # Get previous window name
                                previous_win_app = window.get_application()
                                previous_window_app_name = previous_win_app.get_name()
                                # Get app id
                                sql_expr = c.execute("SELECT app_id FROM\
                                                     applications\
                                                     WHERE app_name=?",
                                                     [previous_window_app_name])
                                app_id = sql_expr.fetchone()
                                # Register unfocus action
                                action = "Unfocus"
                                c.execute("INSERT INTO actions(app_id_fk, project_id_fk,\
                                          action) VALUES (?, ?, ?)", (app_id[0],
                                                                      str(project_id),
                                                                      action))
                            # Insert "focus" action for the current window
                            elif window == current_active_window:
                                # Get app id
                                sql_expr = c.execute("SELECT app_id FROM\
                                                     applications\
                                                     WHERE app_name=?",
                                                     [window_app_name])
                                app_id = sql_expr.fetchone()
                                # Register focus action
                                action = "Focus"
                                c.execute("INSERT INTO actions(app_id_fk,\
                                          project_id_fk, action) VALUES\
                                          (?, ?, ?)", (app_id[0],
                                                       str(project_id),
                                                       action))
                            else:
                                # Do nothing for non-previous/current windows
                                pass
                        # It is not yet registered
                        else:
                            c.execute("INSERT INTO applications(app_name,\
                                      project_id_fk) VALUES (?, ?)",
                                      [window_app_name, str(project_id)])
                    # Committing changes
                    conn.commit()
                    # For the next focus change, the previous will
                    # be the current one
                    previous_active_window = current_active_window
            gtk.events_pending()
            gtk.main_iteration()

        # Interrupt received so quit gracefully
        sys.stdout.write('...Shutting down the daemon.\n')

        # Final tidy up - delete PID file etc
        self.on_exit()
        self.cleanup()
        sys.stdout.write("All Done.")
        # The daemon will close down now

if __name__ == "__main__":
    global app

    if platform.system() == 'Linux':
        SETTINGS = SETTINGS_LINUX
    else:
        SETTINGS = SETTINGS_OTHER

    print "----- %s (Release: %s) -----" % (SETTINGS['APP'], __version__)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            sys.stdout.write("Starting the DBus...\n")
            DBusGMainLoop(set_as_default=True)
            dbus_service = MyDBUSService()
            sys.stdout.write("Starting the app...\n")
            app = GKeepTrackDaemon(SETTINGS)
            sys.stdout.write("Starting daemon mode...")
            app.start()
        elif 'stop' == sys.argv[1]:
            app = GKeepTrackDaemon(SETTINGS)
            sys.stdout.write("Stopping the daemon...\n")
            app.stop()
        elif 'restart' == sys.argv[1]:
            app = GKeepTrackDaemon(SETTINGS)
            sys.stdout.write("Restarting the daemon...")
            app.restart()
        elif 'status' == sys.argv[1]:
            app = GKeepTrackDaemon(SETTINGS)
            app.status()
        else:
            print("usage: %s start|stop|restart|status", sys.argv[0])
            sys.exit(2)
    else:
            print("Invalid command: %r", ' '.join(sys.argv))
            print("usage: %s start|stop|restart|status", sys.argv[0])
            sys.exit(2)

    print("...Done")

# end of module
