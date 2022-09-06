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
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *
from    pedlib.pedcolor import *
from    pedlib.pedtdlg import *

#sys.path.append('..' + os.sep + "pycommon")
from pycommon.pggui import *

RECT = 1
TEXT = 2
CIRC = 3
ROMB = 4

globzorder = 0; globgroup = 0

class DrawObj(object):

    def __init__(self,  rect, text, col1, col2, border, fill):

        global globzorder

        self.rect = rect
        self.text = text
        self.col1 = col1
        self.col2 = col2
        self.border = border
        self.fill = fill
        self.selected = False
        self.id =  randlett(8)
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
        return str(
                (
                self.id, "[" + self.text + "]", self.type, str(self.zorder),
                    str(self.groupid), str(self.rect), str(self.other))
             )

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

        # Last one is the handler
        bb = self.mx[3].copy();  bb.resize(-5)
        self2.crh.set_source_rgb(self.col1);
        self2.crh.rectangle(bb)
        self2.cr.fill()

    def hitmarker(self, rectx):
        ret = 0 #False
        for aa in range(len(self.mx)):
            if self.mx[aa]:
                if rectx.intersect(self.mx[aa])[0]:
                    ret = aa + 1
                    break
        #if ret:
        #    print ("drawobj  hitmarker", ret)

        return ret

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

        www = self.rect.w / 40

        if www < .1: www = .1
        cr.set_line_width(www);

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

        cr.set_line_width(1);

    def hittest(self, rectx):
        inte = rectx.intersect(self.rect)
        return inte[0]

    '''def hitmarker(self, rectx):
        ret = False
        for aa in range(len(self.mx)):
            if self.mx[aa]:
                if rectx.intersect(self.mx[aa])[0]:
                    ret = aa
                    break
        return ret
    '''
    def center(self):
        return (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)

# ------------------------------------------------------------------------
# Line object

class LineObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(LineObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Line"

    def draw(self, cr, self2):

        #print("LineObj draw", str(self.rect))

        self.expand_size(self2)
        cr.set_source_rgb(self.col2[0], self.col2[1], self.col2[2])

        cr.move_to(self.rect[0], self.rect[1])
        cr.line_to(self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])
        #cr.fill()
        cr.stroke()

        #self2.crh.set_source_rgb(self.col2); self2.crh.rectangle(self.rect)
        #cr.stroke()

        if self.selected:
            self.corners(self2, self.rect, self.rsize)

        '''if self.text:
            self2.crh.set_source_rgb(self.col2);
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            xxx = self.rect.w / 2 - xx / 2
            yyy = self.rect.h / 2 - yy / 2
            cr.move_to(self.rect.x + xxx, self.rect.y + yyy)
            PangoCairo.show_layout(cr, self2.layout)'''

    def hittest(self, rectx):
        inte = rectx.intersect(self.rect)
        #print("intersect", inte, "rectx", str(rectx), str(self.rect))
        return inte[0]

    '''def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret
    '''
    def center(self):
        return (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)

class CurveObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill):
        super(CurveObj, self).__init__( rect, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Curve"

    def draw(self, cr, self2):

        #print("CurveObj draw", str(self.rect))

        self.expand_size(self2)
        cr.set_source_rgb(self.col2[0], self.col2[1], self.col2[2])

        cr.move_to(self.rect[0], self.rect[1])
        cr.line_to(self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])
        #cr.fill()
        cr.stroke()

        #self2.crh.set_source_rgb(self.col2); self2.crh.rectangle(self.rect)
        #cr.stroke()

        cent = self.center()
        self.crect = Rectangle(cent[0], cent[1], self.rsize, self.rsize)

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

        if self.selected:
            self2.crh.set_source_rgb(self.col2);
            self2.crh.rectangle(self.crect)
            cr.stroke()

    def hittest(self, rectx):
        inte = rectx.intersect(self.rect)
        #print("intersect", inte, "rectx", str(rectx), str(self.rect))
        return inte[0]

    def hitmarker(self, rectx):
        ret = 0
        ret = super(CurveObj, self).hitmarker(rectx)
        if not ret:
            if rectx.intersect(self.crect)[0]:
                ret = 5

        #if ret:
        #    print("hit curve",  ret)

        return ret

    def center(self):
        return (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)

# ------------------------------------------------------------------------
# Text object

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

    '''def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret
    '''
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

    '''def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret
    '''

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

    '''def hitmarker(self, rectx):
        ret = False
        for aa in self.mx:
            if aa:
                if rectx.intersect(aa)[0]:
                    ret = True
                    break
        return ret
    '''
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

# ---------------------------------------------------------------

def stroke_dims(arrx):

    ul_x = 10000; ul_y = 10000; lr_x = 0; lr_y = 0
    for aa, bb in arrx:
        if ul_x > aa:
            ul_x = aa
        if ul_y > bb:
            ul_y = bb

        if lr_x < aa:
            lr_x = aa
        if lr_y < bb:
            lr_y = bb

    #print("Stroke dims", ul_x, ul_y, lr_x, lr_y)
    # Correct faulty one
    if ul_x == 10000 or ul_y == 10000:
        ul_x = 10; ul_y = 10; lr_x = 20; lr_y = 20
    return  (ul_x, ul_y, lr_x - ul_x, lr_y - ul_y)


class StrokeObj(DrawObj):

    def __init__(self, rect, text, col1, col2, border, fill, arr):

        rect2 = Rectangle(rect[0], rect[1], rect[2], rect[3])

        super(StrokeObj, self).__init__( rect2, text, col1, col2, border, fill)

        self.mx = [0, 0, 0, 0]      # side markers
        self.rsize = 12             # Marker size
        self.type = "Stroke"
        self.arr = []

        # Convert to relative coords
        for aa, bb in arr:
            self.arr.append((aa - rect[0], bb - rect[1]))

    def hittest(self, rectx):
        inte = rectx.intersect(self.rect)
        return inte[0]

    def draw(self, cr, self2):

        # Calc aspect x y
        org = Rectangle(stroke_dims(self.arr))

        #self2.crh.set_source_rgb(self.col1)
        self2.crh.set_source_rgb(self.col2);

        init = 0;
        for aa, bb in self.arr:
            aaa = aa; bbb = bb
            try:
                aaa = aa *  self.rect.w / org.w;
                bbb = bb *  self.rect.h / org.h;
            except:
                pass

            if init == 0:
                cr.move_to(aaa + self.rect.x, bbb + self.rect.y)
            else:
                cr.line_to(aaa + self.rect.x, bbb + self.rect.y)
            init += 1
        cr.stroke()

        if self.selected:
            self.corners(self2, self.rect, self.rsize)

        if self.text:
            self2.crh.set_source_rgb(self.col2);
            self2.layout.set_text(self.text, len(self.text))
            xx, yy = self2.layout.get_pixel_size()
            cr.move_to(self.rect.x - xx / 2, self.rect.y - yy / 2 )
            PangoCairo.show_layout(cr, self2.layout)

    def center(self):
        return (self.rect.x, self.rect.y)


# eof