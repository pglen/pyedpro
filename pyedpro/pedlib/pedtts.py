#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from pedlib import  pedconfig

from pedlib.pedutil import *

# Set this to non zero if you want festival to speak
USE_FESTIVAL = 1
# Otherwise it calls espeak

# -----------------------------------------------------------------------
# Call func with all processes, func called with stat as its argument
# Function may return True to stop iteration

def withps(func, opt = None):
    ret = False
    dl = os.listdir("/proc")
    for aa in dl:
        fname = "/proc/" + aa + "/stat"
        try:
            if os.path.isfile(fname):
                fd = open(fname, "r")
                ff = fd.read().split()
                ret = func(ff, opt)
                fd.close()
            if ret:
                break
        except:
            pass
    return ret

# ------------------------------------------------------------------------
# Create it with status bar text setter

class tts():

    def __init__(self, prog = None):
        self.stopspeak = False
        self.haltspeak = False
        self.speech_pid = None
        self.prog_set_text = prog
        self.prog_set_text("Inited TTS")

    # Create a file, send it to festival
    def _speak(self, cstr):

        self.stopspeak = False
        fname = pedconfig.conf.data_dir + "/festival.txt"

        try:
            fh = open(fname, "w")
            fh.write(cstr)
        except:
            put_exception("Cannot create festival file")
            return
        finally:
            fh.close()
        try:
            if USE_FESTIVAL:
                self.speech_pid = subprocess.Popen(["festival", "--tts", fname])
            else:
                # This is more configurable, add option as it is displayed below.
                #self.speech_pid = subprocess.Popen(["espeak", "-f", fname, "-s", "100"])
                #self.speech_pid = subprocess.Popen(["espeak", "-f", fname, "-v", "english-us"])
                self.speech_pid = subprocess.Popen(["espeak-ng", "-f", fname,])
        except:
            print ("Cannot start TTS espeak-ng", sys.exc_info())
            return

        #print ("started", self.speech_pid.pid)
        GLib.timeout_add(100, self.check_speak)
        return True

    def check_speak2(self, ss, opt):
        if self.speech_pid:
            if  self.speech_pid.pid == int(ss[0]):
                # Zombie does not count:
                if ss[2] != "Z":
                    return True

    # Wait for speech to end (sync)
    def   wait_done(self):

        while True:
            if self.stopspeak:
                break
            if self.haltspeak:
                return
            if not self.speech_pid:
                break
            usleep(100)

        self.stopspeak = False

    # Timer to see if the speaker has terminated
    def check_speak(self):
        # If found, the search returns True
        ret = withps(self.check_speak2)
        if not ret:
            self.speech_pid = None
        else:
            # Look for termination again
            GLib.timeout_add(1000, self.check_speak)

    # --------------------------------------------------------------------
    # Stop tts instances, kill (all) children
    # Start speak

    def read_tts(self, self2, butt = None):

        # Running?

        if self.haltspeak and self.speech_pid:
            return

        self.haltspeak = True
        self.prog_set_text("Stopping TTS processes (please wait)")
        usleep(100)
        if self.speech_pid:
            self.stop_tts()
            return

        self.haltspeak = False
        self.stopspeak = False
        self.prog_set_text("Started Reading")

        #self._speak("Started reading"); self.wait_done()
        #print("After start")

        if self2.xsel == -1 or self2.ysel == -1:
            self2.mained.update_statusbar("Nothing selected")
            #self._speak("Nothing selected")

            # Speak from current point
            #xxx = self2.xpos + self2.caret[0]

            # Speak from current line
            xxx = 0
            yyy = self2.ypos + self2.caret[1]

            # Collect until dot - repeat
            sss = ""

            self2.xsel = xxx; self2.ysel = yyy;

            for yy in range(len(self2.text) - yyy):
                yy2 = yyy + yy
                ttt = self2.text[yy2]
                if "." in ttt:
                    idx = ttt.find(".") + 1  # point after dot
                    sss += ttt[:idx]

                    self2.xsel2 = idx; self2.ysel2 = yy2;
                    self2.gotoxy(self2.xsel2, self2.ysel2, None, True)
                    self2.invalidate()

                    #print("line %d: '%s'" % (yy, sss))
                    self.prog_set_text("Reading at line %d" % (yy2))
                    if not self._speak(sss):
                        self2.mained.update_statusbar("TTS cannot start (installed?)")
                        break

                    self.wait_done()

                    self2.xsel = idx; self2.ysel = yy2;
                    self2.invalidate()
                    sss = ttt[idx:] + " "
                else:
                    sss += ttt + " "

                if  self.haltspeak:
                    break
            return

        # Normalize
        xssel = min(self2.xsel, self2.xsel2)
        xesel = max(self2.xsel, self2.xsel2)
        yssel = min(self2.ysel, self2.ysel2)
        yesel = max(self2.ysel, self2.ysel2)

        cnt = yssel; cnt2 = 0; cumm = ""

        while True:
            if cnt > yesel: break
            #self.pad_list(self2, cnt)

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

        print ("clip:", cumm)
        self._speak(cumm)

    def stop_tts2(self, ss, opt):
        #print ( "stop_tts2", ss[1])
        if USE_FESTIVAL:
            if ss[1] == "(audsp)":
                #print ("killing", ss)
                os.kill(int(ss[0]), signal.SIGKILL)
        else:
            if ss[1] == "(espeak)":
                #print ("killing", ss)
                os.kill(int(ss[0]), signal.SIGKILL)

    def stop_tts(self):
        self.stopspeak = True
        self.prog_set_text("Stopped Reading")
        try:
            withps(self.stop_tts2)
        except:
            put_exception("Cannot kill")
            #self.speech_pid.pid

        self.speech_pid = None

# EOF




