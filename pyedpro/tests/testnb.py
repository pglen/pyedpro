#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Notebook Tab Drag and Drop Example (GTK+3 & Python3)
#
# Requirements:
# * Python (>=3.5)
#   https://www.python.org/
#
# * GTK+ (>=3.0)
#   https://www.gtk.org/
#
# Dependencies:
# * PyGObject
#   https://pygobject.readthedocs.io/en/latest/
#
# References:
# * GtkNotebook: GTK+ 3 Reference Manual
#   https://developer.gnome.org/gtk3/stable/GtkNotebook.html#gtk-notebook-set-tab-detachable
#
# * tests/testnotebookdnd.c - master - GNOME / gtk
#   https://gitlab.gnome.org/GNOME/gtk/blob/master/tests/testnotebookdnd.c
#
# * Drag and drop (DND) of gtk.Notebook tab to another widget
#   http://python.6.x6.nabble.com/Drag-and-drop-DND-of-gtk-Notebook-tab-to-another-widget-td1948624.html
#
# License: CC0 1.0
# see https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gio, Gtk


def main():
    app = Gtk.Application.new('com.github.ma8ma.test',
                              Gio.ApplicationFlags.FLAGS_NONE)
    app.connect('activate', on_activate)
    app.run([])


def on_activate(app):
    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

    notebook = Gtk.Notebook.new()
    notebook.connect_after('drag-begin', _sig_notebook_drag_begin)
    notebook.connect_after('drag-data-get', _sig_notebook_drag_data_get)
    box.pack_start(notebook, True, True, 0)

    label = Gtk.Label.new('Drag me!')
    child_widget = Gtk.Entry.new()
    notebook.append_page(child_widget, label)
    notebook.set_tab_detachable(child_widget, True)  # Enable DnD

    button = Gtk.Button.new_with_label('Drop here!')
    # Gdk.DragAction *must* be MOVE. (GTK+ 3.18)
    button.drag_dest_set(Gtk.DestDefaults.HIGHLIGHT | Gtk.DestDefaults.DROP
                         | Gtk.DestDefaults.MOTION,
                         [Gtk.TargetEntry.new('GTK_NOTEBOOK_TAB',
                                              Gtk.TargetFlags.SAME_APP, 0)],
                         Gdk.DragAction.MOVE)
    button.connect('drag-drop', _sig_drag_drop)
    button.connect_after('drag-data-received', _sig_drag_data_received)
    box.pack_start(button, True, True, 0)

    window = Gtk.ApplicationWindow.new(app)
    window.set_default_size(300, 300)
    window.set_title('Notebook Tab DnD Example')
    window.add(box)
    window.show_all()


drag_page_number = 0


def _sig_notebook_drag_begin(widget, context):
    global drag_page_number
    drag_page_number = widget.get_current_page()
    print('drag-begin:', drag_page_number, widget)


def _sig_notebook_drag_data_get(widget, context, selection, info, timestamp):
    print('drag-data-get:', drag_page_number, selection.get_target())
    selection.set(selection.get_target(), 8, b'%d' % (drag_page_number,))


def _sig_drag_drop(widget, context, x, y, timestamp):
    print('drag-drop:', widget)
    if 'GTK_NOTEBOOK_TAB' in context.list_targets():
        widget.drag_get_data(context, 'GTK_NOTEBOOK_TAB')
    context.finish(True, False, timestamp)
    return True


def _sig_drag_data_received(widget, context, x, y, selection, info, timestamp):
    print('drag-data-received:', selection.get_data())
    src_widget = Gtk.drag_get_source_widget(context)
    the_page_number = int(selection.get_data())
    child_widget = src_widget.get_nth_page(the_page_number)
    child_widget.set_text('Thank you!')


if __name__ == '__main__':
    main()

