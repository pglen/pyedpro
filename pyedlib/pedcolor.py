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

    print "fgcolor", rgb2str(col2rgb(self2.fgcolor))
    print "rbgcolor", rgb2str(col2rgb(self2.rbgcolor))
    print "cbgcolor", rgb2str(col2rgb(self2.cbgcolor))
    
    dialog = Gtk.Dialog(head,
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.window)
    
    dialog.set_icon_from_file(get_img_path("pyedit_sub.png"))
    self.dialog = dialog
    
    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)
    
    #xx, yy = self2.mained.window.get_size()
    #dialog.set_default_size(3*xx/4, yy/2)

    vbox = Gtk.VBox()
    lab3 = Gtk.Label("       ")
    vbox.pack_start(lab3, False, 0, 0 )
    
    hbox1 = col_line(" _Font color ", self2.fgcolor, col_one, self2)
    vbox.pack_start(hbox1, False, 0, 0 )

    hbox2 = col_line(" _Selection Color ", self2.rbgcolor, col_two, self2)
    vbox.pack_start(hbox2, False, 0, 0 )
    
    hbox2 = col_line(" Col_umn Sel. Color ", self2.cbgcolor, col_three,  self2)
    vbox.pack_start(hbox2, False, 0, 0 )
    
    hbox2 = col_line("_Keyword Color ", self2.kwcolor,  col_four, self2)
    vbox.pack_start(hbox2, False, 0, 0 )
  
    hbox2 = col_line("C_lass Color ", self2.clcolor,  col_five, self2)
    vbox.pack_start(hbox2, False, 0, 0 )
            
    hbox2 = col_line("Co_mment Color ", self2.cocolor,  col_six, self2)
    vbox.pack_start(hbox2, False, 0, 0 )
    
    hbox2 = col_line("S_tring Color ", self2.stcolor,  col_seven, self2)
    vbox.pack_start(hbox2, False, 0, 0 )
    
    buttd = Gtk.Button(" _Restore Defaults ")
    buttd.connect("clicked", def_col, self2)
    
    lab4 = Gtk.Label("       ")
    vbox.pack_start(lab4, False , 0, 0)
    
    vbox.pack_start(buttd, False, 0, 0 )
    
    lab5 = Gtk.Label("       ")
    vbox.pack_start(lab5, False , 0, 0)
            
    dialog.vbox.add(vbox)
    dialog.show_all()
    response = dialog.run()   

    dialog.destroy()
                      
# ------------------------------------------------------------------------
# Conversion routines:
                      
def col2rgb(col):

    aa = min(col[0], 1.)
    bb = min(col[1], 1.)
    cc = min(col[2], 1.) 
            
    return Gdk.Color.from_floats(aa, bb, cc)

def rgb2str(icol):
    strx = "#%02x%02x%02x" % (icol.red & 0xff,  \
                        icol.green & 0xff, icol.blue & 0xff)
    return strx
    
def convcolor( col):
    return ( float(int(col[1:3], base=16)) / 256, 
                    float(int(col[3:5], base=16)) / 256, \
                        float(int(col[5:7], base=16)) / 256 )

def rgb2col(icol):
        #print "rgb2col", icol
        col = [0, 0, 0]
        col[0] = float(icol.red) / 256
        col[1] = float(icol.green) / 256
        col[2] = float(icol.blue) / 256
        return col
                                                                                                                                                                                                       
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

# ------------------------------------------------------------------------

def   colbox(col):

    lab1 = Gtk.Label("        ")
    eventbox = Gtk.EventBox()
    frame = Gtk.Frame()
    frame.add(lab1)
    eventbox.add(frame)
    eventbox.color =  col  # Gtk.gdk.Color(col)
    eventbox.modify_bg(Gtk.StateFlags.NORMAL, col2rgb(eventbox.color))
    return eventbox
    
def col_line(tit, col, callb, self2):

    butt1 = Gtk.Button(tit)
    ev1 = colbox(col)
    tit = tit.replace("_", "")
    tit = tit.strip().rstrip()
    
    butt1.connect("clicked", callb, "Choose " + tit, ev1, self2)

    hbox = Gtk.HBox()
    lab1 = Gtk.Label("   ");  lab2 = Gtk.Label("   ")
    
    hbox.pack_start(lab1, False , 0, 0)
    hbox.pack_start(ev1, False , 0, 0)
    hbox.pack_start(lab2, False , 0, 0)
    
    hbox.pack_start(butt1, False, 0, 0 )
    
    return hbox

def colsel(ev, title):

    csd = Gtk.ColorSelectionDialog(title)
    col = csd.get_color_selection()
    col.set_current_color(col2rgb(ev.color))    
    response = csd.run()
    
    if response == Gtk.ResponseType.OK:   
        ev.color = col.get_current_color()
        ev.modify_bg(Gtk.StateFlags.NORMAL, ev.color)
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

    self2.fgcolor  = convcolor(peddoc.FGCOLOR)              
    self2.rbgcolor = convcolor(peddoc.RBGCOLOR)              
    self2.cbgcolor = convcolor(peddoc.CBGCOLOR)              
    self2.kwcolor  = convcolor(peddoc.KWCOLOR)
    self2.clcolor  = convcolor(peddoc.CLCOLOR)
    self2.cocolor  = convcolor(peddoc.COCOLOR)
    self2.stcolor  = convcolor(peddoc.STCOLOR)
    
    self2.invalidate()
    
    '''pedconfig.conf.sql.put("fgcolor",  rgb2str(col2rgb(self2.fgcolor)) )       
    pedconfig.conf.sql.put("rbgcolor", rgb2str(col2rgb(self2.rbgcolor)))
    pedconfig.conf.sql.put("cbgcolor", rgb2str(col2rgb(self2.cbgcolor)))
    pedconfig.conf.sql.put("kwcolor",  rgb2str(col2rgb(self2.kwcolor)) )
    pedconfig.conf.sql.put("clcolor",  rgb2str(col2rgb(self2.clcolor)) )
    pedconfig.conf.sql.put("cocolor",  rgb2str(col2rgb(self2.cocolor)) )
    pedconfig.conf.sql.put("stcolor",  rgb2str(col2rgb(self2.stcolor)) )
    '''
    
    for mm in range(self2.notebook.get_n_pages()):
        vcurr = self2.notebook.get_nth_page(mm)
        vcurr.area.setcol()
    
# EOF
