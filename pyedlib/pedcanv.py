
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
globgroup = 0

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
        self.zorder = globzorder
        globzorder = globzorder + 1

        pass

    def dump(self):
        print (self.text, self.id, "zorder", self.zorder,
                    "groid", self.groupid, str(self.rect), self.other)

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

    def draw(self, cr, self2):

        self.expand_size(self2)

        if self.selected:
            rsize = self.rsize;
            self2.crh.set_source_rgb(self.col2);

            self.mx[0] = Rectangle(self.rect.x - rsize/2,
                        self.rect.y - rsize/2, rsize, rsize)

            self.mx[1] = Rectangle(self.rect.x + self.txx - rsize/2,
                        self.rect.y - rsize/2, rsize, rsize)

            self.mx[2] = Rectangle(self.rect.x + self.txx - rsize/2,
                        self.rect.y + self.tyy - rsize/2, rsize, rsize)

            self.mx[3] = Rectangle(self.rect.x - rsize/2,
                        self.rect.y + self.tyy - rsize/2, rsize, rsize)

            for aa in self.mx:
                if aa:
                    self2.crh.rectangle(aa)

            cr.fill()
            #print("selected", self.id)
            pass

        if self.text:

            self.fd.set_family("Arial")
            self.fd.set_size(22 * Pango.SCALE);

            self.pangolayout = self2.create_pango_layout("a")
            self.pangolayout.set_font_description(self.fd)
            self.pangolayout.set_text(self.text, len(self.text))
            self.txx, self.tyy = self.pangolayout.get_pixel_size()

            #self2.crh.set_source_rgb(self.col1); self2.crh.rectangle(self.rect)
            #txtrect = Rectangle(self.rect.x, self.rect.y, self.txx, self.tyy)
            #self2.crh.set_source_rgb(self.col2); self2.crh.rectangle(txtrect)
            #cr.stroke()

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

        if self.text:
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
            rsize = self.rsize;

            ulx = self.rect.x - self.rect.w
            uly = self.rect.y - self.rect.w
            lrx = self.rect.x + self.rect.w
            lry = self.rect.y + self.rect.w

            self2.crh.set_source_rgb(self.col2);

            self.mx[0] = Rectangle(ulx - rsize/2,
                        uly - rsize/2, rsize, rsize)

            self.mx[1] = Rectangle(ulx - rsize/2,
                        lry - rsize/2, rsize, rsize)

            self.mx[2] = Rectangle(lrx - rsize/2,
                        lry - rsize/2, rsize, rsize)

            self.mx[3] = Rectangle(lrx - rsize/2,
                        uly - rsize/2, rsize, rsize)

            for aa in self.mx:
                if aa:
                    self2.crh.rectangle(aa)
            cr.fill()

        if self.text:
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            cr.move_to(self.rect.x - xx / 2, self.rect.y - yy / 2 )
            PangoCairo.show_layout(cr, self2.layout)

    def center(self):
        return (self.rect.x, self.rect.y)


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
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.hand = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor(Gdk.CursorType.SIZING)

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
                    # Also move whole group
                    if aa.groupid:
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
            self.resize.rect.w = self.size2[0] - xd
            self.resize.rect.h = self.size2[1] - yd
            self.queue_draw()
        else:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.arrow)

    def area_button(self, area, event):
        self.mouse = Rectangle(event.x, event.y, 4, 4)
        #print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)
        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None
        if  event.type == Gdk.EventType.BUTTON_PRESS:
            hit = Rectangle(event.x, event.y, 2, 2)
            hitx = None
            if event.button == 1:
                '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                    print( "Shift ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    print( "Ctrl ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.MOD1_MASK :
                    print( "Alt ButPress x =", event.x, "y =", event.y)
                '''
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

                # Execute new hit test on drag immidiate
                for aa in self.coll:
                    if aa.hittest(hit):
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

                for bb in self.coll:
                    if bb == hitx:
                        if event.state & Gdk.ModifierType.CONTROL_MASK:
                            bb.selected = not bb.selected
                        else:
                            bb.selected = True
                    else:
                        if event.state & Gdk.ModifierType.SHIFT_MASK or \
                            event.state & Gdk.ModifierType.CONTROL_MASK:
                            pass
                        else:
                            bb.selected = False
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

                    if cnt > 1:
                        mmm = (bb.text, "Connect Objects", "Disconnect Objects",
                        "Group Objects", "Ungroup Objects", "Align Left")
                        Menu(mmm, self.menu_action, event)
                    else:
                        mmm = (bb.text, "Objects Properties", "Text",
                                "FG color", "BG Color", "To Back", "To Front")
                        Menu(mmm, self.menu_action2, event)

                    self.queue_draw()
                else:
                    mmm = ("Main Menu","Dump Objects", "Add rect", "Add Rombus")
                    Menu(mmm, self.menu_action3, event)

            else:
                print("??? click", event.button)

    def menu_action2(self, item, num):

        global globzorder

        if num == 5:
            for aa in self.coll:
                if aa.selected:
                    globzorder = globzorder + 1
                    aa.zorder = globzorder
                    break

        if num == 6:
            for aa in self.coll:
                aa.zorder += 1
            for aa in self.coll:
                if aa.selected:
                    aa.zorder = 0
                    break
        self.queue_draw()

    def menu_action(self, item, num):
        if num == 1:
            #print ("Conn obj", item, num)
            ccc = []
            for aa in self.coll:
                if aa.selected:
                    ccc.append(aa)
            for aa in ccc[1:]:
                ccc[0].other.append(aa.id)

        if num == 2:
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

        # Group
        if num == 3:
            global globgroup
            globgroup += 1
            for aa in self.coll:
                if aa.selected:
                    aa.groupid = globgroup

        # Ungroup
        if num == 4:
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

    def menu_action3(self, item, num):
        if num == 1:
            for aa in self.coll:
                aa.dump()

        if num == 2:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_rect(coord, rstr, randcolstr())

        if num == 3:
            rstr = utils.randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_romb(coord, rstr, randcolstr())

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

    def add_circ(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
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

        sortx = sorted(self.coll, reverse = True, key = lambda item: item.zorder)

        # Draw objects
        #for aa in self.coll:
        for aa in sortx:
            try:
                aa.draw(cr, self)
            except:
                print("Cannot draw object", type(aa), sys.exc_info())
                aa.dump()

def set_canv_testmode(flag):
    global canv_testmode
    canv_testmode = flag


# EOF



