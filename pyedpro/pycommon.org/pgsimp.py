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
import pgbox

#print("pyedpro pgsimp", __file__)

#print("pgsimp", __file__)

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

    def __init__(self, head = [], editx = [], skipedit = 0, xalign = 0.5):

        Gtk.TreeView.__init__(self)

        self.callb = None
        self.chcallb = None
        self.actcallb = None

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
            #cell.set_property("alignment", Pango.Alignment.CENTER)
            #cell.set_property("align-set", True)
            cell.set_property("xalign", xalign)

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
        self.connect("row-activated", self.activate)

    def activate(self, xtree, arg2, arg3):
        #print("Activated", row, arg2, arg3)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            #print("Activated str", xstr)
            if self.actcallb:
                self.actcallb(xstr)

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

    def setActcallb(self, callb):
        self.actcallb = callb

    def append(self, args):
        #print("append", args)
        piter = self.treestore.append(None, args)

    # TreeStore
    def insert(self, parent, pos, args):
        print("insert", parent, pos, args)
        piter = self.treestore.insert(parent, pos, args)

    def sel_first(self):
        #print("sel first ...")
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        iter = self.treestore.get_iter_first()
        sel.select_iter(iter)
        ppp = self.treestore.get_path(iter)
        self.scroll_to_cell(ppp, None, 0, 0, 0 )
        self.set_cursor(ppp, self.get_column(0), False)

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

    def find_item(self, item):

        ''' find if we already have an item like that '''

        #print("find", item)
        found = 0
        iter = self.treestore.get_iter_first()
        if not iter:
            return
        while True:
            value = self.treestore.get_value(iter, 0)
            #print("item:", value)
            if item == value:
                found = True
                break
            iter2 = self.treestore.iter_next(iter)
            if not iter2:
                break
            iter = iter2.copy()
        return found

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


# ------------------------------------------------------------------------
# Letter selection control

class   LetterNumberSel(Gtk.VBox):

    def __init__(self, callb = None, font="Mono 13"):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = "abcdefghijklmnopqrstuvwxyz"
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel =  internal_SimpleSel(strx, self.letter, font)

        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        strn = "1234567890!@#$^&*_+ [All]"
        hbox3b = Gtk.HBox()
        hbox3b.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel2 = internal_SimpleSel(strn, self.letter, font)
        hbox3b.pack_start(self.simsel2, 0, 0, 0)
        hbox3b.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
        self.simsel.connect("enter_notify_event", self.enter_label)
        self.simsel.connect("leave_notify_event", self.leave_label)
        self.simsel2.connect("enter_notify_event", self.enter_label)
        self.simsel2.connect("leave_notify_event", self.leave_label)

        self.simsel2.other = self.simsel
        self.simsel.other = self.simsel2

        self.pack_start(hbox3a, 0, 0, False)
        self.pack_start(zSpacer(4), 0, 0, False)
        self.pack_start(hbox3b, 0, 0, False)

    def enter_label(self, arg, arg2):
        #print("Enter")
        self.get_window().set_cursor(self.hand_cursor)

    def leave_label(self, arg, arg2):
        #print("Leave")
        self.get_window().set_cursor()

    def  letter(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

# Select character by index (do not call directly)

class   internal_SimpleSel(Gtk.Label):

    def __init__(self, text = " ", callb = None, font="Mono 13"):
        self.text = text
        self.callb = callb
        self.axx = self.text.find("[All]")
        #self.axx = -1
        Gtk.Label.__init__(self, label=text)
        self.set_has_window(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.modify_font(Pango.FontDescription(font))
        self.lastsel = "All"
        self.lastidx = 0
        self.other = None

    def area_button(self, but, event):

        prop = event.x / float(self.get_allocation().width)
        idx = int(prop * len(self.text))
        #print("width =", self.get_allocation().width)
        #print("idx", idx, )
        #print("click", event.x, event.y)
        try:
            # See of it is all
            if self.axx >= 0:
                if idx > self.axx:
                    #print("all", idx, self.text[idx-5:idx+7])
                    self.lastsel =  "All"
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].upper()
                    self.set_text(self.newtext)
                else:
                    if self.text[idx].isalpha():
                        self.newtext = self.text[:self.axx] + self.text[self.axx:].lower()
                    else:
                        #print("Non alpha, filling pipe char")
                        #print("old sel", self.lastidx, "new sel", idx, self.text[:idx])
                        if  self.lastidx + 2 < idx:
                            idx -= 1
                        self.lastsel =  self.text[idx]
                        self.newtext = self.text[:idx] + "|" + self.text[idx] + "|" + self.text[idx+1:]
                        self.lastidx =  idx

                self.set_text(self.newtext)

            else:
                self.lastsel =  self.text[idx]
                self.newtext = self.text[:idx] + self.text[idx].upper() + self.text[idx+1:]
                self.set_text(self.newtext)

            # Clear the other
            if self.other:
                self.other.newtext = self.other.text[:]
                self.other.set_text(self.other.newtext)

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


# EOF

