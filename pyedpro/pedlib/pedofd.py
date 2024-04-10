#!/usr/bin/env python

# Action Handler for simple open file dialog

from __future__ import absolute_import
from __future__ import print_function

import time, os, re, string, warnings, platform, sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from pedlib import pedconfig

#sys.path.append('..')
#sys.path.append('..' + os.sep + "pycommon")

from pycommon.pggui import *

def ofd(fname = "", self2 = None):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog("pyedpro: Open File",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

    #dialog.set_transient_for(self2.mained.mywin)
    if self2:
        dialog.set_transient_for(self2.get_toplevel())
    #else:
    #    dialog.set_transient_for(None)

    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    #dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_size_request(800, 600)
    dialog.set_default_size(800, 600)
    #print dialog
    dialog.xmulti = []
    dialog.self2 = self2

    #dialog.set_transient_for(pyedlib.pedconfig.conf.pe.mywin);

    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)

    # Spacers
    label1  = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3  = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5  = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7  = Gtk.Label("   ");  label8 = Gtk.Label("   ")
    label9  = Gtk.Label("   ");
    label10 = Gtk.Label.new_with_mnemonic(" Open File by Name (click on 'Open _This' to open it) ");
    label11  = Gtk.Label("  ");  label12 = Gtk.Label(" ");
    #label13  = Gtk.Label("  ");  label14 = Gtk.Label(" ");

    dialog.label11 = Gtk.Label("   ")
    dialog.label12 = Gtk.Label("   ")

    dialog.pbox = Gtk.HBox()
    fill_path(dialog)

    dialog.vbox.pack_start(label4, 0, 0, 0)
    dialog.vbox.pack_start(dialog.pbox, 0, 0, 0)

    dialog.vbox.pack_start(xSpacer(), 0, 0, 0)
    dialog.vbox.pack_start(label10, 0, 0, 0)
    dialog.vbox.pack_start(xSpacer(), 0, 0, 0)

    warnings.simplefilter("ignore")
    dialog.entry = Gtk.Entry();
    warnings.simplefilter("default")

    dialog.entry.set_activates_default(True)
    dialog.entry.set_text(fname)

    ot =  Gtk.Button.new_with_mnemonic("Open thi_s")
    ot.connect("clicked", butt_this, dialog)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(dialog.entry, True, True, 0)
    hbox2.pack_start(label11, 0, 0, 0)
    hbox2.pack_start(ot, 0, 0, 0)
    hbox2.pack_start(label7, 0, 0, 0)

    dialog.vbox.pack_start(hbox2, 0, 0, 0)

    dialog.vbox.pack_start(xSpacer(), 0, 0, 0)
    label13 = Gtk.Label.new(" Dbl click to select one File/Dir, or Shift/Ctrl for multi select; then press Alt-O or click OK");
    dialog.vbox.pack_start(label13, 0, 0, 0)
    dialog.vbox.pack_start(xSpacer(), 0, 0, 0)

    dialog.ts = Gtk.ListStore(str, str, str, str)
    tview = create_ftree(dialog.ts)

    scroll = Gtk.ScrolledWindow()

    tview.connect("row-activated",  tree_sel, dialog)
    tview.connect("cursor-changed",  tree_sel_row, dialog)
    dialog.tview = tview

    scroll.add(tview)

    frame2 = Gtk.Frame(); frame2.add(scroll)

    hbox3 = Gtk.HBox()
    hbox3.pack_start(label1, 0, 0, 0)
    hbox3.pack_start(frame2, True, True, 0)
    hbox3.pack_start(label2, 0, 0, 0)

    dialog.vbox.pack_start(hbox3, True, True, 0)
    dialog.vbox.pack_start(label3, 0, 0, 0)

    dialog.show_all()
    populate(dialog)
    dialog.set_focus(tview)
    #dialog.set_focus(dialog.entry)
    warnings.simplefilter("default")

    response = dialog.run()

    res = []
    if response == Gtk.ResponseType.ACCEPT:
        xmodel = dialog.ts
        sel = tview.get_selection()
        # Is multi selection?
        iter = xmodel.get_iter_first()
        while True:
            #print("iterate", xmodel.get_value(iter, 0))
            if sel.iter_is_selected(iter):
                xstr = xmodel.get_value(iter, 0)
                xstr2 = os.path.realpath(xstr)
                res.append(xstr2)
            iter = xmodel.iter_next(iter)
            if not iter:
                break

    #print ("response", response, "result", res  )
    dialog.destroy()
    #del dialog
    return res

def butt_this(butt, dialog):
    ttt = dialog.entry.get_text()
    #print("butt_this", ttt)
    if ttt:
        # Expand user var
        ttt = os.path.expanduser(ttt)
        dialog.self2.mained.openfile(ttt)
        # Close like we have a file
        pedconfig.conf.pedwin.update_statusbar("Opened file: '%s'" % ttt);
        #dialog.destroy()
        #return [ttt,]
    else:
        pedconfig.conf.pedwin.update_statusbar("Please enter filename to open.");

def butt_click(butt, dialog):
    #print butt.path
    os.chdir(butt.path)
    populate(dialog)

def fill_path(dialog):

    cccc = dialog.pbox.get_children()
    for cc in cccc:
        dialog.pbox.remove(cc)

    cwd = os.getcwd();
    darr = cwd.split(os.sep)
    dialog.pbox.pack_start(dialog.label11, 0, 0, 0)

    if platform.system().find("Win") >= 0:
        curr = ""
    else:
        curr = os.sep

    for aa in darr:
        butt = Gtk.Button(label=aa)
        if platform.system().find("Win") >= 0:
            curr = curr + aa + os.sep
        else:
            curr = os.path.join(curr, aa)
        #print("path aa '%s' '%s'" % (aa, curr) )
        butt.path = curr
        butt.set_focus_on_click(False)
        butt.connect("clicked", butt_click, dialog)
        dialog.pbox.pack_start(butt, 0, 0, 2)

    dialog.pbox.pack_start(dialog.label12, 0, 0, 0)
    dialog.show_all()

# ------------------------------------------------------------------------

def populate(dialog):

    fill_path(dialog)

    # Clear old contents:
    while True:
        root = dialog.ts.get_iter_first()
        if not root:
            break
        try:
            dialog.ts.remove(root)
        except:
            print("Exception on rm ts", sys.exc_info())

    ppp = ".."
    filestat = os.stat(ppp)
    piter = dialog.ts.append(row=None)
    dialog.ts.set(piter, 0, str(ppp))
    dialog.ts.set(piter, 1, str(filestat.st_size))
    dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
    dialog.ts.set(piter, 3, str(time.ctime(filestat.st_mtime)))

    ddd2 = os.listdir(".")
    #ddd = sorted(ddd2)
    ddd2.sort()
    ddd = []

    # List ignored extensions here
    extno = [".pyc", ".o" ".lo", ".lst", ".png", ".jpg", ]

    for aa in ddd2:
        ext = os.path.splitext(aa)[1]
        flaf = 0
        # Ignore many ext
        for bb in extno:
            #print("bb", bb, ext)
            if ext == bb:
                flaf = 1
                break

        if not flaf:
            ddd.append(aa)

    for filename in ddd:
        if filename[0] == ".":
            continue
        if os.path.isdir(filename):
            try:
                filestat = os.stat(filename)
            except:
                pass
            piter = dialog.ts.append(row=None)
            #dialog.ts.set(piter, 0, "["+ filename + "]")
            #print filename,
            dialog.ts.set(piter, 0, filename )
            dialog.ts.set(piter, 1, str(filestat.st_size))
            dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
            dialog.ts.set(piter, 3, str(time.ctime(filestat.st_mtime)))

    for filename in ddd:
        if filename[0] == ".":
            continue
        if not os.path.isdir(filename):
            try:
                filestat = os.stat(filename)
            except:
                print("Cannot stat", filename)
                pass

            piter = dialog.ts.append(row=None)
            #print filename,
            dialog.ts.set(piter, 0, filename)
            dialog.ts.set(piter, 1, str(filestat.st_size))
            dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
            #dialog.ts.set(piter, 3, str(time.ctime(filestat.st_mtime)))
            dialog.ts.set(piter, 3, str(time.ctime(filestat.st_atime)))

    # --------------------------------------------------------------------

def compare(model, row1, row2, user_data):

    sort_column, _ = model.get_sort_column_id()
    value1 = model.get_value(row1, sort_column)
    value2 = model.get_value(row2, sort_column)
    #print(sort_column, value1, value2)
    if value1 < value2:
        return -1
    elif value1 == value2:
        return 0
    else:
        return 1

def ncompare(model, row1, row2, user_data):
    sort_column, _ = model.get_sort_column_id()
    value1 = model.get_value(row1, sort_column)
    value2 = model.get_value(row2, sort_column)
    #print("n", sort_column, value1, value2, type(value1))
    if int(value1) < int(value2):
        return -1
    elif int(value1) == int(value2):
        return 0
    else:
        return 1

def create_ftree(ts, text = None):

    # create the tview using ts
    tv = Gtk.TreeView(model=ts)

    tv.set_search_column(0)
    tv.set_headers_clickable(True)
    #tv.set_enable_search(True)
    ts.set_sort_func(0, compare, None)
    ts.set_sort_func(1, ncompare, None)

    # create a CellRendererText to render the data
    cell = Gtk.CellRendererText()

    tvcolumn = Gtk.TreeViewColumn('File')
    tvcolumn.set_min_width(240)
    tvcolumn.pack_start(cell, True)
    tvcolumn.add_attribute(cell, 'text', 0)
    tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
    tvcolumn.set_sort_column_id(0)
    tv.append_column(tvcolumn)

    cell2 = Gtk.CellRendererText()
    tvcolumn2 = Gtk.TreeViewColumn('Size')
    tvcolumn2.set_min_width(100)
    tvcolumn2.set_sort_column_id(1)
    tvcolumn2.pack_start(cell2, True)
    tvcolumn2.add_attribute(cell2, 'text', 1)
    tv.append_column(tvcolumn2)

    cell3 = Gtk.CellRendererText()
    tvcolumn3 = Gtk.TreeViewColumn('Perm')
    tvcolumn3.set_min_width(120)
    tvcolumn3.pack_start(cell3, True)
    tvcolumn3.add_attribute(cell3, 'text', 2)
    tv.append_column(tvcolumn3)

    cell4 = Gtk.CellRendererText()
    tvcolumn4 = Gtk.TreeViewColumn('Modified')
    tvcolumn4.set_min_width(150)
    tvcolumn4.pack_start(cell4, True)
    tvcolumn4.set_sort_column_id(3)
    tvcolumn4.add_attribute(cell4, 'text', 3)
    tv.append_column(tvcolumn4)

    tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    return tv

    #sel.get_selected()

def tree_sel_row(xtree, dialog):

    #print("tree_sel_row", xtree)
    sel = xtree.get_selection()
    xmodel, xpath = sel.get_selected_rows()
    if sel:
        try:
            xiter2 = xmodel.get_iter(xpath)
            xstr = xmodel.get_value(xiter2, 0)
            dialog.entry.set_text(xstr)
        except:
            pass
            #print("sel row", sys.exc_info())
    else:
        dialog.entry.set_text("")

def tree_sel(xtree, xiter, xpath, dialog):

    #print ("tree_sel", xtree, xiter, xpath)
    sel = xtree.get_selection()
    xmodel, xpath = sel.get_selected_rows()
    if xpath:
        for aa in xpath:
            xiter2 = xmodel.get_iter(aa)
            xstr = xmodel.get_value(xiter2, 0)
            #print("mul selstr: ", "'" + xstr + "'" )
            if click_dir_action(xstr):
                dialog.xmulti = []
                populate(dialog)
                return
        dialog.response(Gtk.ResponseType.ACCEPT)

# If directory, change to it
def click_dir_action(xstr):
    if xstr[0] == "[":
         xstr = xstr[1:len(xstr)-1]
    if os.path.isdir(xstr):
        #print ("dir", xstr)
        os.chdir(xstr)
        return True

# Call key handler
def area_key(area, event, self):

    #print "area_key", event
    # Do key down:
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            return
            #area.destroy()

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Return:
            #print "Ret"
            return
            #area.destroy()

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_BackSpace:
            os.chdir("..")
            populate(self)
            #print "BS"

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            self.alt = True;

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if self.alt:
                area.destroy()

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            self.alt = False;

    return None

# ------------------------------------------------------------------------
def mode2str(mode):

    #print mode, oct(mode), hex(mode)

    dstr = " "
    if mode & 0x4000:
        dstr = "d"

    estr = ""
    for aa in range(3):
        xstr = ""
        if mode & 0x4: xstr += "r"
        else:        xstr += "-"
        if mode & 0x2: xstr += "w"
        else:        xstr += "-"
        if mode & 0x1: xstr += "x"
        else:        xstr += "-"
        mode = mode >> 3
        estr = xstr + estr  # Reverse

    estr = dstr + estr
    return estr

# eof
