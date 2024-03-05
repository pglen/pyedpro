#!/usr/bin/env python3

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

HEADSIZE = 512
RECSIZE  = 32
CURROFFSET = 8

# This was an attempt to use bytearray -- not working clean

class DbCore():

    def __init__(self, fname):

        #print("initializing core with", fname)

        raise  RuntimeError("Obsolete implemtation.")

        self.dirty      = 0
        self.dirty_end  = 0

        self.buffer = bytearray(RECSIZE)

        try:
            self.fp = open(fname, "rb+")
        except:
            try:
                self.fp = open(fname, "wb+")
            except:
                print("Cannot open /create ", fname)
                self.fp = None

        self.head = bytearray(self.fp.read(HEADSIZE))
        #print("self.head", self.head)

        # Initial file creation
        if len(self.head) < HEADSIZE:
            print("initial padding")
            self.head = bytearray(HEADSIZE)
            self.head[0] = ord('P');   self.head[1] = ord('Y')
            self.head[2] = ord('D');   self.head[3] = ord('B')

            self.head[HEADSIZE - 1] = ord('P');  self.head[HEADSIZE - 2] = ord('Y')
            self.head[HEADSIZE - 3] = ord('D');  self.head[HEADSIZE - 4] = ord('B')

            self.putint(4, 0xaabbccdd)
            self.fp.write(self.head)
            self.fp.seek(0)
            self.head = bytearray(self.fp.read(HEADSIZE))

            nnn = self.getint(4)
            print("nnn", hex(nnn))

        #print("Got sig", buff[0:4])

    def putint(self, offs, num):
        self.head[offs:offs+4] =              \
            num >> 24 & 0xff,                 \
                num >> 16 & 0xff,             \
                    num >> 8 & 0xff,          \
                        num & 0xff

    def getint(self, offs):
        val = self.head[offs] << 24 |         \
                self.head[offs+1] << 16 |     \
                    self.head[offs+2] << 8 |  \
                        self.head[offs+3]
        return val

    def  save_data(self, arg2, arg3):
        curr = self.getint(CURROFFSET)
        print("args", arg2, arg3, "offset =", curr)
        curr += len(arg2) + len(arg3)
        self.putint(CURROFFSET, curr)
        print("curr", curr)

        buff = bytearray(RECSIZE)
        buff[0:4] = 0x1, 0x2, 0x3, 0x4
        for aa in range(len(arg2)):
          buff[4+aa] = ord(arg2[aa:aa+1])

        for aa in range(len(arg3)):
          buff[4+aa] = ord(arg3[aa:aa+1])

        print("buff", buff)

        # Save head
        self.fp.seek(0)
        self.fp.write(self.head)

        #self.fp.seek(HEADSIZE)
        self.fp.write(self.buffer)



# EOF