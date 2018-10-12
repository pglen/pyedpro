#!/usr/bin/env python

# Action Handler for find

from __future__ import absolute_import
from __future__ import print_function
import time, os, re, string, warnings

import pyedlib.pedconfig

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

def ofd(fname = None, self2 = None):

    dialog = Gtk.Dialog("pyedpo: Open File",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
                    
    dialog.set_transient_for(self2.mained.mywin)
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    #dialog.set_size_request(800, 600)
    dialog.set_default_size(800, 600)
    #print dialog

    #dialog.set_transient_for(pyedlib.pedconfig.conf.pe.mywin);
            
    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)

    # Spacers
    label1  = Gtk.Label("   ");  label2 = Gtk.Label("   ") 
    label3  = Gtk.Label("   ");  label4 = Gtk.Label("   ") 
    label5  = Gtk.Label("   ");  label6 = Gtk.Label("   ") 
    label7  = Gtk.Label("   ");  label8 = Gtk.Label("   ") 
    label10 = Gtk.Label("   ");  
    
    dialog.label11 = Gtk.Label("   ") 
    dialog.label12 = Gtk.Label("   ") 

    dialog.pbox = Gtk.HBox()
    fill_path(dialog)
   
    dialog.vbox.pack_start(label4, 0, 0, 0)
    dialog.vbox.pack_start(dialog.pbox, 0, 0, 0)
    dialog.vbox.pack_start(label10, 0, 0, 0)
    
    warnings.simplefilter("ignore")
    dialog.entry = Gtk.Entry(); 
    warnings.simplefilter("default")
    
    dialog.entry.set_activates_default(True)
    dialog.entry.set_text(fname)
    
    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(dialog.entry, True, True, 0)
    hbox2.pack_start(label7, 0, 0, 0)
  
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.vbox.pack_start(label8, 0, 0, 0)

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
    
    response = dialog.run()   
    
    if response == Gtk.ResponseType.ACCEPT:
        res = os.path.realpath(dialog.entry.get_text())
    else:
        res = ""        
    #print "response", response, "res", res    
    dialog.destroy()
    
    return res
 
def butt_click(butt, dialog):
    #print butt.path
    os.chdir(butt.path)
    populate(dialog)
      
def fill_path(dialog):

    cccc = dialog.pbox.get_children()
    for cc in cccc:
        dialog.pbox.remove(cc)
            
    cwd = os.getcwd(); 
    # Hack to detect windows:
    #if cwd[1] == ":":
    #    darr = cwd.split("\\")    
    #else:                   
    darr = cwd.split("/")
            
    dialog.pbox.pack_start(dialog.label11, 0, 0, 0)
    curr = ""
    for aa in darr:
        #butt = Gtk.Button(aa + "/")
        butt = Gtk.Button(label=aa)
        
        curr += aa + "/"; butt.path = curr
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
            print("Exception on rm ts")

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
    
    for aa in ddd2:
        if os.path.splitext(aa)[1] != ".pyc":
            ddd.append(aa)                                    
          
    for filename in ddd:
        if filename[0] == ".":
            continue
        if os.path.isdir(filename):
            filestat = os.stat(filename)
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
            filestat = os.stat(filename)
            piter = dialog.ts.append(row=None)      
            #print filename,
            dialog.ts.set(piter, 0, filename)
            dialog.ts.set(piter, 1, str(filestat.st_size))
            dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
            dialog.ts.set(piter, 3, str(time.ctime(filestat.st_mtime)))
    
    # --------------------------------------------------------------------
    
def create_ftree(ts, text = None):
        
    warnings.simplefilter("ignore")
    # create the tview using ts
    tv = Gtk.TreeView(ts)
    warnings.simplefilter("default")

    # create a CellRendererText to render the data
    cell = Gtk.CellRendererText()
    
    tvcolumn = Gtk.TreeViewColumn('File')
    tvcolumn.set_min_width(240)
    tvcolumn.pack_start(cell, True)
    tvcolumn.add_attribute(cell, 'text', 0)
    tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
    tv.append_column(tvcolumn)

    cell2 = Gtk.CellRendererText()
    tvcolumn2 = Gtk.TreeViewColumn('Size')
    tvcolumn2.set_min_width(100)
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
    tvcolumn4.add_attribute(cell4, 'text', 3)
    tv.append_column(tvcolumn4)

    return tv

def tree_sel_row(xtree, dialog):
    #print "tree_sel_row", xtree
    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    if(xiter):
        xstr = xmodel.get_value(xiter, 0)        
    else:
        xstr = ""
    #xstr2 = xmodel.get_value(xiter, 1)        
    #xstr3 = xmodel.get_value(xiter, 2)        
    #print xstr, xstr2, xstr3
        
    if os.path.isdir(xstr):
        dialog.entry.set_text("")
    else:
         dialog.entry.set_text(xstr)        
    
def tree_sel(xtree, xiter, xpath, dialog):
    #print "tree_sel", xtree, xiter, xpath
    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    xstr = xmodel.get_value(xiter, 0)        
    
    #xstr2 = xmodel.get_value(xiter, 1)        
    #xstr3 = xmodel.get_value(xiter, 2)        
    #print xstr, xstr2, xstr3
        
    if xstr[0] == "[":
         xstr = xstr[1:len(xstr)-1]    
    if os.path.isdir(xstr):
        #print "dir", xstr
        os.chdir(xstr)
        populate(dialog)
    else:
        dialog.entry.set_text(xstr)        
        dialog.response(Gtk.ResponseType.ACCEPT)

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





















