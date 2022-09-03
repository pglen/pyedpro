#!/usr/bin/env python

# Ped font selection

from __future__ import absolute_import
from __future__ import print_function

import  signal, os, time, sys, subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from pedlib import pedconfig
from pedlib.pedutil import *

# I had to do this, as the standard font dialog does not have a mono filter.
# Also, we do not need mono italic etc so the dialog is simpler.
# Plus, the mono fonts are marked incorrectly, this way we can filter them.
# Oh yeah, live feedback ...

def selfont(self, self2):

    head = "pyedpro: Set Editor Main Font"

    dialog = Gtk.Dialog(head,
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)

    try:
        dialog.set_icon_from_file(get_img_path("spyedpro_sub.png"))
    except:
        print("Cannot set icon in", __file__)

    self.dialog = dialog

    dialog.myfd = self2.pangolayout.get_font_description()
    myfam = dialog.myfd.get_family()
    mysiz = dialog.myfd.get_size() / Pango.SCALE

    dialog.lastfam = myfam
    dialog.lastsiz = mysiz

    xx, yy = self2.mained.mywin.get_size()
    #dialog.set_default_size(3*xx/4, yy/2)

    # Spacers
    label1 = Gtk.Label("  ");
    label2a = Gtk.Label("  ");  label2 = Gtk.Label("  ")
    label3 = Gtk.Label("  ");
    label3a = Gtk.Label("  ");
    label4 = Gtk.Label("  ")

    dialog.testlab = Gtk.Label("The test line.\nMulti line text.")
    dialog.testlab.modify_font(dialog.myfd)
    dialog.testlab.set_size_request(200, yy/3)

    dialog.tree = create_tree(self)
    dialog.tree.set_headers_visible(False)
    #dialog.tree.set_size_request(200, -1)

    dialog.tree.connect("cursor-changed",  tree_sel_row, dialog, self2)
    dialog.tree.connect("key-press-event", area_key, dialog)
    dialog.tree.connect("key-release-event", area_key, dialog)

    stree = Gtk.ScrolledWindow()
    stree.add(dialog.tree)
    stree.set_size_request(150, -1)

    hbox = Gtk.HBox()
    hbox.pack_start(label2a, False, False,0)
    hbox.pack_start(stree, True, True,0)
    hbox.pack_start(label2, False ,0, 0)

    vbox = Gtk.VBox()

    #dialog.tree2 = create_tree(self)
    #dialog.tree2.set_headers_visible(False)
    #dialog.tree2.set_size_request(200, 80)
    #dialog.tree2.connect("cursor-changed",  tree_sel_row2, dialog)

    vbox.pack_start(label1, False, 0 ,0 )
    frame = Gtk.Frame()
    frame.add(dialog.testlab)
    vbox.pack_start(frame, True, 0, 0)
    vbox.pack_start(label3, False, 0, 0 )

    hbox.pack_start(vbox, True,  0, 0)
    hbox.pack_start(label4, False, 0, 0 )

    dialog.tree3 = create_tree(self)
    dialog.tree3.set_headers_visible(False)
    dialog.tree3.set_size_request(180, yy/3)

    dialog.tree3.connect("cursor-changed",  tree_sel_row3, dialog, self2)
    dialog.tree3.connect("key-press-event", area_key, dialog)
    dialog.tree3.connect("key-release-event", area_key, dialog)

    stree3 = Gtk.ScrolledWindow()
    stree3.add(dialog.tree3)
    stree3.set_size_request(80, -1)

    sizes = []; add_sizes(sizes)
    update_treestore2(None, dialog.tree3, sizes, mysiz)

    hbox.pack_start(stree3, True, True, 0)
    hbox.pack_start(label3a, False, 0, 0 )

    vlab1 = Gtk.Label() ;    vlab2 = Gtk.Label()
    vbox2 = Gtk.VBox()

    vbox2.add(vlab1)
    vbox2.add(hbox)
    vbox2.add(vlab2)

    dialog.vbox.add(vbox2)
    dialog.show_all()

    pg = Gtk.Widget.create_pango_context(self.mywin)
    fd = pg.get_font_description()

    fonts = pg.list_families();
    dialog.monos = []
    for aa in fonts:
        if aa.is_monospace():
            # Some fonts are marked mono, they are not
            if aa.get_name() == "Cursor":
                continue
            if aa.get_name() == "CM Typewriter Greek":
                continue
            dialog.monos.append(aa)

    dialog.fonts2 = []
    curr = 0; cnt = 0
    for cc in dialog.monos:
        nnn = cc.get_name()
        # This will match more than one, we accept the last match
        if nnn.upper().find(myfam.upper()) >= 0:
            curr = cnt
        dialog.fonts2.append(nnn)
        cnt += 1
    update_treestore(None, dialog.tree, dialog.fonts2, curr)

    result = dialog.run()
    dialog.destroy()
    if result == Gtk.ResponseType.ACCEPT:
        #print result, dialog.lastfam, dialog.lastsiz
        for mm in range(self2.notebook.get_n_pages()):
            vcurr = self2.notebook.get_nth_page(mm)
            vcurr.area.setfont(dialog.lastfam, dialog.lastsiz)

        pedconfig.conf.sql.put("fsize", dialog.lastsiz)
        pedconfig.conf.sql.put("fname", dialog.lastfam)
    else:
        # Restore
        self2.setfont(myfam, mysiz)
        self2.invalidate()


def tree_sel_row(xtree, dialog, self2):

    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    xstr = xmodel.get_value(xiter, 0)
    dialog.lastfam = xstr
    dialog.myfd.set_family(xstr);
    dialog.myfd.set_size(dialog.lastsiz * Pango.SCALE)
    dialog.testlab.modify_font(dialog.myfd)

    self2.setfont(dialog.lastfam, dialog.lastsiz)
    self2.invalidate()

def tree_sel_row3(xtree, dialog, self2):

    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    xstr = xmodel.get_value(xiter, 0)
    #print "tree_sel_row3", xstr
    dialog.lastsiz = int(xstr)
    dialog.myfd.set_family(dialog.lastfam);
    dialog.myfd.set_size(dialog.lastsiz * Pango.SCALE)
    dialog.testlab.modify_font(dialog.myfd)

    self2.setfont(dialog.lastfam, dialog.lastsiz)
    self2.invalidate()


# -------------------------------------------------------------------------
def create_tree(self):

    # create the TreeView using treestore
    treestore = Gtk.TreeStore(str)
    tv = Gtk.TreeView(treestore)
    tv.set_enable_search(True)

    # create a CellRendererText to render the data
    cell = Gtk.CellRendererText()

    # create the TreeViewColumn to display the data
    tvcolumn = Gtk.TreeViewColumn()

    # add the cell to the tvcolumn and allow it to expand
    tvcolumn.pack_start(cell, True)

    # set the cell "text" attribute to column 0 - retrieve text
    # from that column in treestore
    tvcolumn.add_attribute(cell, 'text', 0)

    # add tvcolumn to treeview
    tv.append_column(tvcolumn)

    return tv

def update_treestore(self, tree, text, was):

    #print "was", was

    treestore = tree.get_model()

    # Delete previous contents
    try:
        while True:
            root = treestore.get_iter_first()
            treestore.remove(root)
    except:
        pass
        #print  sys.exc_info()
    if not text:
        treestore.append(None, ["No Fonts",])
        return

    cnt = 0; piter2 = None; next = False
    try:
        for line in text:
            piter = treestore.append(None, [cut_lead_space(line)])
            if cnt == was:
                piter2 = piter
            cnt += 1
    except:
        pass
        #print  sys.exc_info()

    if piter2:
        tree.set_cursor(treestore.get_path(piter2))
    else:
        root = treestore.get_iter_first()
        tree.set_cursor(treestore.get_path(root))

def update_treestore2(self, tree, text, was):

    #print "was", was

    treestore = tree.get_model()

    # Delete previous contents
    try:
        while True:
            root = treestore.get_iter_first()
            treestore.remove(root)
    except:
        pass
        #print  sys.exc_info()
    if not text:
        treestore.append(None, ["No Fonts",])
        return

    cnt = 0; piter2 = None; next = False
    try:
        for line in text:
            piter = treestore.append(None, [cut_lead_space(line)])
            if int(line) == was:
                piter2 = piter
            cnt += 1
    except:
        pass
        #print  sys.exc_info()

    if piter2:
        tree.set_cursor(treestore.get_path(piter2))
    else:
        root = treestore.get_iter_first()
        tree.set_cursor(treestore.get_path(root))


def add_sizes(sizes):

    for num in range(6, 18, 1):     sizes.append(str(num))
    for num in range(18, 32, 2):    sizes.append(str(num))
    for num in range(32, 64, 4):    sizes.append(str(num))
    for num in range(64, 96+1, 8):  sizes.append(str(num))

# ------------------------------------------------------------------------

def area_key(area, event, dialog):

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            dialog.response(Gtk.ResponseType.REJECT)

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Return:
            #print "Ret"
            dialog.response(Gtk.ResponseType.ACCEPT)

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            area.alt = True;

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if area.alt:
                dialog.response(Gtk.ResponseType.REJECT)

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            area.alt = False;










