#!/usr/bin/env python3
import os
import sys
import time
import signal
import json
import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'myappindicator'
PIPE_PATH = "/tmp/worktime"
keep_running = True

def get_icon_path(icon):
    return "{}/assets/img/{}.svg".format(sys.path[0], icon)

def open_pipe(handle_message):
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

    # Open the fifo
    pipe_fd = os.open(PIPE_PATH, os.O_RDONLY | os.O_NONBLOCK)

    with os.fdopen(pipe_fd) as pipe:
        while keep_running:
            message = pipe.read()
            if message:
                handle_message(message)
                # print("Received: '{}'".format(message))
            # print("Doing other stuff")
            time.sleep(0.5)

def main():
    """Start indicator process."""
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath(get_icon_path("time-icon")), appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

    def handle_message(message):
        message = message.strip()
        if message == "start":
            indicator.set_icon(os.path.abspath(get_icon_path("start-icon")))
        elif message == "stop":
            indicator.set_icon(os.path.abspath(get_icon_path("stop-icon")))
        elif message == "pause":
            indicator.set_icon(os.path.abspath(get_icon_path("pause-icon")))
        else:
            print("Message not understood")

    # Launch thread waiting for messages
    pipe_thread = threading.Thread(target=open_pipe, args=(handle_message,))
    pipe_thread.start()

    # Run main process
    gtk.main()

def build_menu():
    """Build a menu with some items."""
    menu = gtk.Menu()

    # Add joke button
    # item_joke = gtk.MenuItem('Joke')
    # item_joke.connect('activate', joke)
    # menu.append(item_joke)

    # Add quit button
    item_quit = gtk.MenuItem('Cerrar')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    # Put buttons in the menu
    menu.show_all()
    return menu

def quit(source):
    """Respond to quit event button"""
    global keep_running
    gtk.main_quit()
    keep_running = False

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
