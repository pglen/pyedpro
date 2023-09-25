#!/usr/bin/env python3

'''!
    @mainpage

    # Twinchain

    Block chain layer on top of twincore

    History:

        Sun 26.Mar.2023   --  Initial

'''

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, uuid
import  struct, io, hashlib

from twincore import *
import pypacker

version = "1.0 dev"
protocol = "1.0"

def _pad(strx, lenx=8):
    ttt = len(strx)
    if ttt >= lenx:
        return strx
    padx = " " * (lenx-ttt)
    return strx + padx

# ------------------------------------------------------------------------

class TwinChain(TwinCore):

    '''

    '''

    def __init__(self, fname = "pydbchain.pydb"):

        #super(TwinCore, self).__init__(fname)
        # Fuck; this one finally worked
        super().__init__(fname)
        #print("TwinChain.init", self.fname)
        self.packer = pypacker.packbin()
        sss = self.getdbsize()
        if sss == 0:
            payload = b"Initial record, do not use."
            #print("Init anchor record", payload)
            # Here we fake the initial backlink for the anchor record
            self.old_dicx = {}
            hh = hashlib.new("sha256"); hh.update(payload)
            self.old_dicx["hash256"] =  hh.hexdigest()

            dt = datetime.datetime.utcnow()
            fdt = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
            self.old_dicx["now"] =  fdt

            # Produce data structure
            header = str(uuid.uuid4())
            aaa = []
            self._fill_record(aaa, header, payload)

            encoded = self.packer.encode_data("", aaa)
            self.save_data(header, encoded)

    def  _key_n_data(self, arrx, keyx, strx):
        arrx.append(keyx)
        arrx.append(strx)

    # --------------------------------------------------------------------

    def _fill_record(self, aaa, header, payload):

        self._key_n_data(aaa, "header", header)
        self._key_n_data(aaa, "protocol", protocol)

        dt = datetime.datetime.utcnow()
        fdt = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        self._key_n_data(aaa, "now", fdt)
        self._key_n_data(aaa, "payload", payload)

        self._key_n_data(aaa, "hash32", str(self.hash32(payload)))

        hh = hashlib.new("sha256"); hh.update(payload)
        self.new_fff = hh.hexdigest()
        self._key_n_data(aaa, "hash256", self.new_fff)

        dd = hashlib.new("md5"); dd.update(payload)
        self._key_n_data(aaa, "md5", dd.hexdigest())

        backlink = self.old_dicx["hash256"] + self.old_dicx["now"]
        backlink += self.new_fff

        #print("backlink raw", backlink)
        bl = hashlib.new("sha256"); bl.update(backlink.encode())
        self._key_n_data(aaa, "backlink", bl.hexdigest())

        self.old_dicx = {}

    def get_payload(self, recnum):
        arr = self.get_rec(recnum)
        decoded = self.packer.decode_data(arr[1])
        dic = self.get_fields(decoded[0])
        if self.core_verbose > 0:
            return dic
        return arr[0].decode(), dic['payload']

    def integrity(self, recnum):

        ''' Scan one record an its integrity based on the previous one '''

        if recnum < 1:
            print("Cannot check initial record.")
            return False

        if self.core_verbose > 4:
            print("Checking ...", recnum)

        arr = self.get_rec(recnum-1)
        decoded = self.packer.decode_data(arr[1])
        dic = self.get_fields(decoded[0])

        arr2 = self.get_rec(recnum)
        decoded2 = self.packer.decode_data(arr2[1])
        dic2 = self.get_fields(decoded2[0])

        backlink =  dic["hash256"] + dic["now"]
        backlink += dic2["hash256"]

        #print("backlink raw", backlink)
        hh = hashlib.new("sha256"); hh.update(backlink.encode())

        if self.core_verbose > 1:
            print("calculated", hh.hexdigest())
        if self.core_verbose > 2:
            print("backlink  ", dic2['backlink'])

        return hh.hexdigest() == dic2['backlink']

    def check(self, recnum):
        arr = self.get_rec(recnum)
        decoded = self.packer.decode_data(arr[1])
        dic = self.get_fields(decoded[0])

        hh = hashlib.new("sha256"); hh.update(dic['payload'].encode())
        if self.core_verbose > 1:
            print("data", hh.hexdigest())
        if self.core_verbose > 2:
            print("hash", dic['hash256'])
        return hh.hexdigest() == dic['hash256']

    def append(self, datax):

        if self.core_verbose > 0:
            print("Append", datax)

        if type(datax) == str:
            datax = datax.encode(errors='strict')

        self.old_dicx = {}
        # Get last data from db
        sss = self.getdbsize()
        #print("sss", sss)
        if sss:
            ooo = self.get_rec(sss-1)
            #print("ooo", ooo)
            decoded = self.packer.decode_data(ooo[1])
            #self.dump_rec(decoded[0])
            self.old_dicx = self.get_fields(decoded[0])
            #print(old_dicx)

            #print("old_fff", self.old_dicx["hash256"])
            #print("old_time", self.old_dicx["now"])

        # Produce data structure
        header = str(uuid.uuid4())
        aaa = []
        self._fill_record(aaa, header, datax)

        encoded = self.packer.encode_data("", aaa)
        #print(encoded)

        self.save_data(header, encoded)

        if self.core_verbose > 1:
            bbb = self.packer.decode_data(encoded)
            #print(bbb[0])
            self.dump_rec(bbb[0])

    def dump_rec(self, bbb):
        for aa in range(len(bbb)//2):
            print(_pad(bbb[2*aa]), "=", bbb[2*aa+1])

    def get_fields(self, bbb):
        dicx = {}
        for aa in range(len(bbb)//2):
            dicx[bbb[2*aa]]  = bbb[2*aa+1]
        return dicx

    def __del__(self):
        ''' Override for now '''
        pass

# EOF
