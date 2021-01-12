#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class GUI:
    def __init__(self):

        self.window = Gtk.Window()
        self.window.set_size_request(400, 400)
        notebook = Gtk.Notebook()
        self.window.add(notebook)
        notebook.connect('create-window', self.notebook_create_window)
        notebook.set_group_name('0') # very important for DND
        for i in range (4):
            label = Gtk.Label('label in page number ' + str(i))
            tab_label = Gtk.Label('page ' + str(i))
            notebook.append_page(label, tab_label)
            notebook.set_tab_detachable(label, True)
        self.window.show_all()
        self.window.connect('destroy', Gtk.main_quit)

    def notebook_create_window (self, notebook, widget, x, y):
        # handler for dropping outside of current window
        window = Gtk.Window()
        new_notebook = Gtk.Notebook()
        window.add(new_notebook)
        new_notebook.set_group_name('0') # very important for DND
        new_notebook.connect('page-removed', self.notebook_page_removed, window)
        window.connect('destroy', self.sub_window_destroyed, new_notebook, notebook)
        window.set_transient_for(self.window)
        window.set_destroy_with_parent(True)
        window.set_size_request(400, 400)
        window.move(x, y)
        window.show_all()
        return new_notebook

    def notebook_page_removed (self, notebook, child, page, window):
        #destroy the sub window after the notebook is empty
        if notebook.get_n_pages() == 0:
            window.destroy()




    def sub_window_destroyed (self, window, cur_notebook, dest_notebook):
        # if the sub window gets destroyed, push pages back to the main window
        # detach the notebook pages in reverse sequence to avoid index errors
        for page_num in reversed(range(cur_notebook.get_n_pages())):
            widget = cur_notebook.get_nth_page(page_num)
            tab_label = cur_notebook.get_tab_label(widget)
            cur_notebook.detach_tab(widget)
            dest_notebook.append_page(widget, tab_label)
            dest_notebook.set_tab_detachable(widget, True)

app = GUI()
Gtk.main()

