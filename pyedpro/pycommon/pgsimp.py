#!/usr/bin/python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, string, fnmatch, math
import random, time, subprocess, traceback, glob

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gui_testmode = False

# ------------------------------------------------------------------------
# An N pixel horizontal spacer. Defaults to X pix get_center
# Re-created for no dependency include of this module

class zSpacer(Gtk.HBox):

    def __init__(self, sp = None):
        GObject.GObject.__init__(self)
        #self.pack_start()
        #if gui_testmode:
        #    col = randcolstr(100, 200)
        #    self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)

# ------------------------------------------------------------------------

class   SimpleTree(Gtk.TreeView):

    def __init__(self, head = [], editx = [], skipedit = 0):

        Gtk.TreeView.__init__(self)

        self.callb = None
        self.chcallb = None

        # repair missing column
        if len(head) == 0:
            head.append("")

        if len(editx) == 0:
            editx.append("")

        self.types = []
        for aa in head:
            self.types.append(str)

        self.treestore = Gtk.TreeStore()
        self.treestore.set_column_types(self.types)

        cnt = 0
        for aa in head:
            # Create a CellRendererText to render the data
            cell = Gtk.CellRendererText()
            if cnt > skipedit:
                cell.set_property("editable", True)
                cell.connect("edited", self.text_edited, cnt)

            tvcolumn = Gtk.TreeViewColumn(aa)
            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, 'text', cnt)
            self.append_column(tvcolumn)
            cnt += 1

        self.set_model(self.treestore)
        self.connect("cursor-changed", self.selection)

    def text_edited(self, widget, path, text, idx):
        #print ("edited", widget, path, text, idx)
        self.treestore[path][idx] = text
        args = []
        for aa in self.treestore[path]:
            args.append(aa)
        self.chcallb(args)

    def selection(self, xtree):
        #print("simple tree sel", xtree)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            self.args = []
            for aa in range(len(self.types)):
                xstr = xmodel.get_value(xiter, aa)
                self.args.append(xstr)
            #print("selection", self.args)
            if self.callb:
                self.callb(self.args)

    def setcallb(self, callb):
        self.callb = callb

    def setCHcallb(self, callb):
        self.chcallb = callb

    def append(self, args):
        #print("append", args)
        piter = self.treestore.append(None, args)

    def sel_last(self):
        #print("sel last ...")
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        iter = self.treestore.get_iter_first()
        if not iter:
            return
        while True:
            iter2 = self.treestore.iter_next(iter)
            if not iter2:
                break
            iter = iter2.copy()
        sel.select_iter(iter)
        ppp = self.treestore.get_path(iter)
        self.scroll_to_cell(ppp, None, 0, 0, 0 )
        self.set_cursor(ppp, self.get_column(0), False)

        #sel.select_path(self.treestore.get_path(iter))

    def clear(self):
        self.treestore.clear()

# ------------------------------------------------------------------------

class   SimpleEdit(Gtk.TextView):

    def __init__(self, head = []):

        Gtk.TextView.__init__(self)
        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.set_editable(True)
        self.connect("unmap", self.unmapx)
        #self.connect("focus-out-event", self.focus_out)
        self.connect("key-press-event", self.area_key)
        self.modified = False
        self.text = ""
        self.savecb = None
        self.single_line = False

    def focus_out(self, win, arg):
        #print("SimpleEdit focus_out")
        self.check_saved()
        #self.mefocus = False

    def check_saved(self):
        if not self.buffer.get_modified():
            return
        #print("Saving")
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.text = self.buffer.get_text(startt, endd, False)
        if self.savecb:
            self.savecb(self.text)

    def focus_in(self, win, arg):
        pass
        #self.buffer.set_modified(False)
        #self.mefocus = True
        #print("SimpleEdit focus_in")

    def unmapx(self, widget):
        #print("SimpleEdit unmap", widget)
        pass

    def area_key(self, widget, event):
        #print("SimpleEdit keypress", event.string)
        #self.buffer.set_modified(True)

        if self.single_line:
            if event.string == "\r":
                #print("newline")
                if self.savecb:
                    try:
                        self.savecb(self.get_text())
                    except:
                        print("Error simpledit callback")
                return True

    def append(self, strx):
        self.check_saved()
        iter = self.buffer.get_end_iter()
        self.buffer.insert(iter, strx)
        self.buffer.set_modified(False)

    def clear(self):
        self.check_saved()
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.buffer.delete(startt, endd)
        self.buffer.set_modified(False)

    def setsavecb(self, callb):
        self.savecb = callb

    def get_text(self):
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, False)

    def set_text(self, txt, eventx = False):
        if eventx:
            self.check_saved()
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.buffer.delete(startt, endd)
        self.buffer.insert(startt, txt)
        self.buffer.set_modified(True)

# Select character by index

class   SimpleSel(Gtk.Label):

    def __init__(self, text = " ", callb = None, font="Mono 13"):
        self.text = text
        self.callb = callb
        self.axx = self.text.find("[All]")
        #self.axx = -1
        Gtk.Label.__init__(self, text)
        self.set_has_window(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.modify_font(Pango.FontDescription(font))
        self.lastsel = "All"

    def area_button(self, but, event):

        idx = int(prop * len(self.text))
        #print("width =", self.get_allocation().width)
        #print("idx", idx)
        #print("click", event.x, event.y)
        if self.text[idx] == " ":
             prop = event.x / float(self.get_allocation().width)
        try:
            # See of it is all
            if self.axx >= 0:
                if idx > self.axx:
                    #print("all", idx, self.text[idx-5:idx+7])
                    self.lastsel =  "All"
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].upper()
                    self.set_text(self.newtext)
                else:
                    self.lastsel =  self.text[idx]
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].lower()
                    self.set_text(self.newtext)
            else:
                self.lastsel =  self.text[idx]
                self.newtext = self.text[:idx] + self.text[idx].upper() + self.text[idx+1:]
                self.set_text(self.newtext)

            if self.callb:
                self.callb(self.lastsel)

        except:
            print(sys.exc_info())

# Give a proportional answer

class   NumberSel(Gtk.Label):

    def __init__(self, text = " ", callb = None, font="Mono 13"):
        self.text = text
        self.callb = callb
        self.axx = self.text.find("[All]")
        Gtk.Label.__init__(self, text)
        self.set_has_window(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.override_font(Pango.FontDescription(font))
        self.lastsel = "All"

    def area_button(self, but, event):

        #print("sss =", self.get_allocation().width)
        #print("click", event.x, event.y)

        prop = event.x / float(self.get_allocation().width)
        idx = int(prop * len(self.text))

        # Navigate to IDX
        if self.text[idx] == " ":
            idx += 1
        else:
            if self.text[idx-1] != " ":
                idx -= 1
        if idx >= len(self.text):
            return

        try:
            # See of it is all
            if self.axx >= 0:
                if idx > self.axx:
                    #print("all", idx, self.text[idx-5:idx+7])
                    self.lastsel =  "All"
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].upper()
                    self.set_text(self.newtext)
                else:
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].lower()
                    self.set_text(self.newtext)

            else:
                self.lastsel =  self.text[idx:idx+2]
                #print("lastsel", self.lastsel)
                self.newtext = self.text[:idx] + self.text[idx].upper() + self.text[idx+1:]
                self.set_text(self.newtext)

            if self.callb:
                self.callb(self.lastsel)

        except:
            print(sys.exc_info())


# ------------------------------------------------------------------------
# Letter selection control

class   LetterNumberSel(Gtk.VBox):

    def __init__(self, callb = None, font="Mono 13"):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = "abcdefghijklmnopqrstuvwxyz"
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel = SimpleSel(strx, self.letter, font)
        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        strn = "1234567890!@#$^&*_+ [All]"
        hbox3b = Gtk.HBox()
        hbox3b.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel2 = SimpleSel(strn, self.letter, font)
        hbox3b.pack_start(self.simsel2, 0, 0, 0)
        hbox3b.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.pack_start(hbox3a, 0, 0, False)
        self.pack_start(zSpacer(4), 0, 0, False)
        self.pack_start(hbox3b, 0, 0, False)

    def  letter(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

class   HourSel(Gtk.VBox):

    def __init__(self, callb = None):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = " 8 10 12 14 16 "
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel = NumberSel(strx, self.letter)
        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.pack_start(hbox3a, 0, 0, False)

    def  letter(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

class   MinSel(Gtk.VBox):

    def __init__(self, callb = None):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = " 0 10 20 30 40 50 "
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel = NumberSel(strx, self.letter)
        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.pack_start(hbox3a, 0, 0, False)

    def  letter(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

# ------------------------------------------------------------------------

class TextViewWin(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.callb = None
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self._create_textview();
        self._create_toolbar()
        self._create_buttons()

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        self.mysize = myfd.get_size() / Pango.SCALE
        self.myfam = myfd.get_family()
        self.textview.connect("key-press-event", self.area_key)
        #self.connect("button-press-event", self.area_button)
        #self.textview.connect("focus-out-event", self.focus_out)
        self.findcall = None;

    def area_key(self, widget, event):
        #print("TextViewWin keypress", event.string, event.keyval)
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == 102:
                #print("control find")
                if self.findcall:
                    # Call with object argument
                    self.findcall[0](self.findcall[1])

    '''
    def area_button(self, but, event):
        print("TextViewWin click", event.x, event.y)
        pass
    '''

    '''
    def focus_out(self, arg1, arg2):
        print("Focus out")
    '''

    def _create_toolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        button_norm = Gtk.ToolButton()
        button_norm.set_icon_name("format-text-none-symbolic")
        button_norm.set_tooltip_text("Remove formatting")
        toolbar.insert(button_norm, 0)

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        toolbar.insert(button_bold, 1)

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        toolbar.insert(button_italic, 2)

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        toolbar.insert(button_underline, 3)

        button_norm.connect("clicked", self.on_rm_clicked, self.tag_norm)
        button_bold.connect("clicked", self.on_button_clicked, self.tag_bold)
        button_italic.connect("clicked", self.on_button_clicked, self.tag_italic)
        button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

        toolbar.insert(Gtk.SeparatorToolItem(), 4)

        radio_justifyleft = Gtk.RadioToolButton()
        radio_justifyleft.set_icon_name("format-justify-left-symbolic")
        toolbar.insert(radio_justifyleft, 5)

        radio_justifycenter = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifycenter.set_icon_name("format-justify-center-symbolic")
        toolbar.insert(radio_justifycenter, 6)

        radio_justifyright = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyright.set_icon_name("format-justify-right-symbolic")
        toolbar.insert(radio_justifyright, 7)

        radio_justifyfill = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyfill.set_icon_name("format-justify-fill-symbolic")
        toolbar.insert(radio_justifyfill, 8)

        radio_justifyleft.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.LEFT
        )
        radio_justifycenter.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.CENTER
        )
        radio_justifyright.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.RIGHT
        )
        radio_justifyfill.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.FILL
        )

        toolbar.insert(Gtk.SeparatorToolItem(), 9)

        button_clear = Gtk.ToolButton()
        button_clear.set_icon_name("edit-clear-symbolic")
        button_clear.set_tooltip_text("Remove ALL formatting")
        button_clear.connect("clicked", self.on_clear_clicked)
        toolbar.insert(button_clear, 10)

        toolbar.insert(Gtk.SeparatorToolItem(), 11)

        button_search = Gtk.ToolButton()
        button_search.set_icon_name("system-search-symbolic")
        button_search.set_tooltip_text("Search current text")
        button_search.connect("clicked", self.on_search_clicked)
        toolbar.insert(button_search, 12)

        button_mag = Gtk.ToolButton()
        button_mag.set_icon_name("zoom-in-symbolic")
        button_mag.set_tooltip_text("Magnify Font")
        button_mag.connect("clicked", self.on_zoom_clicked)
        toolbar.insert(button_mag, 13)

        button_mag2 = Gtk.ToolButton()
        button_mag2.set_icon_name("zoom-out-symbolic")
        button_mag2.set_tooltip_text("Set smaller Font")
        button_mag2.connect("clicked", self.on_unzoom_clicked)
        toolbar.insert(button_mag2, 14)

    def on_zoom_clicked(self, arg1):

        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE

        fd = Pango.FontDescription()
        fd.set_size((mysize + 1) * Pango.SCALE)
        self.textview.modify_font(fd)

    def on_unzoom_clicked(self, arg1):

        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE

        fd = Pango.FontDescription()
        fd.set_size((mysize - 1) * Pango.SCALE)
        self.textview.modify_font(fd)

    def _create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        #self.textview.set_has_window(True)

        #self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        scrolledwindow.add(self.textview)

        #self.tag_norm = self.textbuffer.create_tag("norm", weight=Pango.Weight.NORMAL)
        self.tag_norm = self.textbuffer.create_tag("normal", style=Pango.Style.NORMAL)
        self.tag_bold = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tag_found = self.textbuffer.create_tag("found", background="yellow")
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

    def _create_buttons(self):

        #check_editable = Gtk.CheckButton(label="Editable")
        #check_editable.set_active(True)
        #check_editable.connect("toggled", self.on_editable_toggled)
        #self.grid.attach(check_editable, 0, 2, 1, 1)
        ##
        #check_cursor = Gtk.CheckButton(label="Cursor Visible")
        #check_cursor.set_active(True)
        #check_editable.connect("toggled", self.on_cursor_toggled)
        #self.grid.attach_next_to(
        #    check_cursor, check_editable, Gtk.PositionType.RIGHT, 1, 1)

        # ---------------------------------------------------------------------------------

        radio_wrapword =  Gtk.RadioButton.new_with_label_from_widget(None, "Word")
        self.grid.attach(radio_wrapword, 0, 3, 1, 1)

        radio_wrapchar =  Gtk.RadioButton.new_with_label_from_widget(radio_wrapword, "Character")
        self.grid.attach_next_to(
            radio_wrapchar, radio_wrapword, Gtk.PositionType.RIGHT, 1, 1)

        radio_wrapnone = Gtk.RadioButton.new_with_label_from_widget(radio_wrapword, "None")
        self.grid.attach_next_to(
                radio_wrapnone, radio_wrapchar, Gtk.PositionType.RIGHT, 1, 1)

        radio_wrapnone.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.NONE)
        radio_wrapchar.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.CHAR)
        radio_wrapword.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.WORD)

    def get_text(self):
        startt = self.textbuffer.get_start_iter()
        endd = self.textbuffer.get_end_iter()
        txt = self.textbuffer.get_text(startt, endd, False)
        return txt

    def get_all(self):
        print("Get_all called")
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, True)

    def  get_modified(self):
        return self.textbuffer.get_modified()

    def set_text(self, txt):
        if self.textbuffer.get_modified():
            startt = self.textbuffer.get_start_iter()
            endd = self.textbuffer.get_end_iter()
            old = self.textbuffer.get_text(startt, endd, False)
            if self.callb:
                self.callb(old)
            #print("old_content", old)
        self.textbuffer.set_text(txt)
        self.textbuffer.set_modified(False)

    def on_rm_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.remove_tag(self.tag_bold, start, end)
            self.textbuffer.remove_tag(self.tag_italic, start, end)
            self.textbuffer.remove_tag(self.tag_underline, start, end)

    def on_button_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)

    def on_clear_clicked(self, widget):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.remove_all_tags(start, end)

    def on_editable_toggled(self, widget):
        self.textview.set_editable(widget.get_active())

    def on_cursor_toggled(self, widget):
        self.textview.set_cursor_visible(widget.get_active())

    def on_wrap_toggled(self, widget, mode):
        self.textview.set_wrap_mode(mode)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    def on_search_clicked(self, widget):

        if self.findcall:
            # Call with object argument
            self.findcall[0](self.findcall[1])

        #dialog = SearchDialog(None)
        #response = dialog.run()
        #if response == Gtk.ResponseType.OK:
        #    cursor_mark = self.textbuffer.get_insert()
        #    start = self.textbuffer.get_iter_at_mark(cursor_mark)
        #    if start.get_offset() == self.textbuffer.get_char_count():
        #        start = self.textbuffer.get_start_iter()
        #
        #    self.search_and_mark(dialog.entry.get_text(), start)

        dialog.destroy()

    def search_and_mark(self, text, start):
        end = self.textbuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match is not None:
            match_start, match_end = match
            self.textbuffer.apply_tag(self.tag_found, match_start, match_end)
            self.search_and_mark(text, match_end)

# EOF

