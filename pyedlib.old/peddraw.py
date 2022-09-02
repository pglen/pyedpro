#!/usr/bin/env python

# Drawing operations done here

from __future__ import absolute_import

import signal, os, time, sys, codecs

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import pedconfig

from .keywords import *
from .pedutil import *
from .utils import *

BOUNDLINE   = 80            # Boundary line for col 80 (the F12 func)

class peddraw(object):

    def __init__(self):
        return self

    # Underline with red wiggle
    def draw_wiggle(self, gcr, xx, yy, xx2, yy2):

        gcr.set_line_width(1)

        # The  wiggle took too much processing power .... just a line
        #self.draw_line(gcr, xx, yy, xx2, yy2)

        # Back to Wiggle
        while True:
            xx3 = xx + 4
            if xx3 >= xx2: break
            self.draw_line2(gcr, xx, yy, xx3, yy2+2)
            xx = xx3; xx3 = xx3 + 4
            self.draw_line2(gcr, xx, yy+2, xx3, yy2)
            xx = xx3

        gcr.stroke()

    def draw_line2(self, cr, xx, yy, xx2, yy2):
        #print "draw line", xx, yy
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)

    def draw_line(self, cr, xx, yy, xx2, yy2):
        #print "draw line", xx, yy
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)
        cr.stroke()

    # --------------------------------------------------------------------
    # Draw caret

    def draw_caret(self, gcx):

        gcx.set_line_width(1)
        gcx.set_source_rgba(0, 0, 5)

        #print "drawing caret", self.caret[0], self.caret[1], \
        #        self.caret[0] * self.cxx, self.caret[1] * self. cyy

        try:
            line = self.text[self.ypos + self.caret[1]]
        except:
            line = ""

        xxx = calc_tabs2(line[self.xpos:], self.caret[0], self.tabstop)
        xx = xxx * self.cxx
        #xx = self.caret[0] * self.cxx
        yy = self.caret[1] * self.cyy

        ch = 3 * self.cyy / 3; cw = 3 * self.cxx / 4

        # Order: Top, left right, buttom
        if self.focus:
            # Flash cursor
            if self.bigcaret:
                rxx = xx + self.cxx
                ly = yy + self.cyy; uy = yy
                mmx = xx + cw; mmy = yy + ch
                dist = 80
                self.draw_line(gcx, mmx - dist, uy, mmx + dist, uy)
                self.draw_line(gcx, mmx - dist, ly, mmx + dist, ly)
                self.draw_line(gcx, xx , mmy - dist, xx, mmy + dist)
                self.draw_line(gcx, rxx , mmy - dist, rxx, mmy + dist)
            else:
                if self.insert:
                    self.draw_line(gcx, xx, yy, xx + cw, yy)
                    self.draw_line(gcx, xx + 1, yy, xx + 1, yy + self.cyy )
                    self.draw_line(gcx, xx + 3, yy, xx + 3, yy + self.cyy )
                    self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )
                else:
                    self.draw_line(gcx, xx, yy, xx + cw, yy)
                    self.draw_line(gcx, xx + 1, yy, xx + 1, yy + self.cyy )
                    self.draw_line(gcx, xx + 2, yy, xx + 2, yy + self.cyy )
                    self.draw_line(gcx, xx + 3, yy, xx + 3, yy + self.cyy )
                    self.draw_line(gcx, xx + 4, yy, xx + 4, yy + self.cyy )
                    self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )
        else:
            #self.window.draw_line(gcx, xx, yy, xx + cw, yy)
            self.draw_line(gcx, xx + 1, yy + 2, xx + 1, yy -2 + self.cyy )
            self.draw_line(gcx, xx + 3, yy + 2, xx + 3, yy -2 + self.cyy )
            #self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )

    # --------------------------------------------------------------------
    # This is a response to the draw event request

    def draw_text(self, gc, x, y, text, fg_col = None, bg_col = None):
        #print "draw_text, ",  self.xpos

        if self.hex:
            text2 = ""
            for aa in text:
                tmp = "%02x " % ord(aa)
                text2 += tmp
            text2 = text2[self.xpos * 3:]
        elif self.stab:
            text2 = "";  cnt = 0;
            for aa in text:
                if aa == " ":  text2 += "_"
                elif aa == "\t":
                    spaces = self.tabstop - (cnt % self.tabstop)
                    cnt += spaces - 1
                    for bb in range(spaces):
                        text2 += "o"
                else:
                    text2 += aa
                cnt += 1
            #text2 = text2[self.xpos:]
            #self.layout.set_text(ppp, len(ppp))
        else:
            #text2 = text[self.xpos:].replace("\r", " ")
            text2 = text.replace("\r", " ")

        xx, yy = self.layout.get_pixel_size()

        #utf8_decoder = codecs.getincrementaldecoder('utf8')()
        '''try:
            codecs.decode(text2)
            print ("string is UTF-8, length %d bytes" % len(string))
        except UnicodeError:
            print ("string is not UTF-8")
            return xx, yy'''

        text2 = kill_non_ascii(text2)

        '''bbb = is_ascii(text2)
        if bbb > 0:
            text2 = text2[:bbb-1] + " Non ASCII char "
            #return xx, yy
        '''

        self.layout.set_text(text2, len(text2))

        xx, yy = self.layout.get_pixel_size()

        #offs = self.xpos * self.cxx
        offs = 0
        if bg_col:
            gc.set_source_rgba(bg_col[0], bg_col[1], bg_col[2])

            # The hard way ....
            #rc = self.layout.get_extents().logical_rect
            #rc = self.layout.get_extents().ink_rect
            #print "rc", rc.x, rc.y, rc.width / Pango.SCALE, \
            #            rc.height   / Pango.SCALE
            #gc.rectangle(x, y, rc.width / Pango.SCALE, \
            #            rc.height / Pango.SCALE)
            gc.rectangle(x - offs, y, xx , yy)
            #print self.xpos, x, y, xx, yy
            gc.fill()

        if fg_col:
            gc.set_source_rgba(fg_col[0], fg_col[1], fg_col[2])

        #gc.move_to(x - offs, y)
        gc.move_to(x, y)
        PangoCairo.show_layout(gc, self.layout)

        if self.scol:
            gc.set_source_rgba(0, 0, 0)
            pos = BOUNDLINE - self.xpos
            self.draw_line(gc, pos * self.cxx, \
                     0, pos * self.cxx, self.hhh)

        return xx, yy

    # ----------------------------------------------------------------
    # Paint selection

    def draw_selection(self, gc):

        xx = 0; yy = 0;
        cnt = self.ypos;

        # Normalize (Read: [xy]ssel - startsel  [xy]esel - endsel
        xssel = min(self.xsel, self.xsel2)
        xesel = max(self.xsel, self.xsel2)
        yssel = min(self.ysel, self.ysel2)
        yesel = max(self.ysel, self.ysel2)

        # Override if column selection not active
        if not self.colsel:
            if yssel != yesel:
                xssel = self.xsel
                xesel = self.xsel2

        draw_start = xssel
        if xssel != -1:
            if self.colsel: bgcol = self.cbgcolor
            else: bgcol = self.rbgcolor

            while cnt <  self.xlen:
                if cnt >= yssel and cnt <= yesel:

                    line2 = self.text[cnt]
                    line  = untab_str(self.text[cnt])

                    xssel2 = calc_tabs(line2, xssel, self.tabstop)
                    xesel2 = calc_tabs(line2, xesel, self.tabstop)

                    # adjust selection to tabs
                    if self.colsel:
                        frag = line[xssel2:xesel2]
                        draw_start = xssel2
                    else :   # Startsel - endsel
                        if cnt == yssel and cnt == yesel:   # sel on the same line
                            frag = line[xssel2:xesel2]
                        elif cnt == yssel:                  # start line
                            frag = line[xssel2:]
                        elif cnt == yesel:                  # end line
                            draw_start = 0
                            frag = line[:xesel2]
                        else:
                            draw_start = 0                  # intermediate line
                            frag = line[:]

                    #dss = draw_start #-= self.xpos
                    dss = calc_tabs(line2, draw_start, self.tabstop)
                    dss -= self.xpos
                    self.draw_text(gc, dss * self.cxx, yy, \
                                      frag, self.fgcolor, bgcol)

                cnt = cnt + 1
                yy += self.cyy
                if yy > self.hhh:
                    break

    # --------------------------------------------------------------------
    # Color keywords. Very primitive coloring, a compromise for speed

    def draw_syntax(self, cr):

        if not self.colflag:
            return

        # Paint syntax colors
        xx = 0; yy = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            #line = self.text[cnt]
            line =  untab_str(self.text[cnt])
            for kw in keywords:
                ff = 0          # SOL
                while True:
                    ff = line.find(kw, ff)
                    if ff >= 0:
                        ff2 = calc_tabs(line, ff, self.tabstop) - self.xpos
                        self.draw_text(cr, ff2 * self.cxx, yy, line[ff:ff+len(kw)],
                            self.kwcolor, None)
                        ff += len(kw)
                        #break
                    else:
                        break

            for kw in clwords:
                cc = 0      # SOL
                while True:
                    cc = line.find(kw, cc)
                    if cc >= 0:
                        cc2 = calc_tabs(line, cc, self.tabstop) - self.xpos
                        self.draw_text(cr, cc2 * self.cxx, yy, line[cc:cc+len(kw)],
                            self.clcolor, None)
                        cc += len(kw)
                    else:
                        break

            cnt = cnt + 1
            yy += self.cyy
            if yy > self.hhh:
                break

    # Draw comments. Most files have # comments, so draw it
    # In C and C++ we draw the // comments, Luckily
    # preprocessor has hash, default to drawing it as before.

    def draw_comments(self, cr):

        if not self.colflag:
            return

        xx = 0; yy = 0; ln = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            #line = self.text[cnt]
            line =  untab_str(self.text[cnt])  #.replace("\r", " ")

            # Comments: # or // and "
            # This gives us PY comments, C comments and C defines
            ccc = line.find("#");
            if ccc < 0:
                ccc = line.find("//");

            # Quotes before?
            cccc = line.find('"')

            # If hash does not preceed quote:
            if ccc >= 0 and (cccc > ccc or cccc == -1):
                ccc2 = calc_tabs(line, ccc, self.tabstop)
                ccc2 -= self.xpos
                line2 = line[ccc:]
                self.draw_text(cr, ccc2 * self.cxx, yy,
                                    line2, self.cocolor, None)
            else:
                qqq = 0
                while True:
                    quote = '"'
                    sss = qqq
                    qqq = line.find(quote, qqq);
                    if qqq < 0:
                        # See if single quote is found
                        qqq = line.find("'", sss);
                        if qqq >= 0:
                            quote = '\''
                    if qqq >= 0:
                        qqq += 1
                        qqqq = line.find(quote, qqq)
                        if qqqq >= 0:
                            qqq -= self.xpos
                            qqq2 = calc_tabs(line, qqq, self.tabstop)
                            line2 = line[qqq:qqqq]
                            line3 = line2[self.xpos:]
                            self.draw_text(cr, qqq2 * self.cxx,
                                         yy, line3, self.stcolor, None)
                            qqq = qqqq + 1
                        else:
                            break
                    else:
                        break
            cnt = cnt + 1
            yy += self.cyy
            if yy > self.hhh:
                break

    # Underline spelling errors
    def draw_spellerr(self, cr):
        cr.set_source_rgba(255, 0, 0)
        yyy = self.ypos + self.get_height() / self.cyy
        for xaa, ybb, lcc in self.ularr:
            # Draw within visible range
            if ybb >= self.ypos and ybb < yyy:
                ybb -= self.ypos;
                xaa -= self.xpos; lcc -= self.xpos;
                self.draw_wiggle(cr,
                     xaa * self.cxx, ybb * self.cyy + self.cyy,
                            lcc * self.cxx, ybb * self.cyy + self.cyy)

    # Paint main text
    def draw_maintext(self, cr):

        xx = 0; yy = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            # Got fed up with tabs, generate an untabbed copy for drawing
            if self.hex or self.stab:
               text3 = self.text[cnt]
            else:
               text3 = untab_str(self.text[cnt], self.tabstop)

            #print "'" + text3 + "'"
            text4 = text3[self.xpos:]
            dx, dy = self.draw_text(cr, xx, yy, text4)
            cnt += 1
            yy += dy
            if yy > self.hhh:
                break


# EOF




































