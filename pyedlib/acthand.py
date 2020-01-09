#!/usr/bin/env python

# Action Handler for the editor. Extracted to a separate module for
# easy update. These are the actions for pyedpro. You may define more
# and attach a key handler to it in the tables of keyhand.py

# Notes:
#
# a.) Navigation may be blind, the doc class will contain the cursor
#       within the document.
#
# b.) Some functions are sensitive to shift ctrl alt etc ...
    #       See the arrow key code [left()] how it is implemented to extend
#       selection.
#
# c.) Anatomy of key handler function:
#       shift pre - ctrl/alt handler - regular handler - shift post
#       This way the nav keys can select in their original function
#
# d.) Token completion. Tokens are kept in a stack 10 deep. If half of the
#       token is typed, the token complete will fill in the other half.
#       This is a very desirable behavior when writing code, as it feeds the
#       variable name to the text, essentially preventing var name mistype.
#       Because token completion has a short stack, it has a large
#       probability to fill in the var names from local scope.
#       If token completion filled in an unwanted string, backpedal to the
#       half point in the string and type as usual.
#       If the completion behavure is not desired, disable the code marked
#       "Token Completion"
#

from __future__ import absolute_import
from __future__ import print_function

import string, subprocess, os, platform, datetime
import py_compile

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from . import pedync, pedofd, pedspell, pedbuffs, pedconfig, pedtts

# Some action functions have their own file
#from pedfind import *
from . import pedfind
from .pedgoto import *
from .pedundo import *
from .keywords import *

# General set of utilities
from .pedutil import *

# ------------------------------------------------------------------------
# Action handler. Called from key handler.
# There is a function for most every key. Have at it.
# Function name hints to key / . like up() is key up, and the action

class ActHand:

    def __init__(self):
        self.was_home = 0
        self.was_end = 0

        self.clips = []
        for aa in range(10):
            self.clips.append("");
        self.currclip = 0;

    # -----------------------------------------------------------------------

    def ctrl_tab(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ctrl_tab")

        if self2.shift:
            self2.mained.prevwin()
        else:
            self2.mained.nextwin()

    def up(self, self2):
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        incr = 1
        if self2.alt:
            self.pgup(self2)
        elif self2.ctrl:
            incr = 10
        elif self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                self2.xsel2 = xidx + 1
            if self2.ysel == -1:
                self2.ysel = yidx

        self2.set_caret(xidx, yidx - incr)

        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            self2.invalidate()
        else:
            self2.clearsel()

    # --------------------------------------------------------------------

    def down(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        incr = 1
        if self2.ctrl:
            incr = 10
        elif self2.alt:
            self.pgdn(self2)
        elif self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                self2.xsel2 = xidx
                self2.colsel = False
            if self2.ysel == -1:
                self2.ysel = yidx

        self2.set_caret(xidx, yidx + incr)

        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            self2.invalidate()
        else:
            self2.clearsel()

    # --------------------------------------------------------------------

    def left(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                #self2.colsel = True
            if self2.ysel == -1:
                self2.ysel = yidx

        if self2.ctrl:
            line = self2.text[yidx]
            idx  = xprevchar(line, " ", self2.caret[0] - 1)
            idx2 = prevchar(line, " ", idx)
            idx3 = xprevchar(line, " ", idx2)
            if idx == -1:
                #print ("ctrl - L prev line")
                if yidx:
                    yidx -= 1
                    line = self2.text[yidx]
                    xidx = len(line)
                    idx = xprevchar(line, " ", xidx)
                    self2.set_caret(idx+1 , yidx)
            else:
                self2.set_caret(idx3+1, yidx)
            self2.invalidate()
        elif self2.alt:
            line = self2.text[yidx]
            # Only move ONE word
            try:
                if line[xidx-1] != " ":
                    begs, ends = selword(line, xidx-1)
                    self2.set_caret(begs, yidx)
            except:
                pass
        else:
            self2.set_caret(xidx - 1, yidx)

        # Extend selection
        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            if self2.ysel > self2.ysel2:
                self2.xsel = self2.caret[0] + self2.xpos
            else:
                self2.xsel2 = self2.caret[0] + self2.xpos
        else:
            self2.clearsel()

    # ---------------------------------------------------------------------

    def right(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                self2.colsel = False
            if self2.ysel == -1:
                self2.ysel = yidx

        if self2.ctrl:
            line = self2.text[yidx]
            idx = nextchar(line, " ", xidx)
            idx2 = xnextchar(line, " ", idx)
            #print (idx, idx2, len(line))
            # Jump to next line
            if idx2 == idx or idx2 == len(line):
                yidx += 1
                if yidx < len(self2.text):
                    self2.caret[0] = 0
                    line = self2.text[yidx]
                    idx2 = xnextchar(line, " ", 0)
                    self2.set_caret(idx2, yidx)
                    self2.invalidate()
            else:
                #print ("ctrl_right", idx2, yidx)
                self2.set_caret(idx2, yidx)
        elif self2.alt:
            line = self2.text[yidx]
            begs, ends = selword(line, xidx)
            self2.set_caret(ends, yidx)
        else:
            self2.set_caret(xidx + 1, yidx)

        # Extend selection
        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            if self2.ysel > self2.ysel2:
                self2.xsel = self2.caret[0] + self2.xpos
            else:
                self2.xsel2 = self2.caret[0] + self2.xpos
            self2.invalidate()
        else:
            self2.clearsel()

    # ---------------------------------------------------------------------
    # This handler is also used for:
    #
    #       o  addig new lines
    #       o  signaling for rescan
    #       o  signaling for rescan

    def ret(self, self2):
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self.pad_list(self2, yidx)
        line = self2.text[yidx][:]
        self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
        spaces = cntleadchar(line, " ")
        self2.text[yidx] = line[:xidx];
        # Insert new after current
        yidx += 1
        self2.undoarr.append((xidx, yidx, ADDED + CONTFLAG, \
                spaces + line[xidx:]))
        text = self2.text[:yidx]
        text.append(spaces + line[xidx:])
        text += self2.text[yidx:]
        self2.text = text
        self2.set_caret(len(spaces), yidx)

        # Signal the rest for ...
        for aa in sumkeywords:
            if line.find(aa) >= 0:
                self2.needscan = True

        # Contain undo
        limit_undo(self2)

        # Update maxlines
        mlines = len(self2.text)
        if mlines > self2.maxlines + 10:
            self2.set_maxlines(mlines)

        self2.set_changed(True)
        self2.src_changed = True
        self2.invalidate()

    def delete(self, self2):
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        # Delete selection
        if self2.xsel != -1:
            #print ("sel del")
            self.cut(self2, True)
        else:
            xlen = len(self2.text[yidx])
            if xlen:
                line = self2.text[yidx][:]
                if xidx >= xlen:     # bring in line from below
                    self2.undoarr.append((xidx, yidx, MODIFIED, \
                        self2.text[yidx]))
                    self2.text[yidx] += genstr(" ", xidx-xlen)
                    self2.text[yidx] += self2.text[yidx+1][:]
                    self2.undoarr.append((xidx, yidx+1, \
                        DELETED + CONTFLAG, self2.text[yidx+1]))
                    del (self2.text[yidx+1])
                    self2.invalidate()
                else:               # remove char
                    self2.undoarr.append((xidx, yidx, MODIFIED, \
                            self2.text[yidx]))
                    self2.text[yidx] = line[:xidx] + line[xidx+1:]
                    self2.set_caret(xidx, yidx)
                    self2.inval_line()
            else:
                del (self2.text[yidx])

        self2.xsel = -1
        self2.set_changed(True)
        self2.src_changed = True
        self2.invalidate()

    # --------------------------------------------------------------------

    def bs(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        # Delete selection
        if self2.xsel != -1:
            #print ("sel del")
            self.cut(self2, True)
            self2.xsel = -1
        else:
            if xidx > 0:
                line = self2.text[yidx][:]
                self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
                self2.text[yidx] = line[:xidx - 1] + line[xidx:]
                self2.set_caret(xidx - 1, yidx)
                self2.inval_line()
            else:                                   # Move line up
                if yidx > 0:
                    if yidx < len(self2.text):      # Any text?
                        self2.undoarr.append((xidx, yidx-1, \
                                MODIFIED, self2.text[yidx-1]))
                        line = self2.text[yidx][:]
                        lenx = len(self2.text[yidx-1])
                        self2.text[yidx-1] += line
                        self2.set_caret(lenx, yidx-1)
                        self2.undoarr.append(\
                                (xidx, yidx, DELETED + CONTFLAG, \
                                        self2.text[yidx]))
                        del (self2.text[yidx])
                        self2.invalidate()
                    else:                           # Just update cursor
                        self2.set_caret(xidx, yidx-1)

        self2.set_changed(True)
        self2.src_changed = True

    # --------------------------------------------------------------------

    def pgup(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                self2.colsel = False
            if self2.ysel == -1:
                self2.ysel = yidx

        if self2.alt:
            #print ("alt-pgup")
            self2.mained.nextwin()
        elif self2.ctrl:
            self2.set_caret(self2.caret[0], yidx - 2 * self2.pgup)
        else:
            self2.set_caret(self2.caret[0], yidx - self2.pgup)

        # Extend selection
        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            if self2.ysel > self2.ysel2:
                self2.xsel = self2.caret[0] + self2.xpos
            else:
                self2.xsel2 = self2.caret[0] + self2.xpos
            self2.invalidate()
        else:
            self2.clearsel()

    # --------------------------------------------------------------------

    def pgdn(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
                self2.colsel = False
            if self2.ysel == -1:
                self2.ysel = yidx

        if self2.alt:
            #print ("alt-pgdn")
            self2.mained.prevwin()
        elif self2.ctrl:
            self2.set_caret(self2.caret[0], yidx + 2 * self2.pgup)
        else:
            self2.set_caret(self2.caret[0], yidx + self2.pgup)

        # Extend selection
        if self2.shift:
            self2.ysel2 = self2.caret[1] + self2.ypos
            if self2.ysel > self2.ysel2:
                self2.xsel = self2.caret[0] + self2.xpos
            else:
                self2.xsel2 = self2.caret[0] + self2.xpos
            self2.invalidate()
        else:
            self2.clearsel()


    # --------------------------------------------------------------------

    def home(self, self2):

        xidx = self2.caret[0] + self2.xpos
        yidx = self2.caret[1] + self2.ypos
        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
            if self2.ysel == -1:
                self2.ysel = yidx
        if self2.alt:
            #print ("alt-home")
            self2.mained.firstwin()
        elif self2.ctrl:
            self2.set_caret(0, 0)
            self2.invalidate()
        else:
            self.was_home += 1
            if self.was_home == 1:
                self2.set_caret(0, yidx)
                self2.invalidate()
            if self.was_home == 2:
                self2.set_caret(0, yidx - self2.pgup)
                self2.invalidate()
            elif self.was_home == 3:
                #print ("bof")
                self2.set_caret(0, 0)
                self2.invalidate()
                self.was_home = 0

        if self2.shift:
            # End select
            self2.xsel2 = self2.caret[0] + self2.xpos
            self2.ysel2 = self2.caret[1] + self2.ypos
            self2.invalidate()
        else:
            self2.clearsel()
            self2.invalidate()

    # --------------------------------------------------------------------

    def end(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = xidx
            if self2.ysel == -1:
                self2.ysel = yidx
        if self2.alt:
            #print ("alt-end")
            self2.mained.lastwin()
        elif self2.ctrl:
            last = len(self2.text) - 1
            xlen = len(self2.text[last])
            self2.set_caret(xlen, last)
            self2.invalidate()
        elif self2.shift:
            # Begin select
            if self2.xsel == -1:
                self2.xsel = self2.caret[0]  + self2.xpos
            if self2.ysel == -1:
                self2.ysel = self2.caret[1]  + self2.ypos
            xlen = len(self2.text[yidx])
            self2.set_caret(xlen, self2.caret[1] + self2.ypos)
            self2.xsel2 = self2.caret[0] + self2.xpos
            self2.ysel2 = self2.caret[1] + self2.ypos
            self2.invalidate()
        else:
            self2.clearsel()
            self.was_end += 1
            if self.was_end == 2:
                #print ("eop")
                yidx += 20
                try:
                    xlen = len(self2.text[yidx])
                    self2.set_caret(xlen, yidx)
                    self2.invalidate()
                except:
                    pass

            elif self.was_end == 3:
                #print ("eof")
                last = len(self2.text) - 1
                xlen = len(self2.text[last])
                self2.set_caret(xlen, last)
                self2.invalidate()
                self.was_end = 0
            else:
                xlen = len(self2.text[yidx])
                self2.set_caret(xlen, yidx)

        if self2.shift:
            # End select
            self2.xsel2 = self2.caret[0] + self2.xpos
            self2.ysel2 = self2.caret[1] + self2.ypos
            self2.invalidate()
        else:
            self2.clearsel()
            self2.invalidate()

    # --------------------------------------------------------------------

    def esc(self, self2):

        self2.mained.update_statusbar("Esc")
        self2.clearsel()
        if pedconfig.conf.pgdebug > 9:
            print ("ESC")

        #print (pedync.yes_no_cancel("Escape", "This is a question" ))

    def ins(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("INS")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.insert = not self2.insert
        self2.set_caret(xidx, yidx)

    def ctrl_num(self, self2, num):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL -- ", num)

        self2.mained.update_statusbar("Switched to clipboard %d." % num)
        self.currclip = num
        #print ("current", self.clips[self.currclip])
        #for aa in range(len(self.clips)):
        #    print (aa, self.clips[aa])
        self2.invalidate()
        self2.update_bar2()

    def ctrl_1(self, self2):
        self.ctrl_num(self2, 1)

    def ctrl_2(self, self2):
        self.ctrl_num(self2, 2)

    def ctrl_3(self, self2):
        self.ctrl_num(self2, 3)

    def ctrl_4(self, self2):
        self.ctrl_num(self2, 4)

    def ctrl_5(self, self2):
        self.ctrl_num(self2, 5)

    def ctrl_6(self, self2):
        self.ctrl_num(self2, 6)

    def ctrl_7(self, self2):
        self.ctrl_num(self2, 7)

    def ctrl_8(self, self2):
        self.ctrl_num(self2, 8)

    # This sums all clipboards, puts it into 9
    def ctrl_9(self, self2):
        self.clips[9] = ""
        for aa in range(8):
            self.clips[9] += self.clips[aa]
        self.ctrl_num(self2, 9)

    def ctrl_0(self, self2):
        self.ctrl_num(self2, 0)

    def ctrl_a(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL -- A")

        self2.xsel = 0; self2.ysel = 0
        self2.ysel2 = len(self2.text)
        self2.xsel2 = self2.maxlinelen
        self2.set_caret(self2.maxlinelen,  len(self2.text))
        self2.invalidate()

    def ctrl_b(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL -- B")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        line = self2.text[yidx]
        bb, ee = selword(line, xidx)
        if bb != ee:
            self2.xsel = bb; self2.xsel2 =  ee
            self2.ysel = self2.ysel2 = yidx
            self2.gotoxy(self2.xsel2, self2.ysel)
        else:
            self2.mained.update_statusbar("Please navigate to word.")

        self2.invalidate()
        #self2.set_changed(True)

    # --------------------------------------------------------------------
    # Not many ctrl - alt handlers yet (reserved for gnome shortcuts)

    # Cleanse non ascii
    def ctrl_alt_a(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - A")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        line = self2.text[yidx]
        #print("line: (", line))
        newline = ""
        for aa in line:
            #print("%d" (% ord(aa)),)
            if ord(aa) < 128:
                newline += aa

        if line != newline:
            self2.text[yidx] = newline
            self2.mained.update_statusbar("Cleaned non ASCII characters.")
            self2.invalidate()
        pass

    def ctrl_alt_b(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - B")

        pass

    #// Deactivate code:
    def ctrl_alt_c(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - C")

        self.ctrl_c(self2)
        extx = os.path.splitext(self2.fname)[1]
        # This will catch all 'C' varieties, else py assumed
        if extx[1] == "c" or extx[1] == "h":
            strx  = "#if 0\n"
            strx2 = "#endif\n"
        else:
            strx  = "''' "
            strx2 = "''' "

        self.add_str(self2, strx)
        self.ctrl_v(self2)
        self.add_str(self2, strx2)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        xidx -= len(strx); yidx += 1
        self2.set_caret(xidx, yidx)
        self2.mained.update_statusbar("Selection commented out.")
        self2.invalidate()


    def ctrl_alt_h(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - H")

        pedfind.find(self, self2, True)

    def ctrl_alt_j(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - J")

        self2.coloring(not self2.colflag)
        if self2.colflag: strx = "on"
        else: strx = "off"
        self2.mained.update_statusbar("Coloring is %s." % strx)

    def ctrl_alt_k(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - K")

        self2.hexview(not self2.hex)

    def ctrl_alt_r(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - ALT - R")

        #print("Read file on tts ");
        if not self2.tts:
            self2.tts = pedtts.tts(self2.mained.update_statusbar)

        self2.tts.read_tts(self2)

     # --------------------------------------------------------------------

    def ctrl_c(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - C")

        if self2.xsel == -1 or  self2.ysel == -1:
            #self2.mained.update_statusbar("Nothing selected, copying line.")
            self2.mained.update_statusbar("Nothing selected, refuse to copy.")

            '''disp2 = Gdk.Display()
            disp = disp2.get_default()
            clip = Gtk.Clipboard.get_default(disp)

            xidx = self2.caret[0] + self2.xpos;
            yidx = self2.caret[1] + self2.ypos
            if self.currclip == 0:
                #print ("set clip:",  self2.text[yidx])
                clip.set_text(self2.text[yidx], len(self2.text[yidx]))
            self.clips[self.currclip] = self2.text[yidx]'''
            return

        # Normalize
        xssel = min(self2.xsel, self2.xsel2)
        xesel = max(self2.xsel, self2.xsel2)
        yssel = min(self2.ysel, self2.ysel2)
        yesel = max(self2.ysel, self2.ysel2)

        cnt = yssel; cnt2 = 0; cumm = ""
        while True:
            if cnt > yesel: break
            self.pad_list(self2, cnt)
            line = self2.text[cnt]
            if self2.colsel:
                frag = line[xssel:xesel]
            else :                                  # startsel - endsel
                if cnt == yssel and cnt == yesel:   # sel on the same line
                    frag = line[xssel:xesel]
                elif cnt == yssel:                  # start line
                    frag = line[xssel:]
                elif cnt == yesel:                  # end line
                    frag = line[:xesel]
                else:
                    frag = line[:]

            if cnt2: frag = "\n" + frag
            cumm += frag
            cnt += 1; cnt2 += 1

        #print ("clip:", cumm)
        #clip = Gtk.Clipboard()
        disp2 = Gdk.Display()
        disp = disp2.get_default()
        clip = Gtk.Clipboard.get_default(disp)

        if self.currclip == 0:
            if self2.shift:
                self2.mained.update_statusbar("Clipboard append only works on clip 1 - 7")
            else:
                self2.mained.update_statusbar("Clipboard copied.")
                clip.set_text(cumm, len(cumm))
        else:
            if self2.shift:
                self2.mained.update_statusbar("Clipboard %d appended." % self.currclip)
                self.clips[self.currclip] += cumm
            else:
                self2.mained.update_statusbar("Clipboard %d copied." % self.currclip)
                self.clips[self.currclip] = cumm

    def ctrl_d(self, self2):
        if self2.shift:
            dt = datetime.datetime(1990, 1, 1);
            dt2 = dt.now()
            strx2 =  dt2.strftime("%d/%m/%y %H:%M:%S ")
            self.add_str(self2, strx2)
        else:
            #print ("CTRL - D")
            xidx = self2.caret[0] + self2.xpos;
            cnt = 0; cnt2 = 0; zlen = len(self2.text)
            while True:
                if cnt >= zlen: break
                line = self2.text[cnt];  xlen = len(line)
                if xlen and line[xlen-1] == " ":
                    self2.undoarr.append((xidx, cnt, MODIFIED, self2.text[cnt]))
                    self2.text[cnt] = line.rstrip()
                    cnt2 += 1
                cnt += 1

            self2.mained.update_statusbar("Trimmed %d lines." % cnt2)

            if cnt2 > 0:
                self2.set_changed(True)

        self2.invalidate()

     # --------------------------------------------------------------------

    def ctrl_e(self, self2):

        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - E")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        line = self2.text[yidx]
        self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))

        cntb, cnte = selword(line, xidx)
        wlow = line[cntb:cnte].capitalize()
        #print ("word   '" + line[cntb:cnte] + "'", wlow)
        self2.text[yidx] = line[:cntb] + wlow + line[cnte:]
        self2.set_changed(True)
        self2.inval_line()

    def alt_f(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - F")
        pass

    def ctrl_f(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - F")

        pedfind.find(self, self2)

    def ctrl_h(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - H")

        self2.ctrl = False
        self2.alt = False
        self.left(self2)

    def ctrl_g(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - G")

        #self2.closedoc()
        if self2.shift:
            self.f5(self2)
        else:
            self.f6(self2)
        pass

    def ctrl_i(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - I")


        if self2.shift and self2.countup:
            self2.countup = 0
        else:
            strx = "%d" % self2.countup
            for aa in strx:
                #event = Gdk.Event(Gdk.EventType.KEY_PRESS);
                event = Gdk.EventKey()
                event.string  = aa
                event.keyval = ord(aa)
                self.add_key(self2, event)
            self2.countup += 1

    def ctrl_j(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - J")

        self2.ctrl = False
        self2.alt = False
        self.down(self2)

    def ctrl_k(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - K")

        self2.ctrl = False
        self2.alt = False
        self.up(self2)

    def ctrl_l(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - L")

        self2.ctrl = False
        self2.alt = False
        self.right(self2)

    def ctrl_m(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - M")

        self2.acorr = not self2.acorr
        if self2.acorr:
            self2.mained.update_statusbar(\
                "Autocorrect is on with %d enties." % len(acorr))
        else:
            self2.mained.update_statusbar("Autocorrect is off.")

    def ctrl_r(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - R")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        line = self2.text[yidx]
        self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))

        cntb, cnte = selword(line, xidx)
        if cntb == cnte:
              self2.mained.update_statusbar("Please nav to a word first.")
              return
        w1 = line[cntb:cnte]
        #print ("word1", w1)

        idx = xnextchar(line, " ", cnte)
        cntb2, cnte2 = selword(line, idx)
        if cntb2 == cnte2:
              self2.mained.update_statusbar("No second word on line.")
              return
        w2 = line[cntb2:cnte2]
        #print ("word2", w2)

        idx2 = xnextchar(line, " ", cnte2)
        cntb3, cnte3 = selword(line, idx2)
        if cntb3 == cnte3:
              self2.mained.update_statusbar("No third word on line.")
              return
        w3 = line[cntb3:cnte3]
        #print ("word3", w3)

        self2.text[yidx] = line[:cntb] + \
                w3 + " " + w2 + " " + w1 + line[cnte3:]
        self2.inval_line()

    # ---------------------------------------------------------------------

    def ctrl_t(self, self2):

        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - T")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        line = self2.text[yidx]

        if self2.shift:
            #print("Starting terminal from hotkey.");
            self2.start_term();
        else:
            self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))

            cntb, cnte = selword(line, xidx)
            if cntb == cnte:
                  self2.mained.update_statusbar("Please nav to a word first.")
                  return
            w1 = line[cntb:cnte]
            #print ("word1", w1)

            idx = xnextchar(line, " ", cnte)
            cntb2, cnte2 = selword(line, idx)
            if cntb2 == cnte2:
                  self2.mained.update_statusbar("No second word on line.")
                  return
            w2 = line[cntb2:cnte2]
            #print ("word2", w2)

            self2.text[yidx] = line[:cntb] + w2 + " " + w1 + line[cnte2:]
            self2.inval_line()

    # Uppercase stuff
    def ctrl_u(self, self2, lowit = False):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - U")

        #line = ""; xidx = 0; yidx = 0
        # No selection, assume word
        if self2.xsel == -1 or self2.ysel == -1:
            xidx = self2.caret[0] + self2.xpos
            yidx = self2.caret[1] + self2.ypos
            line = self2.text[yidx]
            #cntb, cnte = selword(line, xidx)
            cntb, cnte = selasci2(line, xidx, "_-")
        else:
            # Normalize
            xssel = min(self2.xsel, self2.xsel2)
            xesel = max(self2.xsel, self2.xsel2)
            yssel = min(self2.ysel, self2.ysel2)
            yesel = max(self2.ysel, self2.ysel2)

            xidx = xssel; yidx = yssel;
            line = self2.text[yidx]
            cntb = xssel; cnte = xesel

        if cnte == cntb:
            self2.mained.update_statusbar("Please nav to a word first.")
            return

        self2.undoarr.append((xidx, yidx, MODIFIED, line))
        #print ("word / selection", line[cntb:cnte])

        if self2.shift or lowit:
            wlow = line[cntb:cnte].lower()
        else:
            wlow = line[cntb:cnte].upper()

        self2.text[yidx] = line[:cntb] + wlow + line[cnte:]
        self2.inval_line()

    def ctrl_v(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - V")

        #clip = Gtk.Clipboard()
        disp2 = Gdk.Display()
        disp = disp2.get_default()
        clip = Gtk.Clipboard.get_default(disp)

        if self.currclip == 0:
            clip.request_text(self.clip_cb, self2)
        else:
            self.clip_cb(clip, self.clips[self.currclip],
                self2)

    # Pad line list to accomodate insert
    # We group this operation into change (no undo needed)
    def pad_list(self, self2, yidx):
         # Extend list to accomodate insert
        ylen = len(self2.text) - 1 # dealing with index vs len
        if yidx >= ylen:
            cnt = 0
            for aa in range(yidx - ylen):
                #self2.undoarr.append((0,  yidx + cnt, ADDED + CONTFLAG, ""))
                self2.text.append("")
                cnt += 1
            #self2.undoarr.append((0, yidx, NOOP, ""))

    # Pad line to accomodate insert
    def pad_line(self, self2, xidx, yidx):
        xlen = len(self2.text[yidx])
        if xidx >= xlen:
            #self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
            for aa in range(xidx - xlen):
                self2.text[yidx] += " "

    # Paste clipboard
    def clip_cb(self, clip, text, self2, boundary = True ):
        #print ("Clipboard: '" + text + "'", self2.caret[1], self2.ypos)
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        # Replace selection
        if self2.xsel != -1:
            #print ("sel replace")
            #self2.set_caret(self., yidx)
            self.cut(self2, True)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        cnt = yidx; cc = ""; ttt = str.split(text, "\n")

        if self2.colsel:
            if boundary:
                self2.undoarr.append((xidx, yidx, NOOP, ""))
            for aa in ttt:
                self.pad_list(self2, yidx)
                line = self2.text[yidx]
                self2.undoarr.append((xidx, yidx, MODIFIED  + CONTFLAG, \
                                 self2.text[yidx]))
                if xidx > len(line):        # pad line
                    line +=  genstr(" ", xidx - len(line))
                self2.text[yidx] = line[:xidx] + aa + line[xidx:]
                self2.gotoxy(xidx, yidx)
                yidx += 1
        else:
            if len(ttt) == 1:               # single line
                if boundary:
                   self2.undoarr.append((xidx, yidx, NOOP, ""))
                self.pad_list(self2, yidx)
                line = self2.text[int(yidx)]
                self2.undoarr.append((xidx, yidx, MODIFIED + CONTFLAG, self2.text[yidx]))
                if xidx > len(line):        # pad line
                    line +=  genstr(" ", xidx - len(line))
                self2.text[yidx] = line[:xidx] + ttt[0] + line[xidx:]
                self2.gotoxy(xidx+len(ttt[0]), yidx)
            else:
                if boundary:
                    self2.undoarr.append((xidx, yidx, NOOP, ""))
                for aa in ttt:
                    self.pad_list(self2, cnt)
                    if cnt == yidx :            # first line
                        line = self2.text[yidx]
                        if xidx > len(line):    # pad line
                            line += genstr(" ", xidx - len(line))
                        self2.undoarr.append((xidx, yidx, \
                            MODIFIED + CONTFLAG, self2.text[yidx]))
                        bb  =  line[:xidx] + aa
                        cc = line[xidx:]
                        self2.text[yidx] = bb
                    else:
                        self2.undoarr.append((xidx, cnt, ADDED + CONTFLAG,\
                                        self2.text[cnt]))
                        text2 = self2.text[:cnt]
                        text2.append(aa)
                        text2 += self2.text[cnt:]
                        self2.text = text2
                    cnt += 1
                #last line:
                self2.undoarr.append((xidx, cnt-1, MODIFIED + CONTFLAG,\
                     self2.text[cnt-1]))
                text2 = self2.text[cnt-1]
                self2.text[cnt-1] = text2 + cc
                self2.gotoxy(len(text2), yidx + len(ttt)-1)

        mlen = self2.calc_maxline()
        self2.set_maxlinelen(mlen, False)

        #self2.set_maxlines(len(self2.text), False)

        self2.set_changed(True)
        self2.src_changed = True
        self2.invalidate()

    # --------------------------------------------------------------------
    # Cut to clipboard

    def ctrl_x(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - X")

        self.cut(self2)

    def cut(self, self2, fake = False, boundary = True):
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if self2.xsel == -1 or  self2.ysel == -1:
            self2.mained.update_statusbar("Nothing selected")
            return

        if self2.colsel:
            # Normalize
            xssel = min(self2.xsel, self2.xsel2)
            xesel = max(self2.xsel, self2.xsel2)
            yssel = min(self2.ysel, self2.ysel2)
            yesel = max(self2.ysel, self2.ysel2)
        else:
            if self2.ysel < self2.ysel2:
                yssel = self2.ysel
                yesel = self2.ysel2
                xssel = self2.xsel
                xesel = self2.xsel2
            elif self2.ysel == self2.ysel2:
                yssel = self2.ysel
                yesel = self2.ysel2
                xssel = min(self2.xsel, self2.xsel2)
                xesel = max(self2.xsel, self2.xsel2)
            else:
                yssel = self2.ysel2
                yesel = self2.ysel
                xssel = self2.xsel2
                xesel = self2.xsel

        #print (xssel, xesel, yssel, yesel)

        #  undo (grouping stops)
        if boundary:
            self2.undoarr.append((xidx, yidx, NOOP, ""))

        cnt = yssel; cnt2 = 0; cumm = ""; darr = []
        while True:
            if cnt > yesel: break
            xidx = self2.caret[0] + self2.xpos
            #yidx = self2.caret[1] + self2.ypos
            self.pad_list(self2, cnt)
            line = self2.text[int(cnt)]
            if self2.colsel:
                self2.undoarr.append((xidx, cnt, \
                    MODIFIED + CONTFLAG, self2.text[int(cnt)]))
                frag = line[xssel:xesel]
                self2.text[int(cnt)] = line[:int(xssel)] + line[int(xesel):]
            else:
                self2.undoarr.append((xssel, cnt, \
                    MODIFIED + CONTFLAG, self2.text[int(cnt)]))
                if cnt == yssel and cnt == yesel:   # Selection on one line
                    frag = line[int(xssel):int(xesel)]
                    self2.text[int(cnt)] = line[:int(xssel)] + line[int(xesel):]
                    #if xssel == 0:
                    #    darr.append(cnt)
                elif cnt == yssel:                  # On start line
                    sline = cnt
                    frag = line[int(xssel):]
                    self2.text[int(cnt)] = line[:int(xssel)]
                    #if xssel == 0:
                    #    darr.append(int(cnt))
                elif cnt == yesel:                  # On end line
                    frag = line[:int(xesel)]
                    self2.text[int(sline)] = self2.text[int(sline)] + line[int(xesel):]
                    darr.append(cnt)
                else:                               # On selected line
                    frag = line[:]
                    #self2.text[cnt] = ""
                    darr.append(cnt)

            if cnt2: frag = "\n" + frag
            cumm += frag
            cnt += 1; cnt2 += 1

        #print ("clip x: '", cumm, "'")

        # Delete from the end to the beginning
        darr.reverse()
        for aa in darr:
            self2.undoarr.append((xidx, aa, \
                DELETED + CONTFLAG, self2.text[aa]))
            #print ("del", aa)
            del(self2.text[aa])

        self2.mained.update_statusbar("Cut %d lines" % (yesel - yssel))

        self2.clearsel()
        self2.gotoxy(xssel, yssel)

        # We use this for deleting as well, so fake clip op
        if not fake:
            #clip = Gtk.Clipboard()
            disp2 = Gdk.Display()
            disp = disp2.get_default()
            clip = Gtk.Clipboard.get_default(disp)

            if self.currclip == 0:
                clip.set_text(cumm, len(cumm))
            self.clips[self.currclip] = cumm

        self2.invalidate()
        self2.set_changed(True)
        self2.src_changed = True

    def ctrl_y(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - Y")

        redo(self2, self)

    def ctrl_z(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - Z")

        undo(self2, self)

    def ctrl_space(self, self2):
        self2.nokey = True
        if pedconfig.conf.pgdebug > 9:
            print ("CTRL - SP")

        self2.mained.update_statusbar("Keyboard disabled.")


    def alt_b(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - B")

        pedbuffs.buffers(self, self2)

    def alt_c(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - C")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.xsel, self2.xsel2 = xidx, xidx + 1
        self2.ysel = self2.ysel2 = yidx
        self2.colsel = True
        self2.invalidate()

    def alt_d(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - D")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        # After EOF, move to end
        if yidx >= len(self2.text):
            yidx = len(self2.text) - 1
            yidx = max(yidx, 0)
            self2.set_caret(xidx, yidx)

            # Refresh values
            xidx = self2.caret[0] + self2.xpos;
            yidx = self2.caret[1] + self2.ypos

        self.pad_list(self2, yidx)
        self2.undoarr.append((xidx, yidx, DELETED, self2.text[yidx]))

        del (self2.text[yidx])
        self2.mained.update_statusbar("Deleted line %d" % yidx)
        self2.invalidate()
        self2.set_changed(True)
        self2.src_changed = True

    def alt_i(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - I")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos;

        self2.undoarr.append((xidx, yidx, NOOP, ""))

        cnt = 0; cnt2 = 0; found  = False;
        zlen = len(self2.text)
        while True:
            if cnt >= zlen: break
            line = self2.text[cnt];  xlen = len(line)
            if line.find("\t") >= 0:
                self2.undoarr.append((xidx, cnt, MODIFIED + CONTFLAG,
                                       self2.text[cnt]))
                line2 = untab_str(line, self2.tabstop)
                self2.text[cnt] = line2
                cnt2 += 1
            cnt += 1
        self2.mained.update_statusbar("Converted %d lines with tabs" % cnt2)

    def alt_j(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - J")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos;

        cnt = yidx + 1; found  = False; zlen = len(self2.text)
        while True:
            if cnt >= zlen: break
            line = self2.text[cnt];  xlen = len(line)
            if xlen >= 80:
                self2.gotoxy(xlen, cnt)
                found = True
                break
            cnt += 1
        if found:
            self2.mained.update_statusbar("Jumped to line %d" % cnt)
        else:
            self2.mained.update_statusbar("No long lines found or at EOF")

    def alt_k(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - K")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
        line = self2.text[yidx]
        self2.text[yidx] = line[:xidx]
        self2.invalidate()
        self2.set_changed(True)

    def alt_l(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - L")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.xsel = 0; self2.xsel2 = len(self2.text[yidx])
        self2.ysel = self2.ysel2 = yidx
        self2.inval_line()

    def alt_o(self, self2):

        # Test
        #pedync.message("\n   Testing    \n\n")

        # Simplified open
        fnames = pedofd.ofd("", self2)
        for fff in fnames:
            #print("Open", (fff))
            self2.mained.openfile(fff)

    def alt_q(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - Q")

        for mm in range(self2.notebook.get_n_pages()):
            vcurr = self2.notebook.get_nth_page(mm)
            vcurr.set_position(1)

        if self2.shift:
            self2.mained.hpaned.set_position(1)

    def alt_s(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - T")

        pedfind.find(self, self2)

    def alt_t(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - T")

        pedfind.find(self, self2, True)

    def alt_v(self, self2):
        xidx = int(self2.caret[0] + self2.xpos)
        yidx = int(self2.caret[1] + self2.ypos)
        line = self2.text[yidx]
        #self2.xsel, self2.xsel2 = selasci2(line, xidx, "-_.[]")
        self2.xsel, self2.xsel2 = selasci2(line, xidx,"-_")
        self2.ysel = self2.ysel2 = yidx
        self2.gotoxy(self2.xsel2, self2.ysel)
        self2.inval_line()

    def alt_w(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - W")

        self2.save()

    def alt_z(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - Z")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos;
        self2.undoarr.append((xidx, yidx, NOOP, ""))

        cnt = 0; cnt2 = 0; cnt3 = 0
        zlen = len(self2.text)
        while True:
            if cnt >= zlen: break
            line = self2.text[cnt];  xlen = len(line)

            if xlen > 78:
                cnt2 += 1
                # Delete this line from doc
                self2.undoarr.append((xidx, cnt, \
                                DELETED + CONTFLAG, line))
                text = self2.text[:cnt] + self2.text[cnt+1:]
                self2.text = text
                zlen -= 1
                arr = line.split();  ttt = ""
                for aa in arr:
                    if len(ttt) + len(aa) > 75:
                        #print (ttt)
                        text = self2.text[:cnt]
                        text.append(ttt)
                        text += self2.text[cnt:]
                        self2.text = text
                        self2.undoarr.append((xidx, cnt, ADDED + CONTFLAG,
                                       ttt))
                        zlen += 1; cnt += 1; cnt3 += 1
                        ttt = aa + " "
                    else:
                        ttt += aa + " "
                if ttt:
                    #print (ttt)
                    text = self2.text[:cnt]
                    text.append(ttt)
                    text += self2.text[cnt:]
                    self2.text = text
                    self2.undoarr.append((xidx, cnt, ADDED + CONTFLAG,
                                       ttt))
                    zlen += 1; cnt += 1; cnt3 += 1
            else:
                cnt += 1

        self2.invalidate()
        self2.set_changed(True)
        self2.mained.update_statusbar(\
            "Converted %d long lines to %d short lines" % (cnt2, cnt3))

    def f1(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F1")

        if platform.system().find("Win") >= 0:
            pedync.message("\n   This feature is Linux only   \n\n"
                               "              ()")
        else:
            self2.mained.update_statusbar("Opening help file ...")
            try:
                ret = subprocess.Popen(["gnome-help",])
            except:
                pedync.message("\n   Cannot launch devhelp   \n\n"
                               "              (Please install)")
    def f2(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F2")

        if platform.system().find("Win") >= 0:
            pedync.message("\n   This feature is Linux only   \n\n"
                               "              ()")
        else:
            self2.mained.update_statusbar("Opening DEV help file ...")
            try:
                ret = subprocess.Popen(["devhelp",])
            except:
                pedync.message("\n   Cannot launch devhelp   \n\n"
                               "              (Please install)")
    def f3(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F3")

        self2.mained.update_statusbar("Opening KEYS help file ...")
        rr = get_exec_path("KEYS")
        launch_pangview(rr)

    def f4(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F4")

        self.play(self2, True)

    def f5(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F5")

        if len(self2.accum) == 0:
            self2.mained.update_statusbar(
                "Please specify a search string (Ctrl-F) or (Alt-S)")
            return

        self2.mained.update_statusbar("Locating previous match.")
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.search_again()
        cnt = len (self2.accum) - 1; match = False
        while True:
            if cnt < 0 : break
            xstr = self2.accum[cnt]

            try:
                bb = xstr.split(" ")[0].split(":")
            except: pass
            #print ("TREE sel", bb)
            # See if match on the same line
            if int(bb[1]) == yidx:
                if int(bb[0]) < xidx:
                    self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
                    match = True
                    break
            elif int(bb[1]) < yidx:
                self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
                match = True
                break

            cnt -= 1

        if not match:
            self2.mained.update_statusbar("At or before first match.")

    def f6(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F6")

        if len(self2.accum) == 0:
            self2.mained.update_statusbar(\
                "Please specify a search string (Ctrl-F) or (Alt-S)")
            return

        self2.mained.update_statusbar("Locating Next match.")
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        match = False

        self2.search_again()

        for xstr in self2.accum:
            # Get back numbers the python way
            try:
                bb = xstr.split(" ")[0].split(":")
            except: pass
            #-print ("TREE sel", bb)
            # See if match on the same line
            if int(bb[1]) == yidx:
                if int(bb[0]) > xidx:
                    self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
                    match = True
                    break
            elif int(bb[1]) > yidx:
                self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
                match = True
                break

        if not match:
            self2.mained.update_statusbar("At or after last match.")

    def f7(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F7")

        self.keyhand.reset()
        if self2.record:
            self2.record = False
            # Nothing recorded, restore old
            if self2.recarr == []:
                self2.mained.update_statusbar("Nothing recorded, resored old macro.")
                self2.recarr = self2.recarr2
                pedconfig.conf.recarr = self2.recarr[:]
            else:
                pedconfig.conf.recarr = self2.recarr[:]
                self2.mained.update_statusbar("Ended recording.")

        else:
            self2.mained.update_statusbar("Started recording ...")
            self2.recarr2 = self2.recarr
            self2.recarr = []
            self2.record = True
        self.keyhand.reset()

    # ---------------------------------------------------------------------

    def play(self, self2, anim = False):

        if self2.record:
            self2.mained.update_statusbar("Still recording, press F7 to stop")
            return True

        xlen = len(self2.recarr)
        if xlen == 0:
            # pull in global
            self2.recarr = pedconfig.conf.recarr[:]

        xlen = len(self2.recarr)
        if xlen == 0:
            self2.mained.update_statusbar("Nothing recorded, cannot play.")
            return True

        self.keyhand.reset()
        self2.mained.update_statusbar("Started Play ...")
        idx = 0
        while True:
            if idx >= xlen: break
            tt, kk, ss, www, sss, \
              self.keyhand.shift, self.keyhand.ctrl, \
                                self.keyhand.alt = self2.recarr[idx]
            idx += 1

            # Synthesize keystroke. We do not replicate state as
            # pyedpro maintains its own internally. (see keyhand.reset())

            ttt = Gdk.EventType.KEY_PRESS
            if tt == 9:
                ttt = Gdk.EventType.KEY_RELEASE

            #print ("playing macro", tt, kk, ss)
            event = Gdk.EventKey()
            event.type = ttt
            #event.time = time.clock() * 1000
            event.keyval = kk
            event.window = www
            event.string  = sss
            #print ("play event", event, event.type, event.keyval)

            self.keyhand.state2 = ss
            self.keyhand.handle_key2(self2, None, event)
            if anim:
                usleep(30)
            #print()
        # If the state gets out or sync ...
        self.keyhand.reset()
        self2.mained.update_statusbar("Ended Play.")

    def f8(self, self2, anim = False):
        if pedconfig.conf.pgdebug > 9:
            print ("F8")

        self.play(self2, anim)

    def f9(self, self2, flag = False):
        self2.spell = not self2.spell

        if pedconfig.conf.pgdebug > 9:
            print ("F9 spell", self2.spell)

        if self2.spell:
            ooo = "on."
            if self2.shift or flag:
                self2.spellmode = True; ppp = "Mode: text"
            else:
                self2.spellmode = False; ppp = "Mode: code"
        else:
            ooo = "off."; ppp = ""

        self2.mained.update_statusbar("Spell checking is %s %s" % (ooo, ppp))
        pedspell.spell(self2, self2.spellmode)

    # This will not be called, as it activates menu
    def f10(self, self2):
        if self2.shift:
            #print ("shift F10")
            pass
        if self2.ctrl:
            #print ("ctrl F10")
            pass

    def f11(self, self2):
        if self2.mained.full:
            self2.mained.mywin.unfullscreen()
            self2.mained.full = False
        else:
            self2.mained.mywin.fullscreen()
            self2.mained.full = True
        if pedconfig.conf.pgdebug > 9:
            print ("F11")


    def f12(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("F12")

        pass

    # ---------------------------------------------------------------------
    # Add synthesized str

    def add_str(self, self2, strx):

        for aa in strx:
            if aa == '\n':
                self.ret(self2)
            else:
                #event = Gdk.Event(Gdk.EventType.KEY_PRESS);
                event = Gdk.EventKey()
                event.string  = aa
                event.keyval = ord(aa)
                self.add_key(self2, event)

    #-------------------------------------------------------------------
    # Add regular key

    def add_key(self, self2, event):

        # CR / LF still haunts us, ignore CR
        if event.keyval == Gdk.KEY_Return:
            #print ("Ignoring Ctrl-Return")
            return

        if self2.readonly:
            self2.mained.update_statusbar("This buffer is read only.")
            return

        if self2.hex:
            self2.mained.update_statusbar("Cannot edit in hex mode.")
            return

        # Replace selection
        if self2.xsel != -1:
            #print ("sel replace")
            #self2.set_caret(self., yidx)
            self.cut(self2, True)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        # Extend list to accomodate insert
        self.pad_list(self2, yidx)
        # Pad string to accomodate insert
        self.pad_line(self2, xidx, yidx)

        line2 = self2.text[yidx][:]
        #xidx2 = decalc_tabs(line2, self2.caret[0] + self2.xpos, self2.tabstop);
        #print ("before/after", xidx, xidx2, event.string)

        ccc = ""
        try:
            if event.string != "":
                ccc = event.string
            else:
                ccc = chr(event.keyval)

            self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
            # Replace selection
            if self2.xsel != -1:
                #print ("sel replace")
                self.ctrl_x(self2, True)
                line2 = self2.text[yidx][:]

            if self2.insert:
                self2.text[yidx] = line2[:xidx] + ccc + line2[xidx:]
            else:
                self2.text[yidx] = line2[:xidx] + ccc + line2[xidx+1:]

            mlen = len(self2.text[yidx])
            if  mlen > self2.maxlinelen:
                self2.set_maxlinelen(mlen)

            #self2.set_caret(calc_tabs(self2.text[yidx], xidx + 1), yidx)
            self2.set_caret(xidx + 1, yidx)

            if self2.acorr:
                # See if autocorrect is needed
                for acs, acs2 in acorr:
                    lendiff = len(acs2) - len(acs)
                    ss = self2.text[yidx][xidx-(len(acs)-1):xidx+1]
                    if ss == acs:
                        xstr =  "Autocorrected to "'"%s"'"" % acs2
                        self2.mained.update_statusbar(xstr)
                        line = self2.text[yidx]
                        self2.text[yidx] = line[:xidx-(len(acs)-1)] + \
                                            acs2 + line[xidx+1:]
                        #self2.set_caret(calc_tabs(self2.text[yidx], \
                        #    xidx + lendiff, sel2.tabstop), yidx)
                        self2.set_caret(xidx + lendiff + 1, yidx)

            ''' # See if token is complete
            if ccc == " ":
                line = self2.text[yidx]
                begs, ends = selword(line, xidx - 1)
                if ends - begs >= 4:
                    #print ("token complete", line[begs:ends])
                    # Limit size of token stack
                    if len(self2.tokens) > 10:
                        del(self2.tokens[0])
                    self2.tokens.append(line[begs:ends])
                    #print (self2.tokens)

            # See if token completion is needed
            line = self2.text[yidx]
            idx = prevchar(line, " ", xidx - 1)
            word = line[idx+1:xidx+1]
            #print ("word", word)
            for aa in self2.tokens:
                lendiff = len(aa) - len(word)
                #print ("src",  aa[:len(aa) / 2])
                if aa[:len(aa) / 2] == word:
                    #print ("completion", aa)
                    self2.text[yidx] = line[:idx+1] + aa + line[xidx+1:]
                    tmp = calc_tabs(self2.text[yidx], xidx + lendiff, self2.tabstop)
                    self2.set_caret(tmp, yidx)
                    xstr =  "Autocompleted to "'"%s"'"" % aa
                    self2.mained.update_statusbar(xstr)'''

            ''' # See if spell checking needed
            if ccc == " ":
                #err = pedspell.spell_line(line, 0, len(line))
                #self2.ularr = []
                #for ss, ee in err:
                #    self2.ularr.append((ss, yidx, ee))
                self2.invalidate()    '''

            self2.inval_line()
            self2.set_changed(True)
            self2.src_changed = True

        except:
            # Could not convert it to character, alert user
            # Usualy unhandled control, so helps developmet
            #print  ("Other key", sys.exc_info(), event.keyval)
            if(pedconfig.conf.verbose):
                print("Other key", event.keyval, \
                    hex(event.keyval), hex(event.state))
            pass
        return True

    def alt_a(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT - A")

        self2.mained.saveall()

    def alt_g(self, self2):
        gotodlg(self2)

    def alt_y(self, self2):
        if pedconfig.conf.pgdebug > 9:
            print ("ALT- Y -- Compile")

        writefile("tmp", self2.text, "\n")
        try:
           py_compile.compile('tmp', doraise = True)
        except py_compile.PyCompileError as msg:

            self2.mained.update_statusbar("Syntax error.")

            if sys.version_info.major < 3:
                try:
                    ln  = msg[2][1][1]; col = msg[2][1][2]
                    mmm = "\n" + msg[2][0] + "\n\n    Ln: " +  str(ln) + " Col: " + str(col)
                    self2.gotoxy(col - 1, ln - 1)
                    pedync.message("    " + mmm + "    ", msg[1])
                except:
                    pedync.message(" " + str(msg) + "  ", "Syntax Error")
                    #print("line", msg);
                    pass
            else:
                    print("Error on compile: '", msg.args, "'")
                    zzz = str(msg.args[2]).split("(")
                    sss = zzz[1].split()[2].replace(")", "")
                    #print ("sss", sss)
                    self2.gotoxy(10, int(sss) - 1)
                    pedync.message("    " + str(msg) + "    ")

        except:
            print(sys.exc_info())
        else:
            pedync.message("\n  Syntax OK   \n")
            self2.mained.update_statusbar("Syntax OK.")
        finally:
            os.remove("tmp")

            #print ("com", sys.exc_info())

    # --------------------------------------------------------------
    # Tab handle is awkward. The regular key tab will insert
    # spaces to the next multiple of four.
    # To insert a real tab, use shift tab  (like for Makefiles)

    def tab(self, self2):

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos

        if pedconfig.conf.pgdebug > 9:
            print ("TAB", self2.shift)

        #tabstop = 4
        tabstop = self2.tabstop
        self.pad_list(self2, yidx)

        # No Selection, do tab
        if self2.ysel == -1:
            self2.undoarr.append((xidx, yidx, MODIFIED, self2.text[yidx]))
            if self2.shift:
                line2 = self2.text[yidx][:]
                self2.text[yidx] = line2[:xidx] + "\t" + line2[xidx:]
                spaces = self2.tabstop - (xidx % self2.tabstop)
                self2.set_caret(xidx+1, yidx)

                #print ("shif tab", spaces)
                #self2.set_caret(xidx + tabstop, yidx)
            else:
                spaces = tabstop - (xidx % tabstop)
                while spaces:
                    #event = Gdk.Event(Gdk.EventType.KEY_PRESS);
                    event = Gdk.EventKey()
                    event.string  = " "
                    event.keyval = ord(" ")
                    self.add_key(self2, event)
                    spaces -= 1
            self2.invalidate()
        else:
            # Indent, normalize
            yssel = min(self2.ysel, self2.ysel2)
            yesel = max(self2.ysel, self2.ysel2)
            #print ("TAB in sel")
            cnt = yssel
            self2.undoarr.append((xidx, yidx, NOOP, ""))
            if self2.shift:
                while True:
                    if cnt > yesel: break
                    self2.undoarr.append((xidx, cnt, \
                            MODIFIED | CONTFLAG, self2.text[cnt]))
                    self2.text[cnt] =  rmlspace(self2.text[cnt], 4)
                    cnt += 1
            else:
                while True:
                    if cnt > yesel: break
                    self2.undoarr.append((xidx, cnt, \
                        MODIFIED | CONTFLAG, self2.text[cnt]))
                    self2.text[cnt] = "    " + self2.text[cnt]
                    cnt += 1
            self2.invalidate()

# EOF



















