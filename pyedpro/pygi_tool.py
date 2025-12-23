#!/usr/bin/env python3

import os, sys, getopt, signal, random, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import Gio

ui_info = \
'''<ui>
    <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='New'/>
      <menuitem action='Open'/>
      <menuitem action='Save'/>
     </menu>
    </menubar>
    <toolbar  name='ToolBar'>
        <toolitem action='New'/>
        <toolitem action='Open'/>
        <toolitem action='Save'/>
     </toolbar>
</ui>'''

def create_action_group(self):

    entries = (
      ( "FileMenu", None, "_File" ),                # name, stock id, label

      ( "New", Gtk.STOCK_NEW,                       # name, stock id
        "_New", "<control>N",                       # label, accelerator
        "Create a new file",                        # tooltip
        self.activate_action ),

      ( "Open", Gtk.STOCK_OPEN,
        "_Open", "<control>O",
        "Open a file",
        self.activate_action ),

      ( "Save", Gtk.STOCK_SAVE,
        "_Save", "<control>S",
        "Save this  file",
        self.activate_action ),
    )

    action_group = Gtk.ActionGroup(name="AppWindowActions")
    action_group.add_actions(entries)
    #action_group.add_toggle_actions(toggle_entries)
    #action_group.add_radio_actions(color_entries, COLOR_RED, self.activate_radio_action)
    #action_group.add_radio_actions(shape_entries, SHAPE_OVAL, self.activate_radio_action)

    return action_group

class myWindow(Gtk.Window):

    def __init__(self):
        super().__init__()
        self.connect("delete-event", Gtk.main_quit)
        self.connect("destroy", Gtk.main_quit)
        self.set_default_size(300, 400)

        warnings.simplefilter("ignore")
        self.merge = Gtk.UIManager()
        mergeid = self.merge.add_ui_from_string(ui_info)
        self.acg = create_action_group(self)
        self.merge.insert_action_group(self.acg, 0)
        self.accel = self.merge.get_accel_group()
        self.tbar = self.merge.get_widget("/ToolBar")
        self.mbar = self.merge.get_widget("/MenuBar")
        warnings.simplefilter("default")

        self.mbar.show()
        self.tbar.show()

        self.headbar = Gtk.HeaderBar()
        self.headbar.set_decoration_layout("icon,menu:minimize,maximize,close")
        self.headbar.set_show_close_button(True)
        self.set_titlebar(self.headbar)

        button = Gtk.Button()
        button.connect("pressed", self.doall)
        button.set_tooltip_text("Will execute ./cycle.sh in current directory")

        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

        self.headbar.pack_end(button)

        vbox = Gtk.VBox()
        vbox.pack_start(self.mbar, 0, 0, 0)
        vbox.pack_start(self.tbar, 0, 0, 0)
        vbox.pack_start(Gtk.Label(label="Hello"), 1, 1, 0)
        self.add(vbox)

    def doall(self, arg1):
        print("doall")
        pass

    def activate_action(self, action):
        print("activate_action:", action)

ww = myWindow()
try:
    ww.set_icon_from_file("pedlib/images/pyedpro.png")
except:
    pass

ww.show_all()
Gtk.main()
