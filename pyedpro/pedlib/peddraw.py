#!/usr/bin/env python

# Drawing operations done here

from __future__ import absolute_import

import signal, os, time, sys, codecs

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

import cairo

from pedlib import pedconfig
from pedlib import pedplug

from pedlib.keywords import *
from pedlib.pedutil import *

BOUNDLINE   = 80            # Boundary line for col 80 (the F12 func)

class peddraw(object):

    def __init__(self, self2):
        self.self2 = self2
        self.utf8_decoder = codecs.getincrementaldecoder('utf8')()

    # Underline with red wiggle
    def draw_wiggle(self, gcr, xx, yy, xx2, yy2):

        gcr.set_line_width(1)

        xx += self.strip
        xx2 += self.strip

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
        #print( "draw line", xx, yy)
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)

    def draw_line(self, cr, xx, yy, xx2, yy2):
        #print( "draw line", xx, yy)
        cr.set_source_rgba(*list(self.self2.carcolor))
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)
        cr.stroke()
        cr.set_source_rgba(*list(self.self2.fgcolor))

    # --------------------------------------------------------------------
    # Draw caret

    def draw_caret(self, gcx):

        gcx.set_line_width(1)
        gcx.set_source_rgba(*list(self.self2.cocolor))

        #print( "drawing caret", self.caret[0], self.caret[1], \
        #        self.caret[0] * self.cxx, self.caret[1] * self. cyy)

        try:
            line = self.text[self.ypos + self.caret[1]]
        except:
            line = ""

        xxx = calc_tabs2(line[self.xpos:], self.caret[0], self.tabstop)
        xx = xxx * self.cxx
        #xx = self.caret[0] * self.cxx
        yy = self.caret[1] * self.cyy

        ch = 3 * self.cyy / 3; cw = 3 * self.cxx / 4

        xx +=  self.strip

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

    def _draw_text(self, gc, x, y, text, fg_col = None, bg_col = None, esc = None):

        #print( "_draw_text",  self.xpos, self.ypos, self.caret, x/self.cxx, y/self.cyy)

        fo = cairo.FontOptions()
        #fo.set_antialias( cairo.ANTIALIAS_FAST)
        fo.set_antialias( cairo.ANTIALIAS_BEST)
        #fo.set_antialias( cairo.ANTIALIAS_DEFAULT)
        #fo.set_antialias( cairo.ANTIALIAS_SUBPIXEL)
        #fo.set_antialias( cairo.ANTIALIAS_GRAY)
        #fo.set_antialias( cairo.ANTIALIAS_NONE)
        #print("cairo fo", fo, fo.get_antialias() )
        gc.set_font_options(fo)

        #x = int(x)
        ## if below zero, shift
        #if not esc:
        #    if x < 0:
        #        text = text[-x:]
        #        x = 0

        x +=  self.strip                # Leave space on the front
        if y/self.cyy == self.caret[1]:
            #print( "_draw_text: '%s' len=%d x=%d y=%d" % (text, len(text), x, y) )
            #print( "_draw_text: len=%d x=%d y=%d" % (len(text), x, y) )
            pass

        if not esc:
            if self.hex:
                text2 = ""
                for aa in text:
                    tmp = "%02x " % ord(aa)
                    text2 += tmp
                text2 = text2[self.xpos * 3:]
                #print("text2", text2)

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
                text2 = text.replace("\r", "a ")
        else:
            #text2 = text[self.xpos:].replace("\r", " ")
            text2 = text.replace("\r", "a ")

        #utf8_decoder = codecs.getincrementaldecoder('utf8')()
        try:
            if type(text2) != str:
                text2 = codecs.decode(text2)
                #print ("string is UTF-8, length %d bytes" % len(text2))
            else:
                pass
                #print ("string is text, length %d bytes" % len(text2))

        except UnicodeError:
            print ("string is not UTF-8")
            #return xx, yy

        #text2 = kill_non_ascii(text2)

        '''bbb = is_ascii(text2)
        if bbb > 0:
            text2 = text2[:bbb-1] + " Non ASCII char "
            #return xx, yy
        '''

        self.layout.set_text(text2, len(text2))

        #xx, yy = self.layout.get_pixel_size()
        #xx, yy = self.layout.get_size()
        #xx /=  Pango.SCALE;
        #yy /=  Pango.SCALE;

        #(pr, lr) = self.layout.get_pixel_extents()
        (pr, lr) = self.layout.get_extents()
        xx = lr.width / Pango.SCALE; yy = lr.height / Pango.SCALE;

        #offs = self.xpos * self.cxx
        offs = 0
        if bg_col:
            gc.set_source_rgba(bg_col[0], bg_col[1], bg_col[2])

            # The hard way ....
            #rc = self.layout.get_extents().logical_rect
            #rc = self.layout.get_extents().ink_rect
            #print( "rc", rc.x, rc.y, rc.width / Pango.SCALE, \
            #            rc.height   / Pango.SCALE  )
            #gc.rectangle(x, y, rc.width / Pango.SCALE, \
            #            rc.height / Pango.SCALE)
            gc.rectangle(x - offs, y, xx , yy)
            #print( self.xpos, x, y, xx, yy)
            gc.fill()

        if fg_col:
            gc.set_source_rgba(fg_col[0], fg_col[1], fg_col[2])

        #gc.move_to(x - offs, y)
        gc.move_to(x, y)
        PangoCairo.show_layout(gc, self.layout)

        # Debug output, help on visuals
        #self.draw_line(gc, x+2, y+yy-5, x+xx-2, y+yy+5)

        if self.scol:
            gc.set_source_rgba(0, 0, 0)
            pos = BOUNDLINE - self.xpos
            self.draw_line(gc, pos * self.cxx, \
                     0, pos * self.cxx, self.hhh, )

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

                    #line2 = self.text[cnt][self.xpos:]
                    line2 = self.text[cnt]

                    xssel2 = calc_tabs(line2, xssel, self.tabstop)
                    xesel2 = calc_tabs(line2, xesel, self.tabstop)
                    line  = untab_str(line2)

                    # adjust selection to tabs
                    if self.colsel:
                        frag = line[xssel2:xesel2]
                        draw_start = xssel2
                    else :   # Startsel - endsel
                        if cnt == yssel and cnt == yesel:   # sel on the same line
                            frag = line[xssel2:xesel2]
                            draw_start = xssel2
                        elif cnt == yssel:                  # start line
                            draw_start = xssel2
                            frag = line[xssel2:]
                        elif cnt == yesel:                  # end line
                            draw_start = 0
                            frag = line[:xesel2]
                        else:
                            draw_start = 0                  # intermediate line
                            frag = line[:]

                    dss = draw_start - self.xpos
                    #dss2 = calc_tabs(line2, draw_start, self.tabstop)
                                #(self.xpos % self.tabstop)
                    #print(dss, dss2)

                    if dss < 0:
                          frag = frag[-dss:]
                          dss = 0
                    self._draw_text(gc, dss * self.cxx, yy, \
                                      frag, self.fgcolor, bgcol)
                cnt = cnt + 1
                yy += self.cyy
                if yy > self.hhh:
                    break

    def _syntax(self, cr, keyw, xx, yy):
        line =  untab_str(self.text[xx])
        for kw in keyw:
            ff = 0          # SOL
            while True:
                ff = line.find(kw, ff)
                if ff >= 0:
                    line3 = line[ff:ff+len(kw)]
                    ff2 = calc_tabs(line, ff, self.tabstop) - self.xpos
                    if ff2 < 0:
                        line3 = line3[-ff2:]
                        ff2 = 0
                    self._draw_text(cr, ff2 * self.cxx, yy, line3,
                                self.kwcolor, None)
                    ff += len(kw)
                    #break
                else:
                    break

    # --------------------------------------------------------------------
    # Color keywords. Very primitive coloring, a compromise for speed

    def draw_syntax(self, cr):

        if not self.colflag:
            return
        try:
            pedplug.syntax(self, cr)
        except:
            print("plugin failed", sys.exc_info())

        # Paint syntax colors
        yy = 0;  xx = int(self.ypos)
        while xx <  self.xlen:
            self._syntax(cr, keywords, xx, yy)
            xx = xx + 1
            yy += self.cyy
            if yy > self.hhh:
                break

    def draw_clsyntax(self, cr):

        if not self.colflag:
            return
        try:
            pedplug.clsyntax(self, cr)
        except:
            print("plugin failed", sys.exc_info())

        # Paint syntax colors
        yy = 0;  xx = int(self.ypos)
        while xx <  self.xlen:
            self._syntax(cr, clwords, xx, yy)
            xx = xx + 1
            yy += self.cyy
            if yy > self.hhh:
                break

    # --------------------------------------------------------------------
    # Color keywords. Very primitive coloring, a compromise for speed

    def draw_clsyntax2(self, cr):

        if not self.colflag:
            return

        try:
            pedplug.clsyntax(self, cr)
        except:
            print("plugin failed", sys.exc_info())

        # Paint syntax colors
        xx = 0; yy = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            #line = self.text[cnt]
            line =  untab_str(self.text[cnt])
            for kw in clwords:
                cc = 0      # SOL
                while True:
                    cc = line.find(kw, cc)
                    if cc >= 0:
                        line3 = line[cc:cc+len(kw)]
                        cc2 = calc_tabs(line, cc, self.tabstop) - self.xpos
                        if cc2 < 0:
                            line3 = line3[-cc2:]
                            cc2 = 0
                        self._draw_text(cr, cc2 * self.cxx, yy, line3,
                                          self.clcolor, None)
                        cc += len(kw)
                    else:
                        break
            cnt = cnt + 1
            yy += self.cyy
            if yy > self.hhh:
                break

    # --------------------------------------------------------------------
    # Draw comments. Most files have # comments, so draw it
    # In C and C++ we draw the // comments, Luckily
    # preprocessor has hash, default to drawing it as before.

    def draw_comments(self, cr):

        if not self.colflag:
            return

        #print("ext=", self.ext)

        xx = 0; yy = 0; ln = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            line =  untab_str(self.text[cnt])

            # Comments: # or // and "
            # This gives us PY comments, C comments and ASM comments

            if self.ext == ".c" or self.ext == ".h" or \
                self.ext == ".cpp" or self.ext == ".hpp" or \
                self.ext == ".php" or self.ext == ".java":
                ccc = line.find("//");
            elif self.ext == ".asm" or self.ext == ".inc":
                ccc = line.find(";");
            else:
                ccc = line.find("#");

            # Quotes before?
            cccc = line.find('"')

            # If hash does preceed quote:
            if ccc >= 0 and (cccc > ccc or cccc == -1):
                line2 = line[ccc:]  #+self.xpos:]
                ff2 = calc_tabs(line, ccc, self.tabstop) - self.xpos
                if ff2 < 0:
                    line2 = line2[-ff2:]
                    ff2 = 0
                self._draw_text(cr, ff2 * self.cxx, yy,
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
                            self._draw_text(cr, qqq2 * self.cxx,
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

    # --------------------------------------------------------------------
    # Underline spelling errors

    def draw_spellerr(self, cr):
        cr.set_source_rgba(255, 0, 0)
        yyy = self.ypos + self.get_height() / self.cyy
        for xaa, ybb, lcc in self.ularr:
            # Draw within visible range
            if ybb >= self.ypos and ybb < yyy:
                # Correct for tab
                line = self.text[ybb]
                #print("line:", line)
                xaa -= self.xpos;
                ybb -= self.ypos;
                lcc -= self.xpos
                xaa2 = calc_tabs(line, xaa, self.tabstop)
                lcc += xaa2 - xaa
                xaa = xaa2
                if xaa < 0:
                    xaa = 0
                self.draw_wiggle(cr,
                     xaa * self.cxx, ybb * self.cyy + self.cyy,
                            lcc * self.cxx, ybb * self.cyy + self.cyy)

    # --------------------------------------------------------------------
    # Paint main text

    def draw_maintext(self, cr):

        try:
            pedplug.display(self, cr)
        except:
            print("plugin failed", sys.exc_info())

        xx = 0; yy = 0;
        cnt = int(self.ypos)
        while cnt <  self.xlen:
            # Got fed up with tabs, generate an untabbed copy for drawing
            if self.hex or self.stab:
               text3 = self.text[cnt]
            else:
               text3 = untab_str(self.text[cnt], self.tabstop)

            #print( "'" + text3 + "'")
            # + int(self.strip // self.cxx
            text4 = text3[self.xpos:]

            # draw main
            dx, dy = self._draw_text(cr, xx, yy, text4, self.fgcolor)

            # Draw numeric left
            if self.strip:
                self._draw_text(cr, -self.strip + 2, yy, "%d" % cnt, self.fgcolorro, esc=True)

            cnt += 1
            #yy += dy
            yy += self.cyy

            if yy > self.hhh:
                break

# EOF