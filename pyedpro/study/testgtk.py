#!/usr/bin/env python

import signal, os, sys, time, string, pickle, re
#import gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf

# Start of program:

def domod(mmm):

    print (mmm.__name__)
    cnt = 0
    cc = dir(mmm)
    for ee in cc:
        print( ee + ",", )
        #print ee
        if cnt % 4 == 3:
            print
        cnt = cnt + 1

    print
    print

    dd = mmm.__dict__.keys()
    for aa in dd:
        print (aa + ":")
        #print  "-" * len(aa)
        try:
            #ddd = mmm.__dict__[aa].__dict__
            ddd = dir(mmm.__dict__[aa])
            cnt = 0
            for bb in ddd:
                if  not bb.startswith("__"):
                    print (bb + ",",)
                if cnt % 4 == 3:
                    print
                cnt = cnt + 1

            print
            print

        except:
            print ("exception occured")
            pass

if __name__ == '__main__':

    domod(Gtk)
    #domod(Gdk)
    #domod(GLib)
    #domod(Gio)
    #domod(Pango)
    #domod(GObject)
    #domod(GdkPixbuf)
    pass

# EOF
