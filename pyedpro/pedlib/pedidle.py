#!/usr/bin/env python

# Global idle functions
import sys,re

from gi.repository import GLib

from pedlib import pedspell
from pedlib import  pedconfig

from pedlib.pedutil import *
from pedlib.keywords import *

__doc__ = ''' Idle routines and call backs '''

# Globals
last_scanned = None

# ---------------------------------------------------------------------

def _is_c_like(fname):

        ''' Return True if 'C' like file
            This is fooled by non extension items; not a big deal
            colors may get turned on ...
        '''
        #print("c like", self.fname)
        ret = False
        for aa in c_like_exts:
            eee = fname[-(len(aa)):]
            eee = eee.lower()
            #print("eee", eee, aa)
            if aa == eee:
                #print("C Match", self.fname)
                ret = True
                break
        return ret

def _scan_one(win, kwords, kwords2):

    sumw = [] ; sumnum = [] ; sumw2 = []
    try:
        regex = re.compile(kwords)
        for cnt, line in enumerate(win.text):
            res = regex.search(line)
            if res:
                sumw.append(line)
                sumnum.append(cnt)
    except:
        print("Exception in scan handler for", kwords, sys.exc_info())
        pass
    try:
        if kwords2:
            regex3 = re.compile(kwords2)
            for cnt, line in enumerate(win.text):
                res = regex3.search(line)
                if res:
                    sumw2.append("    " + line)
    except:
        print("Exception in scan handler2 for", kwords2, sys.exc_info())
        pass

    return sumw, sumnum

    #print("sumnum", sumnum)

def idle_callback2(self, arg):

    ''' Do Tasks2 when the system is idle '''

    #if "async" in pedconfig.conf.trace:
    #    print( "Idle callback2", arg)
    GLib.source_remove(self.source_id2)
    try:
        run_async_time(self, None)
    except:
        print("Exception in idle_callback2 handler", sys.exc_info())
        put_exception("idle_callback2")

def run_async_time(win, arg):

    '''  Run this on an idle callback so the user can work
            while this is going '''

    global last_scanned

    if  last_scanned == win:
        #print("Not rescanning", win.fname)
        return
    last_scanned = win
    win.mained.start_tree()
    if not win.text:
        return

    if "async" in pedconfig.conf.trace:
        print( "run_async_time", os.path.basename(win.fname), int(time.time()))

    sumw = [] ; sumnum = []
    if _is_c_like(win.fname):
        sumw, sumnum = _scan_one(win, ckeywords, ckeywords2)
    elif ".py" in win.fname[-3:]:
        sumw, sumnum = _scan_one(win, pykeywords2, pykeywords3)
    elif ".html" in win.fname[-5:]:
        sumw, sumnum = _scan_one(win, htmlkeywords, "")
    elif ".bas" in win.fname[-4:]:
        sumw, sumnum = _scan_one(win, htmlkeywords, "")
    elif ".s" in win.fname[-2:] or ".asm" in win.fname[-4:] or \
                ".inc" in win.fname[-4:]:
        sumw, sumnum = _scan_one(win, asmkeywords, asmkeywords2)
    elif ".v" in win.fname[-2:]:
        sumw, sumnum = _scan_one(win, vkeywords, vkeywords2)
    elif ".txt" in win.fname[-4:]:
        pass
    else:            # Default to 'C' like syntax
        try:
            for kw in sumkeywords:
                for line in win.text:
                    if line.find(kw) >= 0:
                        sumw.append(line)
        except:
            pass
        try:
            regex = re.compile(ckeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in async func handler", sys.exc_info())
            pass
    try:
        win.mained.update_treestore(sumw, sumnum)
    except:
        if pedconfig.conf.verbose > 2:
            # This is 'normal', ignore it
            print("exc run_async_time", sys.exc_info())
        pass

    #win.mained.update_statusbar("Rescan done.")

def keytime(self, arg):

    #if "async" in pedconfig.conf.trace:
    #    print( "keytime raw", time.ctime(), self.fired)
    #return

    walk_func(self)

    if self.fired ==  1:
        #print( "keytime", time.time(), self.fired)
        pedspell.spell(self, self.spellmode)

    if self.fired:
        self.fired -= 1

    # Track this buffer
    #if self.diffmode == 2:
    #    self.mained.diffpane.area.xpos = self.xpos
    #    self.mained.diffpane.area.ypos = self.ypos
    #    self.mained.diffpane.area.set_caret(self.xpos + self.caret[0],
    #                                                self.ypos + self.caret[1], True)

    # Track pane buffer back to diff components
    if self.diffpane:
        got_src = 0; got_targ = 0
        src = ""; targ = ""
        srctxt = [] ;  targtxt = []
        dst_tab = None ; src_tab = None

        # See if diff complete, put it in motion
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            if ppp.area.diffmode == 1:
                got_src = True
                src = os.path.basename(ppp.area.fname)
                srctxt = ppp.area.text
                src_tab = ppp
            elif ppp.area.diffmode == 2:
                got_targ = True
                targ = os.path.basename(ppp.area.fname)
                targtxt = ppp.area.text
                dst_tab = ppp

            cnt += 1

        yyy = self.ypos +  self.caret[1]
        zzz = self.ypos +  self.caret[1]
        txt = ""
        for aa in range( self.ypos + self.caret[1]):
            try:
                txt = self.text[aa]
            except:
                pass
            if txt[:8] == " --del--":
                yyy -= 1

            if txt[:8] == " --ins--":
                zzz -= 1
        if got_targ:
            dst_tab.area.xpos = self.xpos
            dst_tab.area.ypos = self.ypos
            dst_tab.area.set_caret(self.xpos + self.caret[0], yyy, True)
        if got_src:
            src_tab.area.xpos = self.xpos
            src_tab.area.ypos = self.ypos
            src_tab.area.set_caret(self.xpos + self.caret[0], zzz, True)

def idle_callback(self, arg):

    ''' Do Tasks  when the system is idle '''

    #if "async" in pedconfig.conf.trace:
    #    print( "Idle callback", self.fname)
    GLib.source_remove(self.source_id)

    if not self.changed:
        return
    try:
        # Mon 06.Sep.2021 always save
        hhh = hash_name(self.fname) + "_" + str(self.currback) + ".sav"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        err = writefile(xfile, self.text, "\n")
        if err[0]:
            strx = "Backed up file '{0:s}'".format(xfile)
            # Make a log entry
            logfile = pedconfig.conf.log_dir + os.sep + "backup.log"
            xentry = "Sav " + time.ctime() + " " + \
                self.fname + " " + os.path.basename(xfile) + "\n"
            writefile(logfile, (xentry, ""), "\n", "a+")
        else:
            strx = "Cannot back up file '{0:s}' {1:s}".format(xfile, err[1])

        self.mained.update_statusbar(strx)
    except:
        print("Exception in idle handler", sys.exc_info())

def _walk_one(self, sline, backstr, keywords, backstr2 = "" ):

    #print("_walk_one", sline, backstr)

    sumw2 = []
    try:
        beginx = 0 ; endd = 0
        regex = re.compile(backstr)
        # Walk back
        for aa in range(int(sline), 0, -1):
            line = self.text[aa]
            res = regex.search(line)
            if res:
                sumw2.append(line)
                beginx = aa
                break

        # Too far, look at function level instaed
        if (beginx == 0 or int(sline) - beginx > 100) and backstr2:
            regex = re.compile(backstr2)
            # Walk back
            for aa in range(int(sline), 0, -1):
                line = self.text[aa]
                res = regex.search(line)
                if res:
                    sumw2.append(line)
                    beginx = aa
                    break

        #print( "beginx", beginx, line, len(self.text))
        # Forward for boundary
        endd = len(self.text)
        for bb in range(beginx + 1, len(self.text)):
            line = self.text[bb]
            res = regex.search(line)
            if res:
                #sumw2.append(line)
                endd = bb - 1
                break
        #print("limits", beginx, endd)
        regex = re.compile(keywords)
        for cc in range(beginx + 1, endd - 1):
            line = self.text[cc]
            res = regex.search(line)
            if res:
                sumw2.append(line)
        #regex2 = re.compile(pykeywords2)
        #for dd in range(beginx + 1, endd - 1):
        #    line = self.text[dd]
        #    res = regex2.search(line)
        #    if res:
        #        sumw2.append(line)

    except:
        if pedconfig.conf.verbose > 2:
            #print("Exception in walk handler", sys.exc_info())
            put_exception("Walk handler")
        pass

    return sumw2

def walk_func(self):

    #if "async" in pedconfig.conf.trace:
    #    print( "walk func")
    #return

    if not self.text:
        return

    sumw2 = []
    sline = self.caret[1] + int(self.ypos)
    sline = max(sline, 0); sline = min(sline, len(self.text))

    # Walk back to last function
    if ".bas" in self.fname.lower()[-4:]:
        sumw2 = _walk_one(self, sline, basewalk, basekeywords)
    elif ".py" in self.fname.lower()[-3:]:
        #print("Search in:", self.fname)
        sumw2 = _walk_one(self, sline, pywalk, pykeywords4, "def ")
    elif ".asm" in self.fname.lower()[-4:] or  ".S" in self.fname.lower()[-2:] :
        sumw2 = _walk_one(self, sline, asmwalk, asmkeywords2)
    elif ".v" in self.fname.lower()[-4:]:
        sumw2 = _walk_one(self, sline, vwalk, vkeywords2)
    #elif _is_c_like(self.fname):
    #   sumw2 = _walk_one(self, sline, cwalk, ckeywords)
    else:
        # Default to 'C'
        sumw2 = _walk_one(self, sline, cwalk, ckeywords)
        #print("No function extraction", self.fname)

    # Always show todo
    got_todo = 0
    for line in self.text:
        if "TODO" in line:
            if not got_todo:
                got_todo = 1
                sumw2.append("----------- TODO List ----------")
            sumw2.append(line)

    try:
        self.mained.update_treestore2(sumw2)
    except:
        if pedconfig.conf.verbose > 2:
            # This is normal, ignore it
            print("walk2", sys.exc_info())
        pass

#  EOF
