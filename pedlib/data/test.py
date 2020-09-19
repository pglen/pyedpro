#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import string, subprocess, os, platform
import py_compile

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from . import pedync, pedofd, pedspell, pedbuffs, pedconfig

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
# Function name hints to key / action. like up() is key up, and the action

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
        #print ("ctrl_tab")
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










