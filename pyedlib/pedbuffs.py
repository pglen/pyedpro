#!/usr/bin/env python

# Action Handler for buffers

import re, string

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

import peddoc, pedync, pedconfig
from pedutil import *

# -------------------------------------------------------------------------

def buffers(self, self2):

    head = "pyedit: buffers"
    
    dialog = gtk.Dialog(head,
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(gtk.RESPONSE_ACCEPT)
    dialog.set_icon_from_file(get_img_path("pyedit_sub.png"))
    dialog.set_position(gtk.WIN_POS_CENTER)
    self.dialog = dialog
 
    xx, yy = self2.mained.window.get_size()

    dialog.set_default_size(3*xx/4, yy/2)

    dialog.treestore = None
    dialog.tree = create_tree(self, dialog)
    dialog.tree.set_headers_visible(False)

    dialog.tree.connect("cursor-changed",  tree_sel_row, dialog, self2)
    dialog.tree.connect("key-press-event", area_key, dialog)
    dialog.tree.connect("key-release-event", area_key, dialog)
   
    stree = gtk.ScrolledWindow()
    stree.add(dialog.tree)
    frame = gtk.Frame()
    frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    
    frame.add(stree)
    
    #dialog.vbox.set_spacing(8)
    
    dialog.vbox.pack_start(frame)
    
    blist = []; was = -1
    nn2 = self2.notebook.get_current_page()
    vcurr2 = self2.notebook.get_nth_page(nn2)
    cc = self2.notebook.get_n_pages()
    for mm in range(cc):
        vcurr = self2.notebook.get_nth_page(mm)
        if was == -1 and vcurr == vcurr2:
            was = mm
        blist.append(vcurr.area.fname)
            
    update_treestore(dialog, dialog, blist, was)
                                                   
    dialog.show_all()
    response = dialog.run()
    dialog.destroy()

    if response != gtk.RESPONSE_ACCEPT:   
        return
        
    cc = self2.notebook.get_n_pages()
    if cc == 0:
        return
    for mm in range(cc):
        vcurr = self2.notebook.get_nth_page(mm)
        if vcurr.area.fname == dialog.res:
            self2.notebook.set_current_page(mm)                        
            nn2 = self2.notebook.get_current_page()
            vcurr2 = self2.notebook.get_nth_page(nn2)
            self2.mained.window.set_focus(vcurr2.vbox.area)                   
            self2.mained.window.show_all()               
            break
                           
# ------------------------------------------------------------------------

def area_key(area, event, dialog):

    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Escape:
            #print "Esc"
            dialog.response(gtk.RESPONSE_REJECT)

    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Return:
            #print "Ret"
            dialog.response(gtk.RESPONSE_ACCEPT)

        if event.keyval == gtk.keysyms.Alt_L or \
                event.keyval == gtk.keysyms.Alt_R:
            area.alt = True;
            
        if event.keyval == gtk.keysyms.x or \
                event.keyval == gtk.keysyms.X:
            if area.alt:
                dialog.response(gtk.RESPONSE_REJECT)
                              
    elif  event.type == gtk.gdk.KEY_RELEASE:
        if event.keyval == gtk.keysyms.Alt_L or \
              event.keyval == gtk.keysyms.Alt_R:
            area.alt = False;

# ------------------------------------------------------------------------

def tree_sel_row(xtree, dialog, self2):

    sel = xtree.get_selection()    
    xmodel, xiter = sel.get_selected_rows()
    # In muti selection, only process first
    for aa in xiter:
        xstr = xmodel.get_value(xmodel.get_iter(aa), 0)    
        #print "Selected:", xstr
        dialog.res = xstr
        break

# Tree handlers
def start_tree(self, win2):

    if not win2.treestore:
        win2.treestore = gtk.TreeStore(str)
    
    # Delete previous contents
    try:      
        while True:
            root = win2.treestore.get_iter_first() 
            win2.treestore.remove(root)                           
    except:
        #print  sys.exc_info()
        pass
    
    piter = win2.treestore.append(None, ["Searching .."])
    win2.treestore.append(piter, ["None .."])
    
# -------------------------------------------------------------------------
def create_tree(self, win2, match = False, text = None):
    
    start_tree(self, win2)
    
    # create the TreeView using treestore
    tv = gtk.TreeView(win2.treestore)
    tv.set_enable_search(True)

    # create a CellRendererText to render the data
    cell = gtk.CellRendererText()

    # create the TreeViewColumn to display the data
    #tvcolumn = gtk.TreeViewColumn("Matches for '" + match + "'")
    tvcolumn = gtk.TreeViewColumn()

    # add the cell to the tvcolumn and allow it to expand
    tvcolumn.pack_start(cell, True)

    # set the cell "text" attribute to column 0 - retrieve text
    # from that column in treestore
    tvcolumn.add_attribute(cell, 'text', 0)
    
    # add tvcolumn to treeview
    tv.append_column(tvcolumn)

    return tv

def update_treestore(self, win2, text, was):
    
    #print "was", was
    
    # Delete previous contents
    try:      
        while True:
            root = win2.treestore.get_iter_first() 
            win2.treestore.remove(root)                           
    except:
        pass
        #print  sys.exc_info()        
    if not text:
        win2.treestore.append(None, ["No Match",])
        return

    cnt = 0; piter2 = None; next = False
    try:
        for line in text:
            piter = win2.treestore.append(None, [cut_lead_space(line)])
            if next:
                next = False; piter2 = piter               
            if cnt == was - 1:
                next = True
            cnt += 1
    except:
        pass
        #print  sys.exc_info()

    if piter2:
        win2.tree.set_cursor(win2.treestore.get_path(piter2))
    else:
        root = win2.treestore.get_iter_first() 
        win2.tree.set_cursor(win2.treestore.get_path(root))
















































