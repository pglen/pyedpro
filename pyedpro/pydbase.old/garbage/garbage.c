
 # --------------------------------------------------------------------
    # Simplify array to connect overlapping ranges. This minimizes IO
    # onto the file

    def simplify(self, dirtarr, thresh = 4):

        #print("simplify",  dirtarr)

        darr = []; old_aa = 0; old_bb = 0
        save_aa = DIRTY_MAX; save_bb = 0;

        for aa, bb in dirtarr:
            if abs(aa - old_bb) > thresh:
                if save_aa != DIRTY_MAX:
                    darr.append((save_aa, save_bb))
                    save_aa = DIRTY_MAX; save_bb = 0
            if save_aa > aa:
                save_aa = aa
            if save_bb < bb:
                save_bb = bb
            old_aa = aa; old_bb = bb

        # Last, append if any
        if save_aa != DIRTY_MAX:
            darr.append((save_aa, save_bb))

        #print(darr)
        return darr;

    def flushx(self):

        ''' Flush all arrays onto their respective files '''

        # Save buffers from
        #print(self.dirtyarr)

        #darr = self.simplify(self.dirtyarr)
        #for aa, bb in darr:
        #    self.fp.seek(aa)
        #    self.fp.write(self.buffer.getbuffer()[aa:bb])
        #self.dirtyarr = []
        #
        ##print(self.idirtyarr)
        #idarr = self.simplify(self.idirtyarr)
        ##print(idarr)
        #
        #for aa, bb in idarr:
        #    self.ifp.seek(aa)
        #    self.ifp.write(self.index.getbuffer()[aa:bb])
        #self.idirtyarr = []
        pass

