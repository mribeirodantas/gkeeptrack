gtimetracker
============

GTimeTracker is a time-tracking software for GNOME, written in Python. It makes use of a Python wrapper for the libwnck.
In Fedora, the package is gnome-python2-libwnck, and that's the only environment I've been testing it so far. New 
collaborators are very welcome, so if you're interested in collaborating please get in touch!

mribeirodantas@fedoraproject.org

GTimeTracker is still very far from what it may achieve someday. I plan to have a software as a service, written 
in Python with Django that will get the raw data from GTimeTracker's daemon and generate charts and interesting
information.

There should also be a GUI for configuration, mostly to help users on whitelisting or blacklisting specific applications.
