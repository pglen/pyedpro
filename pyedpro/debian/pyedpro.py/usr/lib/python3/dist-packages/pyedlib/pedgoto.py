#!/usr/bin/env python

# Action Handler for goto

from __future__ import absolute_import
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
      
import warnings
from . import  pedconfig

def gotodlg(self2):

    warnings.simplefilter("ignore")
    
    dialog = Gtk.Dialog("pyedpro: Goto Line",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)
    
    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ") 
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ") 
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ") 
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ") 

    #warnings.simplefilter("ignore")
    entry = Gtk.Entry(); 
    #warnings.simplefilter("default")

    entry.set_activates_default(True)

    if  self2.oldgoto == "":
        self2.oldgoto = pedconfig.conf.sql.get_str("goto")                               
        if  self2.oldgoto == None:
            self2.oldgoto = ""

    entry.set_text(self2.oldgoto)
    entry.set_width_chars(24)
    dialog.vbox.pack_start(label4, 0, 0, 0)  

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)  
    hbox2.pack_start(entry, 0, 0, 0)  
    hbox2.pack_start(label7, 0, 0, 0)  
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.vbox.pack_start(label5, 0, 0, 0)  

    hbox = Gtk.HBox()
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label8, 0, 0, 0)  
    
    dialog.show_all()
    response = dialog.run()   
    gotxt = entry.get_text()     
    dialog.destroy()

    if response == Gtk.ResponseType.ACCEPT:        
    
        # Save it for later use 
        self2.oldgoto = gotxt
        pedconfig.conf.sql.put("goto", gotxt)                               
  
        if gotxt == "":
            self2.mained.update_statusbar("Must specify line to goto.")
            return          
        try:
            num = int(gotxt)
        except:
            self2.mained.update_statusbar("Invalid line number.")
            return

        if num > len(self2.text):
            num = len(self2.text)     
            self2.gotoxy(0, num - 1)
            self2.mained.update_statusbar("Goto line passed end, landed on %d" %  num)
        else:
            self2.gotoxy(self2.xpos + self2.caret[0], num -1)
            self2.mained.update_statusbar("Done goto line %d" % num)            
    
    warnings.simplefilter("default")
        
# EOF
















