#!/bin/python3
# -*- utf:8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
socket_id = sys.argv[1]
plug = Gtk.Plug.new(int(socket_id))
plug.connect('destroy', Gtk.main_quit)
class SocketDialogWindow(Gtk.Window):
    def __init__(self):
        box = Gtk.Box(spacing=6)

        button1 = Gtk.Button(label="Information")
        button1.connect("clicked", self.on_info_clicked)
        box.add(button1)
        plug.add(box) # box widget added to python plug
        plug.show_all()
    def on_info_clicked(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Info about Python Sample Plugin",
        )
        dialog.format_secondary_text(
            "Copyright \xc2\xa9 2006-2019 Xfce development team\n"
        )
        dialog.run()
        print("INFO dialog closed")
        dialog.destroy()
SocketDialogWindow()
