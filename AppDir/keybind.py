import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')

from gi.repository import Gtk
from gi.repository import Keybinder

def callback(keystr, user_data):
    print ("Handling", user_data)
    print ("Event time:", Keybinder.get_current_event_time())
    Gtk.main_quit()

if __name__ == '__main__':
    keystr = "<Ctrl><Alt>M"
    Keybinder.init()
    Keybinder.bind(keystr, callback, "keystring %s (user data)" % keystr)
    print ("Press", keystr, "to handle keybinding and quit")
    Gtk.main()

