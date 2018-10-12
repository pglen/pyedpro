#!/usr/bin/env python

# Action Handler for find

from __future__ import absolute_import
from __future__ import print_function
import  time, datetime

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

from . import peddoc, pedync, pedconfig

from .pedutil import *

# Adjust to taste. Estimated memory usage is 50 * MAX_LOG bytes
# Fills up slowly, so not a big issue. Delete ~/.pyedit/pylog.txt if 
# you would like to free the memory used by log
MAX_LOG  = 2000


accum = []

# Print as 'print' would, but replicate to log. This class replicate stdout
# and replicates stdout to regular fd, and puts an entry onto accum.

class fake_stdout():

    def __init__(self):
        #self.old_stdout = os.fdopen(sys.stdout.fileno(), "w")
        self.old_stdout = sys.stdout
        self.flag = True
        self.dt = datetime.datetime(1990, 1, 1);

    def flush(self, *args):
        pass
    
    def write(self, *args):
        global accum
        strx = ""
        if self.flag:
            dt2 = self.dt.now()
            strx =  dt2.strftime("%d/%m/%y %H:%M:%S ")
            self.flag = False 
        
        for aa in args:
            if type(aa) == 'tuple':
                for bb in aa:
                    self.old_stdout.write(str(bb) + " ")
                    strx += str(bb)
            else: 
                self.old_stdout.write(str(aa))
                strx +=  str(aa)   
        
        if strx.find("\n") >= 0:
            self.flag = True 
            
        accum.append(strx)
        self.limit_loglen()       

    def limit_loglen(self):
        global accum
        xlen = len(accum)
        if xlen == 0: return
        if xlen  <  MAX_LOG: return
        self.old_stdout.write("limiting loglen " + str(xlen))
        for aa in range(MAX_LOG / 5):
            try:
                del (accum[0])
            except:
                pass

# Persistance for logs. Disable if you wish.

def  save_log():
    pass
    
def load_log():
    pass
                        
# A quick window to dispat what is in accum
                    
def show_log():
    
    win2 = Gtk.Window()
    try:
        win2.set_icon_from_file(get_img_path("pyedpro_sub.png"))
    except:
        print( "Cannot load log icon")

    win2.set_position(Gtk.WindowPosition.CENTER)
    win2.set_default_size(800, 600)
    
    tit = "pyedpro:log"        
    win2.set_title(tit)
    
    '''win2.set_events(    
                    Gtk.gdk.POINTER_MOTION_MASK |
                    Gtk.gdk.POINTER_MOTION_HINT_MASK |
                    Gtk.gdk.BUTTON_PRESS_MASK |
                    Gtk.gdk.BUTTON_RELEASE_MASK |
                    Gtk.gdk.KEY_PRESS_MASK |
                    Gtk.gdk.KEY_RELEASE_MASK |
                    Gtk.gdk.FOCUS_CHANGE_MASK )'''
    win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

    win2.connect("key-press-event", area_key, win2)
    win2.connect("key-release-event", area_key, win2)

    win2.lab = Gtk.TextView()
    win2.lab.set_editable(False)
    tb = win2.lab.get_buffer()
    iter = tb.get_iter_at_offset(0)
    global accum
    for aa in accum:
        tb.insert(iter, aa)
    
    scroll = Gtk.ScrolledWindow(); scroll.add(win2.lab)
    frame = Gtk.Frame(); frame.add(scroll)
    win2.add(frame)
    win2.show_all()
    
# ------------------------------------------------------------------------

def area_key(area, event, dialog):

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            area.destroy()

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Return:
            #print "Ret"
            area.destroy()

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            area.alt = True;
            
        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if area.alt:
                area.destroy()
                              
    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            area.alt = False;
















































































































