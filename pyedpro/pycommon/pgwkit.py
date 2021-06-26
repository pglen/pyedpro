#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings
import inspect

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
sys.path.append(realinc)

from pgutils import  *
from pggui import  *
from pgsimp import  *

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

try:
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2

    #print(WebKit2)
    #print("Webkit ver", WebKit2.get_major_version(), WebKit2.get_minor_version(), WebKit2.get_micro_version())

except:
    # Define a blank one  -- too complex to work
    #class   WebKit2():
    #    def __init__(self):
    #        pass
    #    class  WebView(Gtk.Label):
    #        def __init__(self):
    #            pass
    #        def load_uri(self, url):
    #            pass
    print("Cannot import webkit2, web functions may not be available.")
    raise

class pgwebw(WebKit2.WebView):

    def __init__(self, xlink=None):
        try:
            GObject.GObject.__init__(self)
        except:
            pass
        self.xlink = xlink

    def do_ready_to_show(self):
        #print("do_ready_to_show() was called")
        pass

    def do_load_changed(self, status):

        #print("do_load_changed() was called", status)
        if self.get_uri():
            if self.xlink:
                self.xlink.status.set_text("Loading ... " + self.get_uri()[:64])

        if status == 3: #WebKit2.LoadEvent.WEBKIT_LOAD_FINISHED:
            #print("got WEBKIT_LOAD_FINISHED")
            if self.get_uri():
                if self.xlink:
                    self.xlink.edit.set_text(self.get_uri()[:64])
                    self.xlink.status.set_text("Finished: " + self.get_uri()[:64])
            self.grab_focus()

    def do_load_failed(self, load_event, failing_uri, error):
        print("do_load_failed() was called", failing_uri)
        if self.xlink:
            self.xlink.status.set_text("Failed: " + failing_uri[:64])

    def on_action(self, action):
        self.editor.run_javascript("document.execCommand('%s', false, false);" % action.get_name())

    def on_paste(self, action):
        self.editor.execute_editing_command(WebKit2.EDITING_COMMAND_PASTE)

    def on_new(self, action):
        self.editor.load_html("", "file:///")

    def on_select_font(self, action):
        dialog = Gtk.FontChooserDialog("Select a font")
        if dialog.run() == Gtk.ResponseType.OK:
            fname = dialog.get_font_desc().get_family()
            fsize = dialog.get_font_desc().get_size()
            self.editor.run_javascript("document.execCommand('fontname', null, '%s');" % fname)
            self.editor.run_javascript("document.execCommand('fontsize', null, '%s');" % fsize)
        dialog.destroy()

    def on_select_color(self, action):
        dialog = Gtk.ColorChooserDialog("Select Color")
        if dialog.run() == Gtk.ResponseType.OK:
            (r, g, b, a) = dialog.get_rgba()
            color = "#%0.2x%0.2x%0.2x%0.2x" % (
                int(r * 255),
                int(g * 255),
                int(b * 255),
                int(a * 255))
            self.editor.run_javascript("document.execCommand('forecolor', null, '%s');" % color)
        dialog.destroy()

    def on_insert_link(self, action):
        dialog = Gtk.Dialog("Enter a URL:", self, 0,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        entry = Gtk.Entry()
        dialog.vbox.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.editor.run_javascript(
                "document.execCommand('createLink', true, '%s');" % entry.get_text())
        dialog.destroy()

    def on_insert_image(self, action):
        dialog = Gtk.FileChooserDialog("Select an image file", self, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.editor.run_javascript(
                "document.execCommand('insertImage', null, '%s');" % fn)
        dialog.destroy()

    def on_open(self, action):
        dialog = Gtk.FileChooserDialog("Select an HTML file", self, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.filename = fn
                with open(fn) as fd:
                    self.editor.load_html(fd.read(), "file:///")
        dialog.destroy()

    def on_save(self, action):
        def completion(html, user_data):
            open_mode = user_data
            with open(self.filename, open_mode) as fd:
                fd.write(html)

        if self.filename:
            self.get_html(completion, 'w')
        else:
            dialog = Gtk.FileChooserDialog("Select an HTML file", self, Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            if dialog.run() == Gtk.ResponseType.OK:
                self.filename = dialog.get_filename()
                self.get_html(completion, "w+")
            dialog.destroy()

    def get_html(self, completion_function, user_data):
        def javascript_completion(obj, result, user_data):
            html = self.editor.get_title()
            completion_function(html, user_data)
        self.editor.run_javascript("document.title=document.documentElement.innerHTML;",
                                   None,
                                   javascript_completion,
                                   user_data)


def generate_ui(self):
    ui_def = """
    <ui>
    <menubar name="menubar_main">
        <menu action="menuFile">
        <menuitem action="new" />
        <menuitem action="open" />
        <menuitem action="save" />
        </menu>
        <menu action="menuEdit">
        <menuitem action="cut" />
        <menuitem action="copy" />
        <menuitem action="paste" />
        </menu>
        <menu action="menuInsert">
        <menuitem action="insertimage" />
        </menu>
        <menu action="menuFormat">
        <menuitem action="bold" />
        <menuitem action="italic" />
        <menuitem action="underline" />
        <menuitem action="strikethrough" />
        <separator />
        <menuitem action="font" />
        <menuitem action="color" />
        <separator />
        <menuitem action="justifyleft" />
        <menuitem action="justifyright" />
        <menuitem action="justifycenter" />
        <menuitem action="justifyfull" />
        </menu>
    </menubar>
    <toolbar name="toolbar_main">
        <toolitem action="new" />
        <toolitem action="open" />
        <toolitem action="save" />
        <separator />
        <toolitem action="undo" />
        <toolitem action="redo" />
        <separator />
        <toolitem action="cut" />
        <toolitem action="copy" />
        <toolitem action="paste" />
    </toolbar>
    <toolbar name="toolbar_format">
        <toolitem action="bold" />
        <toolitem action="italic" />
        <toolitem action="underline" />
        <toolitem action="strikethrough" />
        <separator />
        <toolitem action="font" />
        <toolitem action="color" />
        <separator />
        <toolitem action="justifyleft" />
        <toolitem action="justifyright" />
        <toolitem action="justifycenter" />
        <toolitem action="justifyfull" />
        <separator />
        <toolitem action="insertimage" />
        <toolitem action="insertlink" />
    </toolbar>
    </ui>
    """

    actions = Gtk.ActionGroup("Actions")
    actions.add_actions([
    ("menuFile", None, "_File"),
    ("menuEdit", None, "_Edit"),
    ("menuInsert", None, "_Insert"),
    ("menuFormat", None, "_Format"),

    ("new", Gtk.STOCK_NEW, "_New", None, None, self.on_new),
    ("open", Gtk.STOCK_OPEN, "_Open", None, None, self.on_open),
    ("save", Gtk.STOCK_SAVE, "_Save", None, None, self.on_save),

    ("undo", Gtk.STOCK_UNDO, "_Undo", None, None, self.on_action),
    ("redo", Gtk.STOCK_REDO, "_Redo", None, None, self.on_action),

    ("cut", Gtk.STOCK_CUT, "_Cut", None, None, self.on_action),
    ("copy", Gtk.STOCK_COPY, "_Copy", None, None, self.on_action),
    ("paste", Gtk.STOCK_PASTE, "_Paste", None, None, self.on_paste),

    ("bold", Gtk.STOCK_BOLD, "_Bold", "<ctrl>B", None, self.on_action),
    ("italic", Gtk.STOCK_ITALIC, "_Italic", "<ctrl>I", None, self.on_action),
    ("underline", Gtk.STOCK_UNDERLINE, "_Underline", "<ctrl>U", None, self.on_action),
    ("strikethrough", Gtk.STOCK_STRIKETHROUGH, "_Strike", "<ctrl>T", None, self.on_action),
    ("font", Gtk.STOCK_SELECT_FONT, "Select _Font", "<ctrl>F", None, self.on_select_font),
    ("color", Gtk.STOCK_SELECT_COLOR, "Select _Color", None, None, self.on_select_color),

    ("justifyleft", Gtk.STOCK_JUSTIFY_LEFT, "Justify _Left", None, None, self.on_action),
    ("justifyright", Gtk.STOCK_JUSTIFY_RIGHT, "Justify _Right", None, None, self.on_action),
    ("justifycenter", Gtk.STOCK_JUSTIFY_CENTER, "Justify _Center", None, None, self.on_action),
    ("justifyfull", Gtk.STOCK_JUSTIFY_FILL, "Justify _Full", None, None, self.on_action),

    ("insertimage", "insert-image", "Insert _Image", None, None, self.on_insert_image),
    ("insertlink", "insert-link", "Insert _Link", None, None, self.on_insert_link),
    ])

    actions.get_action("insertimage").set_property("icon-name", "insert-image")
    actions.get_action("insertlink").set_property("icon-name", "insert-link")

    ui = Gtk.UIManager()
    ui.insert_action_group(actions)
    ui.add_ui_from_string(ui_def)
    return ui

# EOF
