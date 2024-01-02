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

sys.path.append('..')
import pycommon.pgutils

box_testmode = False

# ------------------------------------------------------------------------

class Rectangle():

    # Accept rect, array, integers
    def __init__(self, *rrr):
        #Gdk.Rectangle.__init__(self)
        if len(rrr) == 4:
            idx = 0
            for aa in rrr:
                bb = int(aa)
                if idx == 0:
                    self.x = bb
                elif idx == 1:
                    self.y = bb
                elif idx == 2:
                    #self.width = bb
                    self.w = bb
                elif idx == 3:
                    #self.height = bb
                    self.h = bb
                else:
                    raise ValueError
                idx += 1
        else:
            for aaa in rrr:
                self.x = aaa[0]; self.y =  aaa[1]
                self.w =  aaa[2];
                #self.width =  aaa[2];
                self.h =  aaa[3]
                #self.height =  aaa[3]
                break
            pass

    # Make it smaller
    def resize(self, ww, hh = 0):
        if hh == 0:
            hh = ww

        #if ww + self.w <= 0 or hh + self.h <= 0:
        #    raise (ValuError, "Cannot have negative rect size")

        self.x -= ww/2; self.w += ww
        self.y -= hh/2; self.h += hh

    def copy(self):
        #print("rect to copy", str(self))
        #print("rect to copy", dir(self))
        nnn = Rectangle()                   # New Instance
        '''
        # Self
        for aa in dir(self):
            try:
                #nnn.__setattr__(aa, self.__getattribute__(aa))
                nnn.aa = self.__getattribute__(aa)
                #print("cp:", aa, end = "")
                #if type(self.__getattribute__(aa)) == int:
                #    print(" -> ", self.__getattribute__(aa), end= " ")
                #print(" --- ", end = "")
            except:
                #print(sys.exc_info())
                print("no", aa)
                pass
        '''

        # Assign explictly
        nnn.x = self.x + 0
        nnn.y = self.y + 0
        nnn.w = self.w + 0
        nnn.h = self.h + 0

        #nnn.width = self.width + 1
        #nnn.height = self.height + 1

        #print("rect out", str(nnn))
        #print("rect out", dir(nnn))
        return nnn

    # I was too lazy to write it; Crappy Gdt rect kicked me to it

    # ==========    self
    # =        =
    # =    ----=----
    # ====|======   |  rect2
    #     |         |
    #      ---------

    def intersect(self, rect2):

        urx = self.x + self.w;      lry = self.y + self.h
        urx2 = rect2.x + rect2.w;   lry2 = rect2.y + rect2.h
        inter = 0

        # X intersect
        if rect2.x >= self.x and rect2.x <= urx:
            inter += 1;
        # Y intersect
        if rect2.y >= self.y and rect2.y <= lry:
            inter += 1;

        # X intersect rev
        if self.x >= rect2.x and self.x <= urx2:
            inter += 1;
        # Y intersect rev
        if self.y >= rect2.y and self.y <= lry2:
            inter += 1;

        #print("inter", inter, str(self), "->", str(rect2))
        return (inter >= 2, self.x)

    # I was too lazy to write it; Crappy Gdt rect kicked me to it
    def contain(self, rect2):
        #self.dump()
        #rect2.dump()
        inter = 0
        # X intersect
        if rect2.x >= self.x and rect2.x + rect2.w <= self.x + self.w:
            inter += 1;
        # Y intersect
        if rect2.y >= self.y and rect2.y + rect2.h <= self.y + self.h:
            inter += 1;
        #print("inter", inter)
        return (inter == 2, self.x)

    # Convert index to values
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.w
        elif key == 3:
            return self.h
        else:
            raise IndexError;

    def dump(self):
        return (self.x, self.y, self.w, self.h)

    '''
    # This was killed in favour of self implemented Rectangle class
    def __getattr__(self, attr):
        if attr == "w":
            return self.width
        elif attr == "h":
            return self.height
        else:
            return super(Gdk.Rectangle, self).__getattr__(attr)

    def __setattr__(self, attr, val):
        if attr == "w":
            self.width = val
        elif attr == "h":
            self.height = val
        else:
            super(Gdk.Rectangle, self).__setattr__(attr, val)
    '''

    def __str__(self):
        return "R: x=%d y=%d w=%d h=%d" % (self.x, self.y, self.w, self.h)

# ------------------------------------------------------------------------
# An N pixel horizontal spacer. Defaults to X pix

class xSpacer(Gtk.HBox):

    def __init__(self, sp = None):
        GObject.GObject.__init__(self)
        #self.pack_start()
        if box_testmode:
            col = pgutils.randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)

# ------------------------------------------------------------------------
# An N pixel spacer. Defaults to 1 char height / width

class Spacer(Gtk.Label):

    global box_testmode

    def __init__(self, sp = 1, title=None, left=False, bottom=False, test=False):

        GObject.GObject.__init__(self)

        #sp *= 1000
        #self.set_markup("<span  size=\"" + str(sp) + "\"> </span>")
        #self.set_text(" " * sp)

        if title:
            self.set_text(title)
        else:
            self.set_text(" " * sp)

        if left:
            self.set_xalign(0)

        if bottom:
            self.set_yalign(1)

        if test or box_testmode:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#888888"))

        #self.set_property("angle", 15)
        #attr = self.get_property("attributes")
        #attr2 = Pango.AttrList()
        #print ("attr", dir(attr))
        #attr.
        #self.set_property("attributes", attr)
        #self.set_property("label", "wtf")
        #self.set_property("background-set", True)

# ------------------------------------------------------------------------
# This override covers / hides the complexity of the treeview and the
# textlisbox did not have the needed detail

class ListBox(Gtk.TreeView):

    def __init__(self, limit = -1, colname = ''):

        self.limit = limit
        self.treestore = Gtk.TreeStore(str)
        Gtk.TreeView.__init__(self, self.treestore)

        cell = Gtk.CellRendererText()
        # create the TreeViewColumn to display the data
        tvcolumn = Gtk.TreeViewColumn(colname)
        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        tvcolumn.add_attribute(cell, 'text', 0)

        # add tvcolumn to treeview
        self.append_column(tvcolumn)
        self.set_activate_on_single_click (True)

        self.callb = None
        self.connect("row-activated",  self.tree_sel)

    def tree_sel(self, xtree, xiter, xpath):
        #print("tree_sel", xtree, xiter, xpath)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            #print("Selected", xstr)
            if self.callb:
                self.callb(xstr)
        pass

    def set_callback(self, funcx):
        self.callb = funcx

    # Delete previous contents
    def clear(self):
        try:
            while True:
                root = self.treestore.get_iter_first()
                if not root:
                    break
                try:
                    self.treestore.remove(root)
                except:
                    print("except: treestore remove")

        except:
            print("update_tree", sys.exc_info())
            pass

    # Select Item. -1 for select none; Rase Valuerror for wrong index.
    def select(self, idx):
        ts = self.get_selection()
        if idx == -1:
            ts.unselect_all()
            return
        iter = self.treestore.get_iter_first()
        for aa in range(idx):
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
        if not iter:
            pass
            #raise ValueError("Invalid selection index.")
        ts.select_iter(iter)

    # Return the number of list items
    def get_size(self):
        cnt = 0
        iter = self.treestore.get_iter_first()
        if not iter:
            return cnt
        cnt = 1
        while True:
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
            cnt += 1
        return cnt

    def get_item(self, idx):
        cnt = 0; res = ""
        iter = self.treestore.get_iter_first()
        if not iter:
            return ""
        cnt = 1
        while True:
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
            if cnt == idx:
                res = self.treestore.get_value(iter, 0)
                break
            cnt += 1
        return res

    def append(self, strx):
        if self.limit != -1:
            # count them
            cnt = self.get_size()
            #print("limiting cnt=", cnt, "limit=", self.limit)
            for aa in range(cnt - self.limit):
                iter = self.treestore.get_iter_first()
                if not iter:
                    break
                try:
                    self.treestore.remove(iter)
                except:
                    print("except: treestore remove lim")

        last = self.treestore.append(None, [strx])
        self.set_cursor_on_cell(self.treestore.get_path(last), None, None, False)

    def get_text(self):
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            return xmodel.get_value(xiter, 0)

    # Get current IDX -1 for none
    def get_curridx(self):
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        if not xiter:
            return -1

        # Count back from match
        cnt = 0
        while True:
            xiter = self.treestore.iter_previous(xiter)
            if not xiter:
                break
            #print ("xiter:", xiter)
            cnt += 1
        return cnt

# ------------------------------------------------------------------------

class   ComboBox(Gtk.ComboBox):

    def __init__(self, init_cont = [], callme = None):

        self.store = Gtk.ListStore(str)
        Gtk.ComboBox.__init__(self)

        self.set_model(self.store)
        cell = Gtk.CellRendererText()

        cell.set_property("text", "hello")
        #cell.set_property("background", "#ffff00")
        #cell.set_property("background-set", True)
        cell.set_padding(10, 0)

        if callme:
            self.connect("changed", callme)

        #cell.set_property("foreground", "#ffff00")
        #cell.set_property("foreground-set", True)
        #print("background-set", cell.get_property("background-set"))
        #print("foreground-set", cell.get_property("foreground-set"))
        #print(" list_properties", cell.list_properties())

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_entry_text_column(0)

        for bb in init_cont:
            self.store.append([bb])

        self.connect("changed", self.combo_changed)

    def combo_changed(self, combo):
        name = ""
        tree_iter = combo.get_active_iter()
        try:
            if tree_iter is not None:
                model = combo.get_model()
                name = model[tree_iter][0]
                #print("Selected: name=%s" % (name))
            else:
                entry = combo.get_child()
                name = entry.get_text()
                #print("Entered: %s" % name)
        except:
            pass

        #print("Combo new selection / entry: '%s'" % name)

    def delall(self):
         # Delete previous contents
        try:
            while True:
                root = self.store.get_iter_first()
                if not root:
                    break
                try:
                    self.store.remove(root)
                except:
                    print("except: self.store remove")
        except:
            print("combo delall", sys.exc_info())
            pass

    # --------------------------------------------------------------------
    def  sel_text(self, txt):

        #print("Sel combo text")

        model = self.get_model()
        iter = model.get_iter_first()
        if iter:
            cnt = 0
            while True:

                #print("entry %d" % cnt, model[iter][0], txt)
                if  model[iter][0] == txt:
                    #print("Found %d" % cnt, model[iter][0])
                    self.set_active_iter(iter)
                    break

                iter = model.iter_next(iter)
                if not iter:
                    break
                cnt += 1

    def     sel_first(self):
        model = self.get_model()
        iter = model.get_iter_first()
        self.set_active_iter(iter)

# ------------------------------------------------------------------------
# Added convenience methods

class   xVBox(Gtk.VBox):

    def __init__(self, col = None):
        GObject.GObject.__init__(self)
        self.pad = 0
        if box_testmode:
            if not col:
                col = pgutils.randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))

    def set_padding(self, pad):
        self.pad = pad

    def pack(self, obj, expand = False, pad = 0):
        if pad == 0:
            pad = self.pad
        self.pack_start(obj, expand, expand, pad)

class   xHBox(Gtk.HBox):

    def __init__(self, col = None):
        GObject.GObject.__init__(self)
        self.pad = 0
        if box_testmode:
            if not col:
                col = pgutils.randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))

    def set_padding(self, pad):
        self.pad = pad

    def pack(self, obj, expand = False, pad = 0):
        if pad == 0:
            pad = self.pad
        self.pack_start(obj, expand, expand, pad)


# EOF


