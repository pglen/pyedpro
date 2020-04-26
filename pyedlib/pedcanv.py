#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, math, pickle

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
from    .pedtdlg import *

canv_testmode = 0

RECT = 1
TEXT = 2
CIRC = 3
ROMB = 4

globzorder = 0
globgroup = 0

def canv_colsel(oldcol, title):

    csd = Gtk.ColorSelectionDialog(title)
    col = csd.get_color_selection()
    #col.set_current_color(float2col(oldcol))
    response = csd.run()
    color = 0
    if response == Gtk.ResponseType.OK:
        color = col.get_current_color()
        #print ("color", color)
    csd.destroy()
    return col2float(color)

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
        self.id = utils.randlett(8)
        self.groupid = 0
        self.pgroupid = 0
        self.orgdrag = ()
        self.other = []
        self.mouse = Rectangle()
        globzorder = globzorder + 1
        self.zorder = globzorder
        #globzorder = globzorder + 1
        self.type = ""

    def dump(self):
        col1 = float2str(self.col1)
        col2 = float2str(self.col2)

        rect2 = self.rect.copy()

        #if self.type == "Circ":
        #    print("Half")
        #    rect2.w = rect2.w / 2; rect2.h = rect2.h / 2
        #print("x type: ", self.type, self.rect.dump(), rect2.dump())

        return (self.id, self.text, self.type, str(self.zorder),
                    str(self.groupid), rect2.dump(),
                        str(col1), str(col2), self.other)

    def __str__(self):
        return (self.id, "[" + self.text + "]", self.type, str(self.zorder),
                    str(self.groupid), str(self.rect), str(self.other))

    def expand_size(self, self2):

        neww = self.rect.x + self.rect.w
        if neww > self2.rect.width:
            self2.set_size_request(neww + 20, self2.rect.height)

        newhh = self.rect.y + self.rect.h
        if newhh > self2.rect.height:
            self2.set_size_request(self2.rect.width, newhh + 20)


    def corners(self, self2, rectz, rsize):

        self2.crh.set_source_rgb(self.col2);

        self.mx[0] = Rectangle(rectz.x - rsize/2,
                    rectz.y - rsize/2, rsize, rsize)

        #rsize += 3
        self.mx[1] = Rectangle(rectz.x + rectz.w - rsize/2,
                    rectz.y - rsize/2, rsize, rsize)

        #rsize += 3
        self.mx[2] = Rectangle(rectz.x - rsize/2,
                    rectz.y + rectz.h - rsize/2, rsize, rsize)

        #rsize += 3
        self.mx[3] = Rectangle(rectz.x + rectz.w - rsize/2,
                    rectz.y + rectz.h - rsize/2, rsize, rsize)

        for aa in self.mx:
            if aa:
                self2.crh.rectangle(aa)
        self2.cr.fill()

        # Last one is handler
        bb = self.mx[3].copy();  bb.resize(-5)
        self2.crh.set_source_rgb(self.col1);
        self2.crh.rectangle(bb)
        self2.cr.fill()

# ------------------------------------------------------------------------
# Rectangle object

class RectObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(RectObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Rect"

    def draw(self, cr, self2):

        #print("RectObj draw", str(self.rect))

        self.expand_size(self2)
        self2.crh.set_source_rgb(self.col1); self2.crh.rectangle(self.rect)
        cr.fill()

        self2.crh.set_source_rgb(self.col2); self2.crh.rectangle(self.rect)
        cr.stroke()

        if self.selected:
            self.corners(self2, self.rect, self.rsize)

        if self.text:
            self2.crh.set_source_rgb(self.col2);
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            xxx = self.rect.w / 2 - xx / 2
            yyy = self.rect.h / 2 - yy / 2
            cr.move_to(self.rect.x + xxx, self.rect.y + yyy)
            PangoCairo.show_layout(cr, self2.layout)

    def hittest(self, rectx):
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

    def center(self):
        return (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)

# ------------------------------------------------------------------------
# Rectangle object

class TextObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(TextObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.fd = Pango.FontDescription()
        self.txx = 0
        self.tyy = 0
        self.type = "Text"

    def draw(self, cr, self2):

        self.expand_size(self2)

        if self.selected:
            rrr = Rectangle(self.rect.x, self.rect.y, self.txx, self.tyy)
            self.corners(self2, rrr, self.rsize)

        if self.text:

            self2.crh.set_source_rgb(self.col2);
            self.fd.set_family("Arial")
            self.fd.set_size(self.rect.h * Pango.SCALE);

            self.pangolayout = self2.create_pango_layout("a")
            self.pangolayout.set_font_description(self.fd)
            self.pangolayout.set_text(self.text, len(self.text))
            self.txx, self.tyy = self.pangolayout.get_pixel_size()

            self2.crh.set_source_rgb(self.col2);
            cr.move_to(self.rect.x, self.rect.y)
            PangoCairo.show_layout(cr, self.pangolayout)

    def hittest(self, rectx):
        recttxt = Rectangle(self.rect.x, self.rect.y, self.txx, self.tyy)
        inte = rectx.intersect(recttxt)
        return inte[0]

    def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret

    def center(self):
        return (self.rect.x + self.txx / 2, self.rect.y + self.tyy / 2)


class RombObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(RombObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Romb"

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

    def draw(self, cr, self2):

        self2.crh.set_source_rgb(self.col1); self2.crh.romb(self.rect)
        cr.fill()

        self2.crh.set_source_rgb(self.col2); self2.crh.romb(self.rect)
        cr.stroke()

        if self.selected:
            self.corners(self2, self.rect, self.rsize)
        if self.text:
            self2.crh.set_source_rgb(self.col2);
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            xxx = self.rect.w / 2 - xx / 2
            yyy = self.rect.h / 2 - yy / 2
            cr.move_to(self.rect.x + xxx, self.rect.y + yyy)
            PangoCairo.show_layout(cr, self2.layout)

    def center(self):
        return (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)


class CircObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):

        rect2 = Rectangle(rect[0], rect[1], rect[2], rect[3])
        super(CircObj, self).__init__( rect2, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Circ"

    def hittest(self, rectx):

        ulx = self.rect.x - self.rect.w
        uly = self.rect.y - self.rect.w
        rectc = Rectangle(ulx, uly, self.rect.w * 2, self.rect.w * 2)
        inte = rectx.intersect(rectc)
        return inte[0]

    def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret

    def draw(self, cr, self2):

        self2.crh.set_source_rgb(self.col1)
        self2.crh.circle(self.rect.x, self.rect.y, self.rect.w)
        cr.fill()

        self2.crh.set_source_rgb(self.col2);
        self2.crh.circle(self.rect.x, self.rect.y, self.rect.w)
        cr.stroke()

        if self.selected:
            ulx = self.rect.x - self.rect.w
            uly = self.rect.y - self.rect.w
            www = 2 * self.rect.w
            rrr = Rectangle(ulx, uly, www, www)
            self.corners(self2, rrr, self.rsize)

        if self.text:
            self2.crh.set_source_rgb(self.col2);
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            cr.move_to(self.rect.x - xx / 2, self.rect.y - yy / 2 )
            PangoCairo.show_layout(cr, self2.layout)

    def center(self):
        return (self.rect.x, self.rect.y)

class Canvas(Gtk.DrawingArea):

    def __init__(self, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
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
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.noop_down = False
        self.hand = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor(Gdk.CursorType.SIZING)
        self.cross =  Gdk.Cursor(Gdk.CursorType.TCROSS)
        self.hair =  Gdk.Cursor(Gdk.CursorType.CROSSHAIR)

    def show_status(self, strx):
        if self.statusbar:
            self.statusbar.set_text(strx)

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if self.drag:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.hand)
            #print ("drag coord", self.dragcoord[0],  self.dragcoord[1], event.x, event.y)
            xd = int(self.dragcoord[0] - event.x)
            yd = int(self.dragcoord[1] - event.y)
            #print ("delta", xd, yd)
            for aa in self.coll:
                if aa.selected:
                    aa.rect.x = aa.orgdrag.x  - xd
                    aa.rect.y = aa.orgdrag.y  - yd
                    # Also move whole group IN NOT SHIFT
                    if aa.groupid and not (event.state & Gdk.ModifierType.SHIFT_MASK) :
                        for bb in self.coll:
                            if aa.groupid == bb.groupid:
                                bb.rect.x = bb.orgdrag.x  - xd
                                bb.rect.y = bb.orgdrag.y  - yd
            self.queue_draw()

        elif self.resize:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.sizing)
            #print ("resize", self.resize.text,  event.x, event.y)
            xd = int(self.dragcoord[0] - event.x)
            yd = int(self.dragcoord[1] - event.y)
            #print ("rdelta", xd, yd)

            if self.size2[0] - xd > 2:
                self.resize.rect.w = self.size2[0] - xd
            if self.size2[1] - yd > 2:
                self.resize.rect.h = self.size2[1] - yd

            self.queue_draw()
        else:
            onmarker = False
            hit = Rectangle(event.x, event.y, 2, 2)
            # Check if on marker
            for cc in self.coll:
                if cc.hitmarker(hit):
                    onmarker = True

            gdk_window = self.get_root_window()
            if onmarker:
                gdk_window.set_cursor(self.cross)
            elif self.noop_down:
                gdk_window.set_cursor(self.hair)
            else:
                gdk_window.set_cursor(self.arrow)

        '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                    print( "Shift ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    print( "Ctrl ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.MOD1_MASK :
                    print( "Alt ButPress x =", event.x, "y =", event.y)
                '''

    def area_button(self, area, event):
        self.mouse = Rectangle(event.x, event.y, 4, 4)
        #print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)

        if  event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            print("DBL click", event.button)

        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None
            self.noop_down = False
            self.get_root_window().set_cursor(self.arrow)

        if  event.type == Gdk.EventType.BUTTON_PRESS:
            hit = Rectangle(event.x, event.y, 2, 2)
            hitx = None
            if event.button == 1:
                if not event.state & Gdk.ModifierType.SHIFT_MASK and \
                            not event.state & Gdk.ModifierType.CONTROL_MASK:
                    # Operate on pre selected
                    if not self.drag:
                        for bb in self.coll:
                            if bb.selected:
                                #print("Operate on selected", bb.id)
                                if bb.hitmarker(hit):
                                    #print("Hit on marker")
                                    self.resize = bb
                                    self.drag = None
                                    self.dragcoord  = (event.x, event.y)
                                    self.size2 = (self.resize.rect.w, self.resize.rect.h)
                                    return
                                elif bb.hittest(hit):
                                    self.drag = bb
                                    self.dragcoord  = (event.x, event.y)
                                    for cc in self.coll:
                                        if cc.selected:
                                            cc.orgdrag = cc.rect.copy()
                                            # Also move whole group
                                            if cc.groupid:
                                                for bb in self.coll:
                                                    if cc.groupid == bb.groupid:
                                                        bb.orgdrag = bb.rect.copy()

                    if self.drag:
                        return

                sortx = sorted(self.coll, reverse = True, key = lambda item: item.zorder)

                # Execute new hit test on drag immidiate
                #for aa in self.coll:
                for aa in sortx:
                    if aa.hittest(hit): # and aa.selected:
                        hitx = aa
                        self.drag = aa
                        self.dragcoord  = (event.x, event.y)
                        aa.orgdrag = aa.rect.copy()
                        # Also move whole group
                        if aa.groupid:
                            for bb in self.coll:
                                if bb.groupid == aa.groupid:
                                    bb.orgdrag = bb.rect.copy()
                        break

                #for bb in self.coll:
                for bb in sortx:
                    if bb == hitx:
                        if event.state & Gdk.ModifierType.CONTROL_MASK:
                            bb.selected = not bb.selected
                        else:
                            bb.selected = True
                            #break
                    else:
                        if event.state & Gdk.ModifierType.SHIFT_MASK or \
                            event.state & Gdk.ModifierType.CONTROL_MASK:
                            pass
                        else:
                            bb.selected = False

                if not hitx:
                    self.noop_down = True
                    gdk_window = self.get_root_window()
                    gdk_window.set_cursor(self.hair)

                self.queue_draw()

            elif event.button == 3:
                #print("Right click")
                bb = None
                # Execute new hit test
                for aa in self.coll:
                    if aa.hittest(hit):
                        bb = aa
                        break
                if bb:
                    cnt = 0
                    for aa in self.coll:
                        if aa.selected:
                            cnt += 1

                    mms = ("Alignment",
                            "Align Left","Align Right",
                            "Align Top","Align Buttom",
                            "Align Mid X","Align Mid Y",)
                    sss = Menu(mms, self.menu_sss, event, True)

                    mmz = ( "Z-Order",
                            "To Front","To Back",
                            "One forward","One Backward",)
                    zzz = Menu(mmz, self.menu_zzz, event, True)

                    ccs = ( "Connect",
                            "Connect Objects (Reg)", "Connect Objects (Yes)",
                            "Connect Objects (No)", "Disconnect Objects",)

                    ccc = Menu(ccs, self.menu_ccc, event, True)

                    if cnt > 1:
                        mmm = (bb.text, ccc,
                        "Group Objects", "Ungroup Objects", sss, zzz)

                        Menu(mmm, self.menu_action, event)

                    else:
                        mmm = (bb.text, "Object Properties", "Text",
                                "FG Color", "BG Color", zzz)
                        Menu(mmm, self.menu_action2, event)

                    self.queue_draw()
                else:
                    mmm = ("Main Menu", "Dump Objects", "Add Rectangle",
                                "Add Rombus", "Add Circle", "Add Text",
                                    "Save Objects", "Load Objects", "-", "Clear Canvas")
                    Menu(mmm, self.menu_action3, event)
            else:
                print("??? click", event.button)

    def menu_ccc(self, item, num):
        print ("Connect", item, num)
        if num == 1:
            #print ("Conn obj", item, num)
            ccc = []
            for aa in self.coll:
                if aa.selected:
                    ccc.append(aa)
            for aa in ccc[1:]:
                ccc[0].other.append(aa.id)

        if num == 4:
            ccc = []
            for aa in self.coll:
                if aa.selected:
                    ccc.append(aa)

            if len(ccc) == 2:
                #print("Please select two objects to disconnect")
                print("disconnecting", ccc[0].text, ccc[1].text)
                try:    ccc[0].other.remove(ccc[1].id)
                except: pass
            else:
                for dd in ccc:
                    dd.other = []


    def menu_zzz(self, item, num):

        #print ("Z order", item, num)
        global globzorder
        if num == 1:
            for aa in self.coll:
                if aa.selected:
                    globzorder = globzorder + 1
                    aa.zorder = globzorder
                    break

        if num == 2:
            for aa in self.coll:
                aa.zorder += 1
            for aa in self.coll:
                if aa.selected:
                    aa.zorder = 0
                    break

        self.queue_draw()


    def menu_sss(self, item, num):
            print ("Align", item, num)

    def menu_action(self, item, num):

        # Group
        if num == 2:
            global globgroup
            globgroup += 1
            for aa in self.coll:
                if aa.selected:
                    aa.groupid = globgroup

        # Ungroup
        if num == 3:
            for aa in self.coll:
                if aa.selected:
                    for bb in self.coll:
                        if aa.groupid == bb.groupid:
                            bb.groupid = 0
                        aa.groupid = 0
        # Align
        if num == 5:
            for aa in self.coll:
                if aa.selected:
                    for bb in self.coll:
                        if bb.selected:
                            bb.rect.x = aa.rect.x
                    break
        self.queue_draw()

    def menu_action2(self, item, num):

        if num == 2:
            print("Getting text")
            bb = None
            for aa in self.coll:
                    if aa.selected:
                        bb = aa
            if bb:
                response, txt = textdlg(bb.text, self.get_toplevel())
                if response == Gtk.ResponseType.ACCEPT:
                    #print("Got text", txt)
                    bb.text = txt
                    self.queue_draw()

        if num == 3:
            ccc = canv_colsel(0, "Foreground Color")
            for aa in self.coll:
                if aa.selected:
                    aa.col2 = ccc
            self.queue_draw()

        if num == 4:
            ccc = canv_colsel(0, "Background Color")
            for aa in self.coll:
                if aa.selected:
                    aa.col1 = ccc
            self.queue_draw()


    def menu_action3(self, item, num):
        if num == 1:
            for aa in self.coll:
                print(aa.dump())

        if num == 2:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_rect(coord, rstr, randcolstr())

        if num == 3:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_romb(coord, rstr, randcolstr())

        if num == 4:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 70, 70)
            self.add_circle(coord, rstr, randcolstr())

        if num == 5:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 40, 40)
            self.add_text(coord, rstr, randcolstr())

        if num == 6:
            fff = "outline.pickle"
            #print("Saving to:", fff)
            sum = []
            for aa in self.coll:
                sum.append(aa.dump())
            ff = open(fff, "wb")
            pickle.dump(sum, ff)
            ff.close()

        if num == 7:
            fff = "outline.pickle"
            #print("Loading:", fff)
            ff = open(fff, "rb")
            sum2  = pickle.load(ff)
            ff.close()
            print(sum2)

            for aa in sum2:
                rectx = Rectangle(aa[5])
                if aa[2] == "Rect":
                    obj = self.add_rect(rectx, aa[1], aa[7], aa[6])
                if aa[2] == "Circ":
                    obj = self.add_circle(rectx, aa[1], aa[7], aa[6])
                if aa[2] == "Text":
                    obj = self.add_text(rectx, aa[1], aa[7], aa[6])
                if aa[2] == "Romb":
                    obj = self.add_romb(rectx, aa[1], aa[7], aa[6])

                obj.id = aa[0]
                obj.zorder = int(aa[3])
                obj.groupid = int(aa[4])
                obj.other  = list(aa[8])

        if num == 8:
            pass

        if num == 9:
            self.coll = []
            self.queue_draw()


    def show_objects(self):
        for aa in self.coll:
            print ("GUI Object", aa)

    # Add rectangle to collection of objects
    def add_rect(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        rob = RectObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_text(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        rob = TextObj(coord, text, col1, col2, border, fill)

        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_circle(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        rob = CircObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_romb(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = str2float(crb);    col2 = str2float(crf)
        rob = RombObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def draw_event(self, doc, cr):

        #print ("Painting .. ", self.cnt)
        self.cnt += 1
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        #bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        self.layout = PangoCairo.create_layout(cr)
        self.rect = self.get_allocation()
        self.cr = cr
        self.crh = CairoHelper(cr)

        # Paint white, ignore system BG
        border = 4
        cr.set_source_rgba(255/255, 255/255, 255/255)
        cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.fill()

        # Draw connections
        cr.set_source_rgba(55/255, 55/255, 55/255)
        for aa in self.coll:
            for cc in aa.other:
                for bb in self.coll:
                    if cc == bb.id:
                        #print("connect draw", aa.text, bb.text)
                        aac = aa.center()
                        cr.move_to(aac[0], aac[1])
                        bbc = bb.center()
                        cr.line_to(bbc[0], bbc[1])
                        cr.stroke()

        #for aa in self.coll:
        #    aa.dump()

        sortx = sorted(self.coll, reverse = False, key = lambda item: item.zorder)

        # Draw objects
        #for aa in self.coll:
        for aa in sortx:
            try:
                aa.draw(cr, self)
            except:
                utils.put_exception("Cannot draw " + str(type(aa)))
                #aa.dump()

def set_canv_testmode(flag):
    global canv_testmode
    canv_testmode = flag


# EOF






























