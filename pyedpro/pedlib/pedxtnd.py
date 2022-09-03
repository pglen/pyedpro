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

from pedlib import pedconfig
from pedlib.keywords import *
from pedlib.pedutil import *

BOUNDLINE  = 80            # Boundary line for col 80 (the F12 func)

class pedxtnd(object):

    def __init__(self, self2):
        self.self2 = self2


