#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import string, subprocess, os, platform, datetime, sys, codecs

from pedlib import  pedconfig
from pedlib import  pedofd
from pedlib import  pedync
from pedlib import  pedspell
from pedlib import  pedcolor
from pedlib import  pedlog
from pedlib import  pedfont
from pedlib import  pedundo
from pedlib import  pedtts
from pedlib import  pedmisc
from pedlib import  pedbuffs

from pedlib.keywords import *
from pedlib.pedutil import *
from pedlib.pedgoto import *
from pedlib.pedcanv import *

class ActHand2():

    def ctrl_alt_num(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - NUM", self2.lastkey)

    # Cleanse non ascii
    def ctrl_alt_a(self, self2):
        if pedconfig.conf.pgdebug > 4:
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
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - B")

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

        self2.undoarr.append((xidx, yidx, pedundo.MODIFIED, line))
        #print ("word / selection", line[cntb:cnte])

        wlow = line[cntb].upper()

        self2.text[yidx] = line[:cntb] + wlow + line[cntb+1:]
        self2.inval_line()

    #// Comment out code: TODO
    def ctrl_alt_c(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - C")

        extx = os.path.splitext(self2.fname)[1]
        #print("extx", extx)

        cumm = self._getsel(self2)
        strx = ""; strx2 = ""
        if cumm:
            self.ctrl_c(self2)
            # This will catch all known varieties, else .py assumed
            if extx == ".c" or extx == ".h" or extx == ".y" or extx == ".l":
                strx  = "#if 0\n"
                strx2 = "#endif\n"
            elif extx == ".asm" or extx == ".inc" or extx == ".S":
                strx  = "%if 0\n"
                strx2 = "%endif\n"
            elif extx == ".htm" or extx == ".html":
                #print("html comment")
                strx  = "<!-- "
                strx2 = " -->"
            else:
                strx  = "''' "
                strx2 = "''' "

            self.add_str(self2, strx)
            self.ctrl_v(self2)
            if strx2:
                self.add_str(self2, strx2)

        else:
            if extx == ".c" or extx == ".h" or extx == ".y" or extx == ".l":
                strx  = "//"
            elif extx == ".asm" or extx == ".inc" or extx == ".S":
                strx  = ";"
            elif extx == ".htm" or extx == ".html":
                strx  = "<!-- " ; strx2 = "-->"
                # Trailer attached to end of line
                xidx2 = self2.caret[0] + self2.xpos;
                yidx2 = self2.caret[1] + self2.ypos
                xlen = len(self2.text[yidx2])
                self2.set_caret(xlen, yidx2)
                self.add_str(self2, strx2)
                self2.set_caret(xidx2, yidx2)
            else:
                strx  = "#"

            self.add_str(self2, strx)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        xidx -= len(strx); yidx += 1
        self2.set_caret(xidx, yidx)
        self2.mained.update_statusbar("Selection commented out.")
        self2.invalidate()

    #// Start termnal
    def ctrl_alt_d(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - D")
        self2.mained.start_term()

    def ctrl_alt_e(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - E")
        pedmisc.exec_test(self2, "kb")

    def ctrl_alt_f(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - F")

        self2.mained.update_statusbar("Filling to column.")
        # Fill till column
        if  self2.shift:
            #self2.mained.update_statusbar("C-A-S 'F' Key pressed.")
            self2.mained.update_statusbar("Promt for fill to column")
            ttt = prompt_for_text(self2, "Enter column to fill to", str(self2.text_fillcol))
            if ttt:
                self2.text_fillcol = int(ttt);
        else:
            xidx = self2.caret[0] + self2.xpos;
            #print("Filling from", xidx, "to", self2.text_fillcol)
            if xidx < self2.text_fillcol:
                for aa in range(self2.text_fillcol - xidx):
                    event = Gdk.EventKey()
                    event.string  = " "
                    event.keyval = ord(" ")
                    self.add_key(self2, event)
            else:
                self2.mained.update_statusbar("Past filling point already.")

    def ctrl_alt_g(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - G")
        self2.mained.update_statusbar("Execute cycle")
        if  self2.shift:
            pass
        self2.mained.doall(None)

    def ctrl_alt_h(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - H")
        #pedfind.find(self, self2, True)
        self2.find(self, True)

    def ctrl_alt_i(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - I")

    def ctrl_alt_j(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - J")
        self2.coloring(not self2.colflag)
        if self2.colflag: strx = "on"
        else: strx = "off"
        self2.mained.update_statusbar("Coloring is %s." % strx)

    def ctrl_alt_k(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - K")
        self2.hexview(not self2.hex)

    def ctrl_alt_l(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - L")

    def ctrl_alt_m(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - M")

    def ctrl_alt_n(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - N")
        self2.uniview(not self2.uni)

    def ctrl_alt_r(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - R")
        #print("Read file on tts ");
        try:
            if not self2.tts:
                self2.tts = pedtts.tts(self2.mained.update_statusbar)

            self2.tts.read_tts(self2)
        except:
            print("No TTS", sys.exc_info())
            self2.mained.update_statusbar("No TTS installed")

    def ctrl_alt_t(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - T")
        self2.start_term()

    def ctrl_alt_r(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - R")
        self2.start_term()


    # // Deactivate comment TODO
    def ctrl_alt_v(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("CTRL - ALT - V ")

        #self2.mained.saveall()
        extx = os.path.splitext(self2.fname)[1]
        #print("extx", extx)
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        try:
            chh = self2.text[yidx][xidx]
            #print("chh", chh)
        except:
            chh = 0

        # This will catch all known varieties, else .py assumed
        if extx == ".c" or extx == ".h" or extx == ".y" or extx == ".l":
            if chh == "/":
                self.delete(self2)
                self.delete(self2)
            else:
                self2.mained.update_statusbar("Not on 'c' comment.")

        elif extx == ".asm" or extx == ".inc" or extx == ".S":
            if chh == ";":
                self.delete(self2)
            else:
                self2.mained.update_statusbar("Not on 'asm' comment.")

        elif extx == ".htm" or extx == ".html":
            #print("html comment strx  = <!-- -->";
            if chh == "<":
                self.delete(self2)
                self.delete(self2)
                self.delete(self2)
                self.delete(self2)
                xidx2 = self2.caret[0] + self2.xpos;
                yidx2 = self2.caret[1] + self2.ypos
                #self.end(self2)
                xlen = len(self2.text[yidx2])
                self2.set_caret(xlen, yidx2)
                self.bs(self2)
                self.bs(self2)
                self.bs(self2)
                self2.set_caret(xidx2, yidx2)
            else:
                self2.mained.update_statusbar("Not on comment character.")

        else:
            # Default comment
            if chh == "#":
                self.delete(self2)
            else:
                self2.mained.update_statusbar("Not on comment character.")

        # Goto next line
        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.set_caret(xidx, yidx + 1)

        #self.down(self2)


# ------------------------------------------------------------------

    def alt_a(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - A")
        self2.mained.saveall()

    def alt_b(self, self2):
        if pedconfig.conf.pgdebug > 4:
            printb ("ALT - B")

        pedbuffs.buffers(self, self2)

    def alt_c(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - C")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.xsel, self2.xsel2 = xidx, xidx + 1
        self2.ysel = self2.ysel2 = yidx
        self2.colsel = True
        self2.invalidate()

    def alt_d(self, self2):
        if pedconfig.conf.pgdebug > 4:
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
        self2.undoarr.append((xidx, yidx, pedundo.DELETED, self2.text[yidx]))

        del (self2.text[yidx])
        self2.mained.update_statusbar("Deleted line %d" % yidx)
        self2.invalidate()
        self2.set_changed(True)
        self2.src_changed = True

    def alt_e(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - E")
        pedconfig.conf.pedwin.openmenu("File")
        pass

    def alt_f(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - F")
        pedconfig.conf.pedwin.openmenu("File")
        pass

    def alt_g(self, self2):
        gotodlg(self2)

    def alt_h(self, self2):
        if  1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - H")

    def alt_i(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - I")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos;

        self2.undoarr.append((xidx, yidx, pedundo.NOOP, ""))

        cnt = 0; cnt2 = 0; found  = False;
        zlen = len(self2.text)
        while True:
            if cnt >= zlen: break
            line = self2.text[cnt];  xlen = len(line)
            if line.find("\t") >= 0:
                self2.undoarr.append((xidx, cnt, pedundo.MODIFIED + pedundo.CONTFLAG,
                                       self2.text[cnt]))
                line2 = untab_str(line, self2.tabstop)
                self2.text[cnt] = line2
                cnt2 += 1
            cnt += 1
        self2.mained.update_statusbar("Converted %d lines with tabs" % cnt2)

    def alt_j(self, self2):
        if pedconfig.conf.pgdebug > 4:
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
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - K")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.undoarr.append((xidx, yidx, pedundo.MODIFIED, self2.text[yidx]))
        line = self2.text[yidx]
        self2.text[yidx] = line[:xidx]
        self2.invalidate()
        self2.set_changed(True)

    def alt_l(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - L")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        self2.xsel = 0; self2.xsel2 = len(self2.text[yidx])
        self2.ysel = self2.ysel2 = yidx
        self2.inval_line()

    def alt_m(self, self2):
        if 1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - M")

    def alt_n(self, self2):
        if  1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - N")

    def alt_o(self, self2):

        # Test
        #pedync.message("\n   Testing    \n\n")

        # Simplified open
        fnames = pedofd.ofd("", self2)
        #print("openfile fnames", fnames)
        for fff in fnames:
            #print("Open", (fff))
            self2.mained.openfile(fff)
            pass

    def alt_p(self, self2):
        if  1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - P")

    def alt_q(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - Q")

        for mm in range(self2.notebook.get_n_pages()):
            vcurr = self2.notebook.get_nth_page(mm)
            vcurr.set_position(1)

        if self2.shift:
            self2.mained.hpaned.set_position(1)

    def alt_r(self, self2):
        if 1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - R")

    def alt_s(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - S")
        #pedfind.find(self, self2)
        self2.find(self)

    def alt_t(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - T")
        #pedfind.find(self, self2, True)
        self2.find(self, True)

    def alt_u(self, self2):
        if 1: #pedconfig.conf.pgdebug > 4:
            print ("ALT - U")

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
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - W")
        self2.save()

    def alt_x(self, self2):

        if pedconfig.conf.pgdebug > 4:
            print ("ALT- X -- Exit")
        self2.mained.activate_exit()

    def alt_y(self, self2):

        if pedconfig.conf.pgdebug > 4:
            print ("ALT- Y -- Compile")
        self2.check_syntax()

    def alt_z(self, self2):
        if pedconfig.conf.pgdebug > 4:
            print ("ALT - Z")

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos;
        self2.undoarr.append((xidx, yidx, pedundo.NOOP, ""))

        cnt = 0; cnt2 = 0; cnt3 = 0
        zlen = len(self2.text)
        while True:
            if cnt >= zlen: break
            line = self2.text[cnt];  xlen = len(line)

            if xlen > 78:
                cnt2 += 1
                # Delete this line from doc
                self2.undoarr.append((xidx, cnt, \
                                pedundo.DELETED + pedundo.CONTFLAG, line))
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
                        self2.undoarr.append((xidx, cnt, pedundo.ADDED + pedundo.CONTFLAG,
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
                    self2.undoarr.append((xidx, cnt, pedundo.ADDED + pedundo.CONTFLAG,
                                       ttt))
                    zlen += 1; cnt += 1; cnt3 += 1
            else:
                cnt += 1

        self2.invalidate()
        self2.set_changed(True)
        self2.mained.update_statusbar(\
            "Converted %d long lines to %d short lines" % (cnt2, cnt3))


# --------------------------------------------------------------------
    # Right CTRL

    # Catch all
    def rctrl_all(self, self2):
        if 1: #pedconfig.conf.pgdebug > 4:
            print ("RCTRL -- Captured str=", self2.curr_event.string,
                                            "keyval=", self2.curr_event.keyval)

    def rctrl_a(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.activate_notetab()

    def rctrl_c(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.activate_caltab()

    def rctrl_f(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.update_statusbar("Starting Thunar ...")
        self2.start_external(["thunar", "."],
                                        ["explorer", ""])
    def rctrl_h(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        #print("Add html comment")

        cumm = self._getsel(self2)
        strx  = "<!-- "; strx2 = " -->"
        if cumm:
            self.ctrl_c(self2)
            self.add_str(self2, strx)
            self.ctrl_v(self2)
            if strx2:
                self.add_str(self2, strx2)
        else:
            # Trailer attached to end of line
            xidx2 = self2.caret[0] + self2.xpos;
            yidx2 = self2.caret[1] + self2.ypos
            xlen = len(self2.text[yidx2])
            self2.set_caret(xlen, yidx2)
            self.add_str(self2, strx2)
            self2.set_caret(xidx2, yidx2)
            self.add_str(self2, strx)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        xidx -= len(strx); yidx += 1
        self2.set_caret(xidx, yidx)
        self2.mained.update_statusbar("Selection HTML comment added.")
        self2.invalidate()

    def rctrl_i(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        #print("Add 'C' comment")

        cumm = self._getsel(self2)
        strx  = "/* "; strx2 = " */"
        if cumm:
            self.ctrl_c(self2)
            self.add_str(self2, strx)
            self.ctrl_v(self2)
            if strx2:
                self.add_str(self2, strx2)
        else:
            # Trailer attached to end of line
            xidx2 = self2.caret[0] + self2.xpos;
            yidx2 = self2.caret[1] + self2.ypos
            xlen = len(self2.text[yidx2])
            self2.set_caret(xlen, yidx2)
            self.add_str(self2, strx2)
            self2.set_caret(xidx2, yidx2)
            self.add_str(self2, strx)

        xidx = self2.caret[0] + self2.xpos;
        yidx = self2.caret[1] + self2.ypos
        xidx -= len(strx); yidx += 1
        self2.set_caret(xidx, yidx)
        self2.mained.update_statusbar("Selection HTML comment added.")
        self2.invalidate()

    def rctrl_l(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.update_statusbar("Starting Libre Office ...")
        self2.start_external(["libreoffice", "--writer"],
                                        ["libreoffice", "--writer"])
    def rctrl_r(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.rescan()

    def rctrl_t(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.update_statusbar("Starting terminal ...")
        self2.mained.start_term()

    def rctrl_w(self, self2):
        if pedconfig.conf.pgdebug > 4:
             print ("RCTRL -- ", self2.curr_event.keyval)
        self2.mained.activate_webtab()

    def rctrl_num(self, self2):
        kkk = self2.curr_event.keyval - Gdk.KEY_0
        if 1: #pedconfig.conf.pgdebug > 4:
            print ("RCTRL -- num, key=", kkk)

# EOF
