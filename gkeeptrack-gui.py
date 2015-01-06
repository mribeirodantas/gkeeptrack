#!/usr/bin/env python

import dbus
import errno
from os import listdir
from os.path import isfile, join
from gi.repository import Gtk, Gio, Gdk

VERSION = '0.1'
path = '/home/mribeirodantas/.gkeeptrack/projects/'


class ListBoxWindow(Gtk.Window):

    track_titles = False
    track_time_per_app = False
    project_name = None

    def __init__(self):

        Gtk.Window.__init__(self, title="GKeepTrack")
        self.set_default_size(400, 200)
        self.set_border_width(10)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "GKeepTrack"
        self.set_titlebar(hb)

        button = Gtk.Button()
        button.connect("clicked", self.add_project)
        icon = Gio.ThemedIcon(name="list-add")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        hb.pack_end(button)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.override_background_color(Gtk.StateType.NORMAL,
                                          Gdk.RGBA(.0, .0, .0, .0))
        hbox.pack_start(listbox, True, True, 0)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        label = Gtk.Label("Track Window Titles", xalign=0)
        check = Gtk.CheckButton()
        check.connect("toggled", self.track_window_titles)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(check, False, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        label = Gtk.Label("Track Time per Application", xalign=0)
        check = Gtk.CheckButton()
        check.connect("toggled", self.track_time_per_application)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(check, False, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        label = Gtk.Label("Choose a Project", xalign=0)
        combo = Gtk.ComboBoxText()
        try:
            files = [f for f in listdir(path) if isfile(join(path, f))]
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                print("You have a problematic installation.")
                print("The projects directory was not found, try reinstalling")
                exit()
        if files == []:
            # combo.insert(0, "0", "None")
            # Disable it, instead of showing None
            combo.set_sensitive(False)
        else:
            for index, file in enumerate(files):
                combo.insert(int(index), str(index), str(file))
        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(combo, False, True, 0)
        combo.connect("changed", self.combo_changed)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)

        label1 = Gtk.Label("Tracking", xalign=0)
        vbox.pack_start(label1, True, True, 0)

        switch = Gtk.Switch()
        switch.connect("notify::active", self.start_tracking)
        switch.props.valign = Gtk.Align.CENTER
        hbox.pack_start(switch, False, True, 0)
        if running:
            switch.set_state(True)
        else:
            switch.set_state(False)
        listbox.add(row)

    def add_project(self, widget):
        pass

    def track_window_titles(self, widget):
        if self.track_titles is True:
            self.track_titles = False
            print("Untracking window titles")
        else:
            self.track_titles = True
            print("Tracking Window Titles")

    def track_time_per_application(self, widget):
        if self.track_time_per_app is True:
            self.track_time_per_app = False
            print("Untracking time per app")
        else:
            self.track_time_per_app = True
            print("Tracking time per app")

    def combo_changed(self, combo):
        self.project_name = combo.get_active_text()

    def start_tracking(self, widget, is_active):
        if widget.get_active():
            print("Starting tracking")
            # ./daemon.py "name of the project"
            # Creates .tracking (lock_file) in GKT_PATH
            if self.project_name is None:
                message = "Tracking started."
            else:
                message = "Tracking of project " + self.project_name\
                          + " just started."
            print(message)

        else:
            print("Stopping tracking")
            # Removes .tracking (lock_file) in GKTPATH
            # Sends a signal to daemon.py to stop
            if self.project_name is None:
                message = "Tracking stopped."
            else:
                message = "Tracking of project " + self.project_name\
                          + " just started."
            print(message)

if __name__ == "__main__":
    try:
        bus = dbus.SessionBus()
        daemon_bus = bus.get_object('org.gkeeptrack.daemon',
                                    '/org/gkeeptrack/daemon')
        is_running = daemon_bus.get_dbus_method('is_running',
                                                'org.gkeeptrack.daemon')
        running = is_running()
    except dbus.exceptions.DBusException:  # No daemon bus
        running = False

    win = ListBoxWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
