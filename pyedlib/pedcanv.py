
#!/usr/bin/env python

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, math

#from six.moves import range

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import  peddoc, pedconfig, pedofd
from . import  pedync, pedspell, pedfont
from . import  pedcolor, pedlog, utils

# Into our name space
from    .pedmenu import *
from    .pedui import *
from    .pedutil import *
from    .pedgui import *
from    .pedcolor import *

canv_testmode = 0

RECT = 1
TEXT = 2
CIRC = 3
ROMB = 4

globzorder = 0

class DrawObj():

    def __init__(self,  rect, text, col1, col2, border, fill):

        global globzorder

        self.rect = rect
        self.text = text
        self.col1 = col1
        self.col2 = col2
        self.border = border
        self.fill = fill
        self.selected = False
        self.zorder = globzorder
        self.id = utils.randlett(8)
        self.groupid = 0
        self.pgroupid = 0

        globzorder = globzorder + 1

        pass

    def dump(self):
        print ("zorder", self.zorder, "groupid", self.groupid)

    def expand_size(self, self2):

        neww = self.rect.x + self.rect.w
        if neww > self2.rect.width:
            self2.set_size_request(neww + 20, self2.rect.height)

        newhh = self.rect.y + self.rect.h
        if newhh > self2.rect.height:
            self2.set_size_request(self2.rect.width, newhh + 20)

# ------------------------------------------------------------------------
# Rectangle object

class RectObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(RectObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size

    def draw(self, cr, self2):

        #print("RectObj draw", str(self.rect))

        self.expand_size(self2)
        self2.crh.set_source_rgb(self.col1); self2.crh.rectangle(self.rect)
        cr.fill()

        self2.crh.set_source_rgb(self.col2); self2.crh.rectangle(self.rect)
        cr.stroke()

        if self.selected:
            rsize = self.rsize;
            self2.crh.set_source_rgb(self.col2);

            self.mx[0] = Rectangle(self.rect.x - rsize/2,
                        self.rect.y - rsize/2, rsize, rsize)

            self.mx[1] = Rectangle(self.rect.x + self.rect.w - rsize/2,
                        self.rect.y - rsize/2, rsize, rsize)

            self.mx[2] = Rectangle(self.rect.x + self.rect.w - rsize/2,
                        self.rect.y + self.rect.h - rsize/2, rsize, rsize)

            self.mx[3] = Rectangle(self.rect.x - rsize/2,
                        self.rect.y + self.rect.h - rsize/2, rsize, rsize)

            for aa in self.mx:
                if aa:
                    self2.crh.rectangle(aa)

            cr.fill()
            #print("selected", self.id)
            pass

        if self.text:
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            xxx = self.rect.w / 2 - xx / 2
            yyy = self.rect.h / 2 - yy / 2
            cr.move_to(self.rect.x + xxx, self.rect.y + yyy)
            PangoCairo.show_layout(cr, self2.layout)

    def hittest(self, rectx):

        #if aa[0] == CIRC:
        #    rect = Rectangle(aa[1][0], aa[1][1], aa[1][2], aa[1][2])
        inte = rectx.intersect(self.rect)
        return inte[0]

    def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret

#self.coll.append((ROMB, coord, text, col1, col2, border, fill))

'''
class RombObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(RombObj, self).__init__(rect)
        self.text = text
        self.col1 = col1
        self.col2 = col2
        self.border = border
        self.fill = fill

    def draw(self, cr, self2):

        self2.crh.set_source_rgb(self.col1); self2.crh.romb(self.rect)
        cr.fill()

        self2.crh.set_source_rgb(self.col2); self2.crh.romb(self.rect)
        cr.stroke()

        if self.selected:
            pass

        if self.text:
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            xxx = self.rect.w / 2 - xx / 2
            yyy = self.rect.h / 2 - yy / 2
            cr.move_to(self.rect.x + xxx, self.rect.y + yyy)
            PangoCairo.show_layout(cr, self2.layout)
'''

class Canvas(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("draw", self.draw_event)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("button-press-event", self.area_button)
        self.connect("button-release-event", self.area_button)
        self.coll = []
        self.cnt = 0
        self.drag = None
        self.resize = None
        self.coord = (0,0)
        self.coord2 = (0,0)
        self.size2 = (0,0)

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if self.drag:
            #print ("drag", self.drag.text,  event.x, event.y)
            xd = int(self.coord[0] - event.x)
            yd = int(self.coord[1] - event.y)
            #print ("delta", xd, yd)
            self.drag.rect.x = self.coord2[0] - xd
            self.drag.rect.y = self.coord2[1] - yd
            self.queue_draw()

        elif self.resize:
            #print ("resize", self.resize.text,  event.x, event.y)
            xd = int(self.coord[0] - event.x)
            yd = int(self.coord[1] - event.y)
            #print ("rdelta", xd, yd)
            self.resize.rect.w = self.size2[0] - xd
            self.resize.rect.h = self.size2[1] - yd
            self.queue_draw()

    def area_button(self, area, event):

        print( "ButPress", event.type, "state", event.state, " x =", event.x, "y =", event.y)

        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None


        if  event.type == Gdk.EventType.BUTTON_PRESS:
            if event.get_state() & Gdk.ModifierType.BUTTON1_MASK:
                print("but1")

            if event.get_state() & Gdk.ModifierType.BUTTON3_MASK:
                print("but3")


            '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                print( "Shift ButPress x =", event.x, "y =", event.y)

            if event.state & Gdk.ModifierType.CONTROL_MASK:
                print( "Ctrl ButPress x =", event.x, "y =", event.y)

            if event.state & Gdk.ModifierType.MOD1_MASK :
                print( "Alt ButPress x =", event.x, "y =", event.y)
            '''

            hit = Rectangle(event.x, event.y, 2, 2)
            #hit.dump()

            hitx = None
            # Operate on pre selected
            for bb in self.coll:
                if bb.selected:
                    print("Operate on selected", bb.id)
                    if bb.hitmarker(hit):
                        print("Hit on marker")
                        self.resize = bb
                        self.drag = None
                        self.coord  = (event.x, event.y)
                        self.size2 = (self.resize.rect.w, self.resize.rect.h)
                        return
                    elif bb.hittest(hit):
                        self.drag = bb
                        self.coord  = (event.x, event.y)
                        self.coord2 = (self.drag.rect.x, self.drag.rect.y)
                        return

            # Execute new hit test
            for aa in self.coll:
                if aa.hittest(hit):
                    print("intersect", aa.text, aa.id)
                    hitx = aa
                    self.drag = aa
                    self.coord  = (event.x, event.y)
                    self.coord2 = (self.drag.rect.x, self.drag.rect.y)
                    break

            for bb in self.coll:
                if bb == hitx:
                    bb.selected = True
                else:
                    bb.selected = False

            self.queue_draw()

                #if type(aa) == RectObj: # or type(aa) == RombObj:
                #    rect = aa.rect

                #if aa[0] == CIRC:
                #    rect = Rectangle(aa[1][0], aa[1][1], aa[1][2], aa[1][2])

                #inte = hit.intersect(rect)
                #if inte[0]:

            pass

    def show_objects(self):
        for aa in self.coll:
            print ("GUI Object", aa)

    # Add rectangle to collection of objects
    def add_rect(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        rob = RectObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        return rob

    def add_circ(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        self.coll.append((CIRC, coord, text, col1, col2, border, fill))

    def add_romb(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        #rob = RombObj(coord, text, col1, col2, border, fill)
        #self.coll.append(rob)
        #return rob

    def draw_event(self, doc, cr):

        #print ("Painting .. ", self.cnt)
        self.cnt += 1
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        #bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        self.layout = PangoCairo.create_layout(cr)
        self.rect = self.get_allocation()
        self.crh = CairoHelper(cr)

        # Paint white, ignore system BG
        border = 4
        cr.set_source_rgba(255/255, 255/255, 255/255)
        cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.fill()
        #cr.stroke()

        # Draw objects
        for aa in self.coll:

            if type(aa) == RectObj:
                #print("rectobj", aa)
                aa.draw(cr, self)

            #if type(aa) == RombObj:
            #    #print("rombobj", aa)
            #    aa.draw(cr, self)

            '''
            if aa[0] == CIRC:
                neww = aa[1][0] + aa[1][2]
                if neww > rect.width:
                    self.set_size_request(neww + 20, rect.height)

                newhh = aa[1][1] + aa[1][2]
                if newhh > rect.height:
                    self.set_size_request(rect.width, newhh + 20)

                crh.set_source_rgb(aa[3])
                crh.circle(aa[1][0], aa[1][1], aa[1][2])
                cr.fill()

                crh.set_source_rgb(aa[4]); crh.circle(aa[1][0], aa[1][1], aa[1][2])
                cr.stroke()

                if aa[2]:
                    self.layout.set_text(aa[2], len(aa[2]))
                    xx, yy = self.layout.get_pixel_size()
                    cr.move_to(aa[1][0] - xx / 2, aa[1][1] - yy / 2)
                    PangoCairo.show_layout(cr, self.layout)

            newhh = self.rect.x + self.rect.w
            if neww > rect.width:
                self.set_size_request(neww + 20, rect.height)

            newhh = aa[1][1] + aa[1][3]
            if newhh > rect.height:
                self.set_size_request(rect.width, newhh + 20)
            if aa[0] == ROMB:

                neww = aa[1][0] + aa[1][2]
                if neww > rect.width:
                    self.set_size_request(neww + 20, rect.height)
                newhh = aa[1][1] + aa[1][2]
                if newhh > rect.height:
                    self.set_size_request(rect.width, newhh + 20)

                crh.set_source_rgb(aa[3])
                crh.romb(aa[1])
                cr.fill()

                crh.set_source_rgb(aa[4]);
                crh.romb(aa[1])
                cr.stroke()

                if aa[2]:
                    self.layout.set_text(aa[2], len(aa[2]))
                    xx, yy = self.layout.get_pixel_size()
                    xxx = aa[1][2] / 2 - xx / 2
                    yyy = aa[1][3] / 2 - yy / 2
                    cr.move_to(aa[1][0] + xxx, aa[1][1] + yyy)
                    PangoCairo.show_layout(cr, self.layout)
               '''

def set_canv_testmode(flag):
    global canv_testmode
    canv_testmode = flag




















































































































































































