#!/usr/bin/env python3

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, warnings

import struct, io


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

DIRTY_MAX   = 0xffffffff

# Must be less than (512 - (32 + 16)) / 8  = 58
HASH_LIM    = 10

# Must be less than (4096 - 512) / 8  = 448
DATA_LIM    = 10

INTSIZE     = 4
HEADSIZE    = 512
RECSIZE     = 32
JUMPSIZE    = 4096

CURROFFSET  = 16
CURRHASH    = 20
LINKHASH    = 24
LINKDATA    = 28
FIRSTHASH   = 32

FILESIG     = b"PYDB"
RECSIG      = b"RECB"
RECSEP      = b"RECS"
RECEND      = b"RECE"

# ------------------------------------------------------------------------
#

class DbCore():

    def __init__(self, fname):

        #print("initializing core with", fname)

        self.hdirty      = DIRTY_MAX
        self.hdirty_end  = 0

        self.dirty      = DIRTY_MAX
        self.dirty_end  = 0

        self.dirtyarr = []

        try:
            self.fp = open(fname, "rb+")
        except:
            try:
                self.fp = open(fname, "wb+")
            except:
                print("Cannot open /create ", fname)
                self.fp = None

        self.head = io.BytesIO(self.fp.read(HEADSIZE))
        self.buffer = io.BytesIO(self.fp.read())

        #print("self.head", dir(self.head))
        headsize = self.getsize(self.head)
        buffsize = self.getsize(self.buffer)
        #print("headsize", headsize, "buffsize", buffsize)

        # Initial file creation
        if headsize < HEADSIZE:
            #print("initial padding")
            self.head.write(bytearray(HEADSIZE))

            self.head.seek(0)
            self.head.write(FILESIG)
            self.head.write(struct.pack("I", 0xaabbccdd))
            self.head.write(struct.pack("B", 0xaa))
            self.head.write(struct.pack("B", 0xbb))
            self.head.write(struct.pack("B", 0xcc))
            self.head.write(struct.pack("B", 0xff))

            self.head.seek(HEADSIZE-4)
            self.head.write(FILESIG)

            # To the file as well
            self.fp.seek(0)
            self.fp.write(self.head.getbuffer())
            self.fp.seek(0)

        # help on memoryview
        buff = self.head.getbuffer()
        #print("Got sig", self.head.getvalue()[0:4], bytes(buff[0:4]))
        if  self.head.getvalue()[0:4] != FILESIG:
            #print("Invalid data signature")
            raise  RuntimeError("Invalid database signature.")

    # Deliver a 32 bit hash of whatever
    def hash32(self, strx):

        lenx = len(strx);  hashx = int(0)
        for aa in strx:
            bb = ord(aa)
            hashx +=  int((bb << 12) + bb)
            hashx &= 0xffffffff
            hashx = int(hashx << 8) + int(hashx >> 8)
            hashx &= 0xffffffff

        return hashx

    def getsize(self, buffio):
        pos = buffio.tell()
        endd = buffio.seek(0, io.SEEK_END)
        buffio.seek(pos, io.SEEK_SET)
        return endd

    def getint(self, offs):
        self.head.seek(offs, io.SEEK_SET)
        val = self.head.read(4)
        ss = struct.unpack("I", val)
        #print("up", ss)
        return ss[0]

    def putint(self, offs, val):
        #print("putint", offs, val)
        self.head.seek(offs, io.SEEK_SET)
        pp = struct.pack("I", val)
        #print("pp", pp)
        self.hwrite(pp)

    def puthash_offs(self, offs, curr, hash):
        self.buffer.seek(offs, io.SEEK_SET)
        cc = struct.pack("I", curr)
        self.xwrite(cc)
        hh = struct.pack("I", hash)
        self.xwrite(hh)

    def gethash_offs(self, offs):
        self.buffer.seek(offs, io.SEEK_SET)
        val = self.buffer.read(4)
        curr = struct.unpack("I", val)
        val2 = self.buffer.read(4)
        hash = struct.unpack("I", val2)
        return (curr[0], hash[0])

    def getbuffint(self, offs):
        self.buffer.seek(offs, io.SEEK_SET)
        val = self.buffer.read(4)
        return struct.unpack("I", val)[0]

    def getbuffshort(self, offs):
        self.buffer.seek(offs, io.SEEK_SET)
        val = self.buffer.read(2)
        return struct.unpack("H", val)[0]

    def getbuffstr(self, offs, xlen):
        self.buffer.seek(offs, io.SEEK_SET)
        val = self.buffer.read(xlen)
        return val

    # Mark dirty automatically
    def  xwrite(self, var):
        bb = self.buffer.tell()
        if self.dirty > bb:
            self.dirty = bb

        self.buffer.write(var)
        ee = self.buffer.tell()
        if self.dirty_end < ee:
            self.dirty_end = ee

        self.dirtyarr.append((bb, ee))

    # Header: Mark dirty automatically
    def  hwrite(self, var):
        bb = self.head.tell()
        if self.hdirty > bb:
            self.hdirty = bb

        self.head.write(var)
        ee = self.head.tell()
        if self.hdirty_end < ee:
            self.hdirty_end = ee

    def  dump_rec(self, rec):

        #sig = self.getbuffint(rec)

        sig = self.getbuffstr(rec, INTSIZE)
        if sig != RECSIG:
            print("Damaged data '%s' at" % sig, rec)

        hash = self.getbuffint(rec+4)
        blen = self.getbuffint(rec+8)
        #print("sig", sig, "hash", hex(hash), "len=", blen)

        data = self.getbuffstr(rec+12, blen)
        #data = self.buffer.getbuffer()[rec+12:rec+12+blen]
        #print("buff", data)
        #self.buffer.getbuffer()[rec+12+blen:rec+12+blen+4]

        endd = self.getbuffstr(rec + 12 + blen, INTSIZE)
        if endd != RECSEP:
            print("Damaged end data '%s' at" % endd, rec)

        rec2 = rec + 12 + blen;
        hash2 = self.getbuffint(rec2)
        blen2 = self.getbuffint(rec2+4)
        data2 = self.getbuffstr(rec2+8, blen2)

        print("buff", data, "buff2", data2)

        #print("hash2", hex(hash2), "len2=", blen2)


    def  dump_data(self):

        curr = self.getint(CURROFFSET)
        #print("curr", curr)
        chash = self.getint(CURRHASH)
        #print("chash", chash)

        doffs = self.getint(LINKDATA)
        for aa in range(chash):
            if aa < HASH_LIM:
                rec = self.getint(FIRSTHASH + aa * INTSIZE * 2)
                hh  = self.getint(FIRSTHASH + aa * INTSIZE * 2 + INTSIZE)
            else:
                nlink = self.getint(LINKHASH)
                rec, hh = self.gethash_offs(nlink + (aa-HASH_LIM) * INTSIZE * 2)
                rec += doffs

            print(aa, "offs:", rec, "\thash:", hex(hh))
            self.dump_rec(rec)

    # --------------------------------------------------------------------
    # Save data to database file

    def  save_data(self, arg2, arg3):

        #print("args", arg2, "---", arg3)
        curr = self.getint(CURROFFSET)
        #print("curr", curr)
        chash = self.getint(CURRHASH)
        #print("chash", chash)

        hhh = self.hash32(arg2)
        #print("hash", hex(hhh))

        if chash < HASH_LIM:
            self.putint(FIRSTHASH + chash * 2 * INTSIZE, curr)
            self.putint(FIRSTHASH + chash * 2 * INTSIZE + INTSIZE, hhh)
        else:
            # Allocate link
            nlink = self.getint(LINKHASH)
            if nlink == 0:
                nlink = (curr // JUMPSIZE + 1) * JUMPSIZE
                self.putint(LINKHASH, nlink)
                print("New link", chash, curr, nlink)

            self.puthash_offs(nlink + (chash - HASH_LIM) * 2 * INTSIZE, curr, hhh)

        self.putint(CURRHASH, chash + 1)

        if chash < DATA_LIM:
            pos = curr
        else:
            # Allocate after the link
            dlink = self.getint(LINKDATA)
            if dlink == 0:
                dlink = (curr // JUMPSIZE + 4) * JUMPSIZE
                self.putint(LINKDATA, dlink)
            pos = (curr - DATA_LIM ) + dlink

        # Update data
        self.buffer.seek(pos)
        self.xwrite(RECSIG)
        self.xwrite(struct.pack("I", hhh))
        self.xwrite(struct.pack("I", len(arg2)) )
        self.xwrite(arg2.encode("cp437"))
        self.xwrite(RECSEP)
        self.xwrite(struct.pack("I", len(arg3)) )
        self.xwrite(arg3.encode("cp437"))

        # Update lenght
        if chash < DATA_LIM:
            self.putint(CURROFFSET, self.buffer.tell())
        else:
            self.putint(CURROFFSET, self.buffer.tell() - dlink)

        self.flushx()


    def flushx(self):

        #print("dirty", self.dirty, "dirty_end", self.dirty_end)
        #print("hdirty", self.hdirty, "hdirty_end", self.hdirty_end)
        #
        # Save buffer
        #if self.dirty != DIRTY_MAX:
        #    self.fp.seek(self.dirty + HEADSIZE)
        #    self.fp.write(self.buffer.getbuffer()[self.dirty:self.dirty_end])
        #    self.dirty = DIRTY_MAX
        #    self.dirty_end = 0

        # Save buffer
        if self.hdirty != DIRTY_MAX:
            self.fp.seek(self.hdirty)
            self.fp.write(self.head.getbuffer()[self.hdirty:self.hdirty_end] )
            self.hdirty = DIRTY_MAX
            self.hdirty_end = 0

        #print(self.dirtyarr)

        # Simplify
        darr = []
        old_aa = 0; old_bb = 0
        save_aa = DIRTY_MAX; save_bb = 0;
        for aa, bb in self.dirtyarr:
            if abs(aa - old_bb) > 4:
                if save_aa != DIRTY_MAX:
                    darr.append((save_aa, save_bb))
                    save_aa = DIRTY_MAX; save_bb = 0
            if save_aa > aa:
                save_aa = aa
            if save_bb < bb:
                save_bb = bb
            old_aa = aa; old_bb = bb

        # Last
        if save_aa != DIRTY_MAX:
            darr.append((save_aa, save_bb))

        #print(darr)

        #for aa, bb in self.dirtyarr:
        for aa, bb in darr:
            self.fp.seek(aa + HEADSIZE)
            self.fp.write(self.buffer.getbuffer()[aa:bb])

        self.dirtyarr = []


# EOF



