#!/usr/bin/env python3

'''!
    @mainpage

    # Twincore

    Database with two files. One for data, one for index;

    The reason for this name is that two files are created. The first contains
    the data, the second contains the offsets (indexes) and hashes.

    The second file can be re-built easily from the first using the reindex option.

    Structure of the data:

        32 byte header, starating with FILESIG;

        4 bytes    4 bytes          4 bytes         Variable
        ------------------------------------------------------------
        RECSIG     Hash_of_key      Len_of_key      DATA_for_key
        RECSEP     Hash_of_payload  Len_of_payload  DATA_for_payload

            .
            .
            .

        RECSIG     Hash_of_key      Len_of_key      DATA_for_key
        RECSEP     Hash_of_payload  Len_of_payload  DATA_for_payload

    Deleted records are marked with RECSIG mutated from RECB to RECX

    New data is appended to the end, no duplicate filtering is done.
    Retrieval is searched from reverse, the latest record with this key
    is retrieved first.

    Verbosity:    (use the '-v' option multiple times)

        0 =  no output
        1 =  normal, some items printed, short record ;
        2 =  more detail; full record (-vv)
        3 =  more detail + damaged records (-vvv)

    Debug:    (use the '-d' option with number)

        0 =  no output
        1 =  normal, some items
        2 =  more details

    History:

        Sat 04.Feb.2023     --  Converted from CURRDATA to ftell

'''

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading
import  struct, io

from twinbase import *

version = "1.0 dev"

# NamedAtomicLock -- did not work here

# ------------------------------------------------------------------------

class TwinCore(TwinCoreBase):

    '''

     Data file and index file; protected by locks
     The TWIN refers to separate files for data / index.

    '''

    def __init__(self, fname = "pydbase.pydb"):

        super(TwinCoreBase, self).__init__()
        #print("initializing core with", fname)

        self.core_verbose  = 0
        #self.pool = threading.BoundedSemaphore(value=1)

        self.cnt = 0
        self.fname = fname
        self.idxname  = os.path.splitext(self.fname)[0] + ".pidx"
        self.lckname  = os.path.splitext(self.fname)[0] + ".lock"
        #self.lckname2 = os.path.splitext(self.fname)[0] + ".lock2"

        # This will never show ... but it was informative at one point
        if core_pgdebug > 4:
            print("fname:    ", fname)
            print("idxname:  ", self.idxname)
            print("lockname: ", self.lckname)

        self.lasterr = "No Error"

        #print("Q pid", os.getpid())

        # Make sure only one process can use this
        waitlock(self.lckname)

        #print("pid", os.getpid())

        # Initial file creation

        # Nuke false index
        try:
            if not os.path.isfile(self.fname):
                #os.rename(self.idxname, self.idxname + ".old")
                os.remove(self.idxname)

        except:
            pass

        self.fp = self.softcreate(self.fname)
        self.ifp = self.softcreate(self.idxname)

        #waitlock(self.waitlock2)

        buffsize = self.getsize(self.fp)
        if buffsize < HEADSIZE:
            #print("initial padding")
            self.create_data(self.fp)
            #try:
            #    # There was no file, delete index, if any
            #    os.rename(self.idxname, self.idxname + ".dangle")
            #    #os.remove(self.idxname)
            #except:
            #    pass

            #print("initial padding")
            self.create_idx(self.ifp)
        else:
            # Initial index creation
            #self.ifp = self.softcreate(self.idxname)
            indexsize = self.getsize(self.ifp)

            # See if valid index
            if indexsize < HEADSIZE:
                self.create_idx(self.ifp)
                # It was an existing data, new index needed
                if self.core_verbose > 0:
                    print("Reindexing")
                self.__reindex()

        # Check
        if  self.getbuffstr(0, 4) != FILESIG:
            print("Invalid data signature")
            dellock(self.lckname)
            raise  RuntimeError("Invalid database signature.")

        #print("buffsize", buffsize, "indexsize", indexsize)
        dellock(self.lckname)

    def __del__(self):

        try:
            #self.fp.ob_flush()
            #self.ifp.ob_flush()
            #self.fp.flush()
            #self.ifp.flush()

            if hasattr(self, "fp"):
                self.fp.close()
                self.ifp.close()

            pass
        except:
            print("Cannot close files", sys.exc_info())

    def getdbsize(self):
        ret = self._getdbsize(self.ifp)
        if not ret:
            ret = 0
        return ret

    def _getdbsize(self, ifp):

        try:
            #chash = self.getidxint(CURROFFS) - HEADSIZE
            chash = self.getsize(ifp) - HEADSIZE
            ret = int(chash / (2 * self.INTSIZE))
        except:
            ret = 0

        return  ret

    # --------------------------------------------------------------------
    def rec2arr(self, rec):

        arr = []
        sig = self.getbuffstr(rec, self.INTSIZE)

        if sig == RECDEL:
            return arr

        if sig != RECSIG:
            if self.core_verbose > 0:
                print(" Damaged data (sig) '%s' at" % sig, rec)
            return arr

        hash = self.getbuffint(rec+4)
        blen = self.getbuffint(rec+8)
        data = self.getbuffstr(rec + 12, blen)

        if core_integrity:
            ccc = self.hash32(data)
            if self.core_verbose > 1:
                print("rec", rec, "hash", hex(hash), "check", hex(ccc))
            if hash != ccc:
                if self.core_verbose > 0:
                    print("Error on hash at rec", rec, "hash", hex(hash), "check", hex(ccc))
                return []

        #print("%5d pos %5d" % (cnt, rec), "hash %8x" % hash, "ok", ok, "len=", blen, end=" ")

        endd = self.getbuffstr(rec + 12 + blen, self.INTSIZE)
        if endd != RECSEP:
            if self.core_verbose > 0:
                print(" Damaged data (sep) '%s' at" % endd, rec)
            return arr

        rec2 = rec + 16 + blen;
        hash2 = self.getbuffint(rec2)
        blen2 = self.getbuffint(rec2+4)
        data2 = self.getbuffstr(rec2+8, blen2)

        if core_integrity:
            ccc2 = self.hash32(data2)
            if self.core_verbose > 1:
                print("rec", rec, "hash2", hex(hash2), "check2", hex(ccc2))
            if hash2 != ccc2:
                if self.core_verbose > 0:
                    print("Error on hash at rec", rec, "hash2", hex(hash2), "check2", hex(ccc2))
                return []

        arr = [data, data2]
        return arr

    # -------------------------------------------------------------------
    # Originator, dump single record

    def  dump_rec(self, rec, cnt):

        ''' Print record to the screen '''

        cnt2 = 0
        sig = self.getbuffstr(rec, self.INTSIZE)

        if sig == RECDEL:
            if core_showdel:
                klen = self.getbuffint(rec+8)
                kdata = self.getbuffstr(rec+12, klen)
                rec2 = rec + 16 + klen;
                blen = self.getbuffint(rec2+4)
                data = self.getbuffstr(rec2+8, blen)

                print(" Del at", rec, "key:", kdata, "data:", truncs(data))
            return cnt2

        if sig != RECSIG:
            if self.core_verbose > 1:
                print(" Damaged data (sig) '%s' at" % sig, rec)
            return cnt2

        hash = self.getbuffint(rec+4)
        blen = self.getbuffint(rec+8)

        if blen < 0:
            print("Invalid key length %d at %d" % (blen, rec))
            return cnt2

        data = self.getbuffstr(rec+12, blen)
        if core_integrity:
            ccc = self.hash32(data)
            if self.core_verbose > 1:
                print("rec", rec, "hash", hex(hash), "check", hex(ccc))
            if hash != ccc:
                if self.core_verbose > 0:
                    print("Error on hash at rec", rec, "hash", hex(hash), "check", hex(ccc))
                return []

        endd = self.getbuffstr(rec + 12 + blen, self.INTSIZE)
        if endd != RECSEP:
            if self.core_verbose > 0:
                print(" Damaged data (sep) '%s' at" % endd, rec)
            return cnt2

        rec2 = rec + 16 + blen;
        hash2 = self.getbuffint(rec2)
        blen2 = self.getbuffint(rec2+4)

        if blen2 < 0:
            print("Invalid data length %d at %d" % (blen2, rec))
            return cnt2

        data2 = self.getbuffstr(rec2+8, blen2)
        if core_integrity:
            ccc2 = self.hash32(data2)
            if self.core_verbose > 1:
                print("rec", rec, "hash2", hex(hash), "check2", hex(ccc))
            if hash2 != ccc2:
                if self.core_verbose > 0:
                    print("Error on hash at rec", rec, "hash2", hex(hash), "check2", hex(ccc))
                return []
        if self.core_verbose > 1:
            print("%-5d pos %5d" % (cnt, rec), "%8x" % hash, "len", blen, data,
                                                        "%8x" % hash2,"len", blen2, data2)
            print()

        elif self.core_verbose:
            print("%-5d pos %5d" % (cnt, rec), "%8x" % hash, "len", blen, truncs(data),
                                                        "%8x" % hash2,"len", blen2, truncs(data2))
        else:
            print("%-5d pos %5d" % (cnt, rec), "Data:", truncs(data, 18), "Data2:", truncs(data2, 18))

        cnt2 += 1
        return cnt2

    def  check_rec(self, rec, cnt2):

        ''' Print record to the screen '''
        ret = 0
        sig = self.getbuffstr(rec, self.INTSIZE)

        # Do not check deleted, say OK
        if sig == RECDEL:
            ret = 1
            return ret

        if sig != RECSIG:
            if self.core_verbose > 0:
                print(" Damaged data (sig) '%s' at %d (%d)" % (sig, rec, cnt2))
            #if self.core_verbose > 1:
            #    print("Data", data)

            return ret

        hash = self.getbuffint(rec+4)
        blen = self.getbuffint(rec+8)

        if blen <= 0:
            if self.core_verbose > 1:
                print("Invalid key length %d at %d" % (blen, rec))
            return ret

        data = self.getbuffstr(rec+12, blen)
        ccc = self.hash32(data)
        if hash != ccc:
            if self.core_verbose > 0:
                print("Error on hash at rec", rec, cnt2, "hash", hex(hash), "check", hex(ccc))

            if self.core_verbose > 1:
                print("Data", data)
            return ret

        endd = self.getbuffstr(rec + 12 + blen, self.INTSIZE)
        if endd != RECSEP:
            if self.core_verbose > 0:
                print(" Damaged data (sep) '%s' at %d %d %d" % (endd, rec, cnt2))
            return ret

        rec2 = rec + 16 + blen;
        hash2 = self.getbuffint(rec2)
        blen2 = self.getbuffint(rec2+4)

        if blen2 < 0:
            if self.core_verbose > 1:
                print("Invalid data length2 %d at %d" % (blen2, rec))
            return ret

        data2 = self.getbuffstr(rec2+8, blen2)
        ccc2 = self.hash32(data2)
        if hash2 != ccc2:
            if self.core_verbose > 0:
                print("Error on hash2 at rec", rec, cnt2, "hash2", hex(hash2), "check2", hex(ccc2))
            if self.core_verbose > 1:
                print("Data", data, "Data2", data2)
            return ret

        if self.core_verbose > 2:
            print("Record at %d (%d) OK." % (rec, cnt2))

        ret += 1
        return ret

    # --------------------------------------------------------------------
    # Internal; no locking

    def  __dump_data(self, lim = INT_MAX, skip = 0, dirx = 0):

        ''' Put all data to screen worker function '''

        cnt = skip; cnt2 = 0
        curr =  chash = HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2

        # Direction sensitivity
        if dirx:
            rrr = range(HEADSIZE + skip * self.INTSIZE * 2, chash, self.INTSIZE * 2)
        else:
            rrr = range(chash - self.INTSIZE * 2, HEADSIZE  - self.INTSIZE * 2, -self.INTSIZE * 2)

        for aa in rrr:
            rec = self.getidxint(aa)
            #print(aa, rec)
            if not core_quiet:
                cnt2 += 1
                ret = self.dump_rec(rec, cnt)
                if ret:
                    cnt += 1
                    if cnt >= lim:
                        break

    def  dump_data(self, lim = INT_MAX, skip = 0):

        ''' Put all data to screen '''

        self.__dump_data(lim, skip, 1)

    def  revdump_data(self, lim, skip = 0):

        ''' Put all data to screen in reverse order '''

        self.__dump_data(lim, skip)

    def  reindex(self):
        waitlock(self.lckname)
        ret = self.__reindex()
        dellock(self.lckname)
        return ret

    # --------------------------------------------------------------------

    def  __reindex(self):

        ''' Recover index. Make sure the DB in not in session.  '''

        ret = 0

        #curr = self.getbuffint(CURROFFS) - HEADSIZE
        curr =  self._getdbsize(self.ifp) * self.INTSIZE * 2

        reidx = os.path.splitext(self.fname)[0]  + "_tmp_" + ".pidx"
        tempifp = self.softcreate(reidx)
        self.create_idx(tempifp)
        dlen = self.getsize(self.fp)

        if self.core_verbose > 2:
           print("curr", curr, "dlen", dlen)

        aa =  HEADSIZE
        while 1:
            if aa >= dlen:
                break

            sig = self.getbuffstr(aa, self.INTSIZE)
            # Check if sig is correct
            if sig != RECSIG:
                print("Invalid sig .. resync needed")

            #print("reind", aa)

            try:
                hhh2 = self.getbuffint(aa + 4)
                lenx = self.getbuffint(aa + 8)
                if lenx < 0:
                    print("Invalid key length")
                sep =  self.getbuffstr(aa + 12 + lenx, self.INTSIZE)
                len2 =  self.getbuffint(aa + 20 + lenx)
                if len2 < 0:
                    print("Invalid record length")
            except:
                print("in reindex", sys.exc_info())

            if self.core_verbose == 1:
                print(aa, "sig", sig, "hhh2", hex(hhh2), "len", lenx, \
                    "sep", sep, "len2", len2)
            if self.core_verbose > 1:
                data =  self.getbuffstr(aa + 12, lenx)
                data2 =  self.getbuffstr(aa + 24 + lenx, len2)
                print(aa, "sig", sig, "data", data, "data2", data2)

            # Update / Append index
            #hashpos = self._getint(tempifp, CURROFFS)
            hashpos =  HEADSIZE  + self._getdbsize(tempifp) * self.INTSIZE * 2

            self._putint(tempifp, hashpos, aa)
            self._putint(tempifp, hashpos + self.INTSIZE, hhh2)

            # This is a shame .. did not flush to file immidiately
            tempifp.flush()

            #self._putint(tempifp, hashpos, self.fp.tell())

            # This is dependent on the database structure
            aa += lenx + len2 + 24
            ret += 1

        # Make it go out of scope
        self.fp.flush()
        self.ifp.flush();
        self.ifp.close()
        tempifp.flush();        tempifp.close()

        # Now move files
        try:
            os.remove(self.idxname)
        except:
            pass

        #print("rename", reidx, "->", self.idxname)
        os.rename(reidx, self.idxname)

        # Activate new index
        self.ifp = self.softcreate(self.idxname)
        return ret

    def __save_error(self, rec, vacerrfp):

        vacerrfp.write(b"Err at %8d\n" % rec)

        try:
            ddd = self.getbuffstr(rec, 100)
        except:
            pass

        # Find next valid record, print up to that
        found = 0
        for aa in range(len(ddd)):
            if ddd[aa:aa+4] == RECSIG:
                found = True
                #print("found:", ddd[:aa+4])
                vacerrfp.write(ddd[:aa])
                break
        if not found:
            vacerrfp.write(ddd)

    # ----------------------------------------------------------------

    def  vacuum(self):
        ''' Remove all deleted data
            Make sure the db in not in session. '''

        waitlock(self.lckname)
        ret = self._vacuum()
        dellock(self.lckname)
        return ret

    def  _vacuum(self):

        vacname = os.path.splitext(self.fname)[0] + "_vac_" + ".pydb"
        vacerr  = os.path.splitext(self.fname)[0] +  ".perr"
        vacidx = os.path.splitext(vacname)[0]  + ".pidx"

        if core_pgdebug > 4:
            print("vacname", vacname)
            print("vacidx", vacidx)
            print("vacerr", vacerr)

        ret = 0; vac = 0

        # Open for append
        vacerrfp = self.softcreate(vacerr, False)
        vacerrfp.seek(0, os.SEEK_END)

        try:
            # Make sure they are empty
            os.remove(vacname)
            os.remove(vacidx)
        except:
            pass

        # It is used to raise the scope so vacuumed DB closes
        if 1:
            vacdb = TwinCore(vacname)
            waitlock(vacdb.lckname)

            skip = 0; cnt = 0
            chash =  self._getdbsize(self.ifp) * self.INTSIZE * 2
            rrr = range(HEADSIZE + skip * self.INTSIZE * 2, chash + HEADSIZE, self.INTSIZE * 2)
            for aa in rrr:
                rec = self.getidxint(aa)
                sig = self.getbuffstr(rec, self.INTSIZE)
                if sig == RECDEL:
                    ret += 1
                    if core_pgdebug > 1:
                        print("deleted", rec)
                elif sig != RECSIG:
                    if self.core_verbose:
                        print("Detected error at %d" % rec)
                    ret += 1
                    self.__save_error(rec, vacerrfp)
                else:
                    global core_integrity
                    tmpi = core_integrity
                    core_integrity = True
                    arr = self.get_rec_offs(rec)
                    core_integrity = tmpi

                    if core_pgdebug > 1:
                        print(cnt, "vac rec", rec, arr)

                    if len(arr) > 1:
                        hhh2 = self.hash32(arr[0])
                        hhh3 = self.hash32(arr[1])
                        vacdb.__save_data(hhh2, arr[0], hhh3, arr[1])
                        vac += 1
                    else:
                        # This could be from empty bacause of hash error
                        self.__save_error(rec, vacerrfp)
                        if core_pgdebug > 0:
                            print("Error on vac: %d" % rec)
                cnt += 1

            dellock(vacdb.lckname)

            # if vacerr is empty
            try:
                if os.stat(vacerr).st_size == 0:
                    #print("Vac error empty")
                    os.remove(vacerr)
            except:
                print("vacerr", sys.exc_info())


        dellock(self.lckname)

        # Any vacummed?
        if vac > 0:
            # Make it go out of scope
            self.fp.flush(); self.ifp.flush()
            self.fp.close(); self.ifp.close()

            # Now move files
            try:
                os.remove(self.fname);  os.remove(self.idxname)
            except:
                pass

            if core_pgdebug > 1:
                print("rename", vacname, "->", self.fname)
                print("rename", vacidx, "->", self.idxname)

            os.rename(vacname, self.fname)
            os.rename(vacidx, self.idxname)

            waitlock(self.lckname)
            self.fp = self.softcreate(self.fname)
            self.ifp = self.softcreate(self.idxname)
            dellock(self.lckname)

        else:
            # Just remove non vacuumed files
            if core_pgdebug > 1:
                print("deleted", vacname, vacidx)
            try:
                os.remove(vacname)
                os.remove(vacidx)
            except:
                pass

        #print("ended vacuum")
        return ret, vac

    def  get_rec(self, recnum):

        ''' Get record from database; recnum is a zero based record counter '''

        rsize = self._getdbsize(self.ifp)
        if recnum >= rsize:
            #print("Past end of data.");
            raise  RuntimeError( \
                    "Past end of Data. Asking for %d while max is 0 .. %d records." \
                                     % (recnum, rsize-1) )
            return []

        chash = self.getidxint(CURROFFS)
        #print("chash", chash)
        offs = self.getidxint(HEADSIZE + recnum * self.INTSIZE * 2)

        #print("offs", offs)
        return self.rec2arr(offs)

    def  get_rec_offs(self, recoffs):

        rsize = self.getsize(self.fp)
        if recoffs >= rsize:
            #print("Past end of data.");
            raise  RuntimeError( \
                    "Past end of File. Asking for offset %d file size is %d." \
                                     % (recoffs, rsize) )
            return []

        sig = self.getbuffstr(recoffs, self.INTSIZE)
        if sig == RECDEL:
            if self.core_verbose:
                print("Deleted record.")
            return []
        if sig != RECSIG:
            print("Unlikely offset %d is not at record boundary." % recoffs, sig)
            return []
        #print("recoffs", recoffs)
        return self.rec2arr(recoffs)

    def  get_key_offs(self, recoffs):

        rsize = self.getsize(self.fp)
        if recoffs >= rsize:
            #print("Past end of data.");
            raise  RuntimeError( \
                    "Past end of File. Asking for offset %d file size is %d." \
                                     % (recoffs, rsize) )
            return []

        sig = self.getbuffstr(recoffs, self.INTSIZE)
        if sig == RECDEL:
            if self.core_verbose:
                print("Deleted record.")
            return []
        if sig != RECSIG:
            print("Unlikely offset %d is not at record boundary." % recoffs, sig)
            return []
        #print("recoffs", recoffs)
        return self.rec2arr(recoffs)[0]

    def  del_rec(self, recnum):
        rsize = self._getdbsize(self.ifp)
        if recnum >= rsize:
            if self.core_verbose:
                print("Past end of data.");
            return False
        chash = self.getidxint(CURROFFS)
        #print("chash", chash)
        offs = self.getidxint(HEADSIZE + recnum * self.INTSIZE * 2)
        #print("offs", offs)
        old = self.getbuffstr(offs, self.INTSIZE)
        if old == RECDEL:
            if self.core_verbose:
                print("Record at %d already deleted." % offs);
            return False

        self.putbuffstr(offs, RECDEL)
        return True

    def  del_rec_offs(self, recoffs):

        rsize = self.getsize(self.fp)
        if recoffs >= rsize:
            #print("Past end of data.");
            raise  RuntimeError( \
                    "Past end of File. Asking for offset %d file size is %d." \
                                     % (recoffs, rsize) )
            return False

        sig = self.getbuffstr(recoffs, self.INTSIZE)
        if sig != RECSIG  and sig != RECDEL:
            print("Unlikely offset %d is not at record boundary." % recoffs, sig)
            return False

        self.putbuffstr(recoffs, RECDEL)
        return True

    # Check integrity

    def integrity_check(self, skip = 0):

        waitlock(self.lckname)

        ret = 0; cnt2 = 0
        #chash = self.getidxint(CURROFFS)        #;print("chash", chash)
        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2

        # Direction sensitivity
        rrr = range(HEADSIZE + skip * self.INTSIZE * 2, chash, self.INTSIZE * 2)
        for aa in rrr:
            rec = self.getidxint(aa)
            #print(aa, rec)
            ret  += self.check_rec(rec, cnt2)
            cnt2 += 1

        dellock(self.lckname)

        return ret, cnt2


    def  retrieve(self, strx, limx = 1):

        ''' Retrive in reverse, limit it '''

        if type(strx) == str:
            strx = strx.encode(errors='strict')

        hhhh = self.hash32(strx)
        if core_pgdebug > 2:
            print("strx", strx, hhhh)

        #chash = self.getidxint(CURROFFS)
        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2

        #;print("chash", chash)
        arr = []

        waitlock(self.lckname)

        #for aa in range(HEADSIZE + self.INTSIZE * 2, chash, self.INTSIZE * 2):
        for aa in range(chash - self.INTSIZE * 2, HEADSIZE  - self.INTSIZE * 2, -self.INTSIZE * 2):
            rec = self.getidxint(aa)
            sig = self.getbuffstr(rec, self.INTSIZE)
            if sig == RECDEL:
                if self.core_verbose > 3:
                    print(" Deleted record '%s' at" % sig, rec)
            elif sig != RECSIG:
                if self.core_verbose:
                    print(" Damaged data '%s' at" % sig, rec)
            else:
                hhh = self.getbuffint(rec+4)
                if hhh == hhhh:
                    arr.append(self.get_rec_offs(rec))
                    if len(arr) >= limx:
                        break
        dellock(self.lckname)

        return arr

    def  findrec(self, strx, limx = INT_MAX, skipx = 0):

        ''' Find by string matching substring '''

        waitlock(self.lckname)

        #chash = self.getidxint(CURROFFS)            #;print("chash", chash)
        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2

        arr = []
        strx2 = strx.encode(errors='strict');

        #print("findrec", strx2)

        #for aa in range(HEADSIZE + self.INTSIZE * 2, chash, self.INTSIZE * 2):
        for aa in range(chash - self.INTSIZE * 2, HEADSIZE  - self.INTSIZE * 2, -self.INTSIZE * 2):
            rec = self.getidxint(aa)
            sig = self.getbuffstr(rec, self.INTSIZE)
            if sig == RECDEL:
                if core_showdel:
                    print(" Deleted record '%s' at" % sig, rec)
            elif sig != RECSIG:
                if self.core_verbose > 0:
                    print(" Damaged data '%s' at" % sig, rec)
            else:
                blen = self.getbuffint(rec+8)
                data = self.getbuffstr(rec + 12, blen)
                if self.core_verbose > 1:
                    print("find", data)
                #if str(strx2) in str(data):
                if strx2 in data:
                    arr.append(self.get_key_offs(rec))
                    #arr.append(rec)

                    if len(arr) >= limx:
                        break
        dellock(self.lckname)

        return arr

    # --------------------------------------------------------------------
    # List all active records

    def  listall(self):

        waitlock(self.lckname)
        keys = []; arr = []; cnt = 0

        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2
        maxrec = chash - self.INTSIZE * 2
        rsize = self._getdbsize(self.ifp) - 1

        rrr =  range(maxrec,
                HEADSIZE - self.INTSIZE * 2, -self.INTSIZE * 2)
        for aa in rrr:
            rec = self.getidxint(aa)

            #print(" Scanning at %d %d" % (rec, cnt))

            sig = self.getbuffstr(rec, self.INTSIZE)
            if sig == RECDEL:
                if 1: #core_showdel:
                    print("Deleted record '%s' at" % sig, rec)
            elif sig != RECSIG:
                if 1: #self.core_verbose > 0:
                    print(" Damaged data '%s' at" % sig, rec)
            else:
                    hhh = self.getbuffint(rec+4)
                    print(" Good data '%s' at" % sig, rec, hhh)
                    if hhh not in keys:
                        keys.append(hhh)
                        # as we are going backwards
                        arr.append(rsize - cnt)
                        print("found", hhh)


            cnt += 1

        keys = []
        dellock(self.lckname)

        return arr

    # --------------------------------------------------------------------
    # Search from the end, so latest comes first

    def  find_key(self, keyx, limx = 0xffffffff):

        waitlock(self.lckname)

        skip = 0; arr = []; cnt = 0
        try:
            arg2e = keyx.encode()
        except:
            arg2e = keyx

        hhhh = self.hash32(arg2e)
        #print("hashx", "'" + hashx + "'", hex(hhhh), arg2e)

        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2
        rrr =  range(chash - self.INTSIZE * 2,
                HEADSIZE - self.INTSIZE * 2, -self.INTSIZE * 2)
        for aa in rrr:
            rec = self.getidxint(aa)
            #print(" Scanning at %d %d" % (rec, cnt))

            sig = self.getbuffstr(rec, self.INTSIZE)
            if sig == RECDEL:
                if core_showdel:
                    print("Deleted record '%s' at" % sig, rec)
            elif sig != RECSIG:
                if self.core_verbose > 0:
                    print(" Damaged data '%s' at" % sig, rec)
            else:
                hhh = self.getbuffint(rec+4)
                if hhh == hhhh:
                    if len(arr) >= limx - 1:
                        arr.append(["More data ...",])
                        break
                    arr.append(rec)
                else:
                    pass
                    #print("no match", hex(hhh))

            cnt += 1
        dellock(self.lckname)

        return arr


    def  del_data(self, hash, skip = 1):

        ''' Delete data by hash '''

        cnt = skip
        hhhh = int(hash, 16)                #;print("hash", hash, hhhh)
        curr = self.getbuffint(CURROFFS)    #;print("curr", curr)
        chash = self.getidxint(CURROFFS)    #;print("chash", chash)

        arr = []
        for aa in range(HEADSIZE + skip * self.INTSIZE * 2, chash, self.INTSIZE * 2):
            rec = self.getidxint(aa)

            # Optional check
            #sig = self.getbuffstr(rec, self.INTSIZE)
            #if sig != RECSIG:
            #    print(" Damaged data '%s' at" % sig, rec)

            #blen = self.getbuffint(rec+8)
            #print("data '%s' at" % sig, rec, "blen", blen)

            hhh = self.getbuffint(rec+4)
            if hash == hhh:
                if self.core_verbose > 0:
                    print("Would delete", hhh)

            self.putbuffstr(rec, RECDEL)

            cnt += 1

        return arr


    def  del_rec_bykey(self, strx, maxrec = 1, skip = 0):

        ''' Delete records by key string; needs bin str, converted
        automatically on entry  '''

        if type(strx) == str:
            strx = strx.encode()

        if self.core_verbose > 1:
            print("Start delete ", strx, "skip", skip)

        cnt = 0; cnt3 = 0
        #chash = self.getidxint(CURROFFS)    #;print("chash", chash)
        chash =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2

        for aa in range(HEADSIZE, chash, self.INTSIZE * 2):
            rec = self.getidxint(aa)
            sig = self.getbuffstr(rec, self.INTSIZE)
            if sig == RECDEL:
                if core_showdel:
                    print(" Deleted record '%s' at" % sig, rec)
            elif sig != RECSIG:
                if self.core_verbose > 0:
                    print(" Damaged data '%s' at" % sig, rec)
            else:
                blen = self.getbuffint(rec+8)
                data = self.getbuffstr(rec + 12, blen)
                if self.core_verbose > 2:
                    print("del iterate recs", cnt3, data, strx)

                if strx == data:
                    if self.core_verbose > 0:
                        print("Deleting", cnt3, aa, data)
                    self.putbuffstr(rec, RECDEL)
                    cnt += 1
                    if cnt >= maxrec:
                        break
            cnt3 += 1
        return cnt

    # --------------------------------------------------------------------
    # Save data to database file

    def  save_data(self, arg2, arg3):

        waitlock(self.lckname)

        # Prepare all args, if cannot encode, use original
        try:
            arg2e = arg2.encode()
        except:
            arg2e = arg2
        try:
            arg3e = arg3.encode()
        except:
            arg3e = arg3

        if core_pgdebug > 1:
            print("args", arg2e, "arg3", arg3e)

        hhh2 = self.hash32(arg2e)
        hhh3 = self.hash32(arg3e)

        if core_pgdebug > 1:
            print("hhh2", hhh2, "hhh3", hhh3)

        ret = self.__save_data(hhh2, arg2e, hhh3, arg3e)

        dellock(self.lckname)
        return ret

    def __save_data(self, hhh2, arg2e, hhh3, arg3e):

        # Update / Append data
        tmp = RECSIG
        tmp += struct.pack("I", hhh2)
        tmp += struct.pack("I", len(arg2e))
        tmp += arg2e
        tmp += RECSEP
        tmp += struct.pack("I", hhh3)
        tmp += struct.pack("I", len(arg3e))
        tmp += arg3e

        #print(tmp)
        # The pre - assemple to string added 20% efficiency

        #curr = self.getbuffint(CURROFFS)
        curr =  HEADSIZE  + self._getdbsize(self.ifp) * self.INTSIZE * 2
        #print("curr", curr)

        self.fp.seek(0, os.SEEK_END)
        dcurr = self.fp.tell()

        self.fp.write(tmp)

        # This allowed corruption of the data string
        # Update lenght
        #self.putbuffint(CURROFFS, self.fp.tell()) #// - dlink + DATA_LIM)
        #self.fp.seek(curr)
        #print("hashpos", hashpos)

        # Update / Append index
        self.putidxint(curr, dcurr)
        self.putidxint(curr + self.INTSIZE, hhh2)
        #self.putidxint(CURROFFS, self.ifp.tell())

        self.fp.flush()
        self.ifp.flush()

        return curr

#__all__ = ["TwinCore", "self.core_verbose", "core_quiet", "core_pgdebug",
#                "core_lcktimeout"]
#

# EOF