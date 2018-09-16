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

def colors(self, self2):

    head = "pyedit: colors"
    
    dialog = gtk.Dialog(head,
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(gtk.RESPONSE_ACCEPT)
    dialog.set_icon_from_file(get_img_path("pyedit_sub.png"))
    self.dialog = dialog
    
    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)
    
    #xx, yy = self2.mained.window.get_size()
    #dialog.set_default_size(3*xx/4, yy/2)

    vbox = gtk.VBox()
    lab3 = gtk.Label("       ")
    vbox.pack_start(lab3, False )
    
    hbox1 = col_line(" _Font color ", self2.fgcolor, col_one, self2)
    vbox.pack_start(hbox1, False )

    hbox2 = col_line(" _Selection Color ", self2.rbgcolor, col_two, self2)
    vbox.pack_start(hbox2, False )
    
    hbox2 = col_line(" Col_umn Sel. Color ", self2.cbgcolor, col_three,  self2)
    vbox.pack_start(hbox2, False )
    
    hbox2 = col_line("_Keyword Color ", self2.kwcolor,  col_four, self2)
    vbox.pack_start(hbox2, False )
  
    hbox2 = col_line("C_lass Color ", self2.clcolor,  col_five, self2)
    vbox.pack_start(hbox2, False )
            
    hbox2 = col_line("Co_mment Color ", self2.cocolor,  col_six, self2)
    vbox.pack_start(hbox2, False )
    
    hbox2 = col_line("S_tring Color ", self2.stcolor,  col_seven, self2)
    vbox.pack_start(hbox2, False )
    
    buttd = gtk.Button(" _Restore Defaults ")
    buttd.connect("clicked", def_col, self2)
    
    lab4 = gtk.Label("       ")
    vbox.pack_start(lab4, False )
    
    vbox.pack_start(buttd, False )
    
    lab5 = gtk.Label("       ")
    vbox.pack_start(lab5, False )
            
    dialog.vbox.add(vbox)
    dialog.show_all()
    response = dialog.run()   

    dialog.destroy()
                      
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

def   colbox(col):

    lab1 = gtk.Label("        ")
    eventbox = gtk.EventBox()
    frame = gtk.Frame()
    frame.add(lab1)
    eventbox.add(frame)
    eventbox.color =  col  # gtk.gdk.Color(col)
    eventbox.modify_bg(gtk.STATE_NORMAL, eventbox.color)
    return eventbox
    
def col_line(tit, col, callb, self2):

    butt1 = gtk.Button(tit)
    ev1 = colbox(col)
    tit = tit.replace("_", "")
    tit = tit.strip().rstrip()
    
    butt1.connect("clicked", callb, "Choose " + tit, ev1, self2)

    hbox = gtk.HBox()
    lab1 = gtk.Label("   ");  lab2 = gtk.Label("   ")
    
    hbox.pack_start(lab1, False )
    hbox.pack_start(ev1, False )
    hbox.pack_start(lab2, False )
    
    hbox.pack_start(butt1, False )
    
    return hbox

def colsel(ev, title):

    csd = gtk.ColorSelectionDialog(title)
    col = csd.get_color_selection()
    col.set_current_color(ev.color)    
    response = csd.run()
    
    if response == gtk.RESPONSE_OK:   
        ev.color = col.get_current_color()
        ev.modify_bg(gtk.STATE_NORMAL, ev.color)
    csd.destroy()
        
def col_one(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.fgcolor = ev.color
    pedconfig.conf.sql.put("fgcolor", self2.fgcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()
    
                                    
def col_two(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.rbgcolor = ev.color
    pedconfig.conf.sql.put("rbgcolor", self2.rbgcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()
    
def col_three(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.cbgcolor = ev.color
    pedconfig.conf.sql.put("cbgcolor", self2.cbgcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()

def col_four(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.kwcolor = ev.color
    pedconfig.conf.sql.put("kwcolor", self2.kwcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()
    
def col_five(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.clcolor = ev.color
    pedconfig.conf.sql.put("clcolor", self2.clcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()

def col_six(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.cocolor = ev.color
    pedconfig.conf.sql.put("cocolor", self2.cocolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()

def col_seven(butt, title, ev, self2):
    
    colsel(ev, title)
    self2.stcolor = ev.color
    pedconfig.conf.sql.put("stcolor", self2.stcolor.to_string())        
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    self2.invalidate()

def  def_col(butt, self2):

    self2.fgcolor  = self2.colormap.alloc_color(peddoc.FGCOLOR)              
    self2.rbgcolor = self2.colormap.alloc_color(peddoc.RBGCOLOR)              
    self2.cbgcolor = self2.colormap.alloc_color(peddoc.CBGCOLOR)              
    self2.kwcolor  = self2.colormap.alloc_color(peddoc.KWCOLOR)
    self2.clcolor  = self2.colormap.alloc_color(peddoc.CLCOLOR)
    self2.cocolor  = self2.colormap.alloc_color(peddoc.COCOLOR)
    self2.stcolor  = self2.colormap.alloc_color(peddoc.STCOLOR)
    self2.invalidate()

    pedconfig.conf.sql.put("fgcolor", self2.fgcolor.to_string())        
    pedconfig.conf.sql.put("rbgcolor", self2.rbgcolor.to_string())        
    pedconfig.conf.sql.put("cbgcolor", self2.cbgcolor.to_string())        
    pedconfig.conf.sql.put("kwcolor", self2.kwcolor.to_string())        
    pedconfig.conf.sql.put("clcolor", self2.clcolor.to_string())        
    pedconfig.conf.sql.put("cocolor", self2.cocolor.to_string())        
    pedconfig.conf.sql.put("stcolor", self2.stcolor.to_string())        

    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()




