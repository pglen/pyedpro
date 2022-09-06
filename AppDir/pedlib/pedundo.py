#!/usr/bin/env python

# Undo / redo handler

# To use the undo, we have four operations.
#
# 1.) Line modified - MODIFIED  (crude implementation, you may improve it)
# 2.) Line added    - ADDED
# 3.) Line deleted  - DELETED
# 4.) No change     - NOOP
#
# In order to group operations, (like multi line cut) set the
# CONTFLAG by OR-ing it in. (adding) To signal the end of group do
# a NOOP without the CONTFLAG. Redo is generated .
# Because of redo, please provide the old info every time.
# Like the old buffer on delete, even though it is discarded,
# still the redo uses the info for its operation.
#
# A typical call to the undo looks like this:
#
# self2.undoarr.append((xidx, yidx, MODIFIED + CONTFLAG, self2.text[cnt]))
#   Args: cursor x, cursor y, opcode, original content

#from __future__ import print_function

from pedlib import pedconfig

# Op codes:
(NOOP, MODIFIED, ADDED, DELETED) = list(range(4))

#print "(NOOP, MODIFIED, ADDED, DELETED)", NOOP, MODIFIED, ADDED, DELETED

CONTFLAG = 0x80                         # Continuation flag
CONTMASK = CONTFLAG - 1                 # Cont flag mask

#print hex(CONTFLAG), hex(CONTMASK)

# The undo stack limit pops from the beginning, so the oldest transaction
# is discarded. The stack persists across sessions, so we limit it.
# Note that the stack size is the number of undo transactions saved,
# including NOOP-s

# Development test (make it small, make it often)
#MAX_UNDO = 80                  # TEST

# This is a generous limit, adjust to taste.
MAX_UNDO = 10000                # REAL - Sizeof undo stack

# ------------------------------------------------------------------------
# Limit the size of undo

def     limit_undo(self2):

    xlen = len(self2.undoarr)
    if xlen == 0: return
    if xlen  <  MAX_UNDO: return
    #print "limiting undo size from", len(self2.undoarr)
    for aa in range(MAX_UNDO // 5):
        try:
            del (self2.undoarr[0])
        except:
            pass

    # Look to next boundary
    while True:
        xx, yy, mode, line = self2.undoarr[0]
        if not (mode & CONTMASK): break
        xlen = len(self2.undoarr)
        if  xlen == 0: break
        #print "boundary del at", xlen
        del (self2.undoarr[0])

    #print "limited undo size to", len(self2.undoarr)

# ------------------------------------------------------------------------
# The undo information is maintained in the array of tuples called 'undoarr'.
# We save current location (x and y), transaction type and the old line.
# The undo stack and redo stack are filled in a complimentarily fashion.
# (walk undo - fill redo -- walk redo - fill undo)
# Because the way they are designed, they can fill each other

def undo(self2, keyh):

    xlen = len(self2.undoarr)
    if xlen == 0:
        self2.mained.update_statusbar("Nothing to undo.")
        return

    while True:
        xlen = len(self2.undoarr)
        if xlen == 0: break

        xx, yy, mode, line = self2.undoarr[xlen-1]
        xx = int(xx); yy = int(yy);

        mode2 = mode & CONTMASK
        #print "undo", hex(mode), xx, yy, "line '", line, "'"

        if mode2 == MODIFIED:                   # Line change
            keyh.pad_list(self2, yy)
            self2.redoarr.append((xx, yy, mode, self2.text[yy]))
            self2.text[yy] = line
            self2.gotoxy(xx, yy)
        elif mode2 == ADDED:                    # Addition - delete
            keyh.pad_list(self2, yy)
            self2.redoarr.append((xx, yy, mode, self2.text[yy]))
            self2.gotoxy(xx, yy)
            del (self2.text[yy])
        elif mode2 == DELETED:                  # Deletion - recover
            keyh.pad_list(self2, yy)
            self2.redoarr.append((xx, yy, mode, self2.text[yy]))
            text = self2.text[:yy]
            text.append(line)
            text += self2.text[yy:]
            self2.text = text
            self2.gotoxy(xx, yy)
        elif mode2 == NOOP:                     # Place Holder
            self2.redoarr.append((xx, yy, mode, self2.text[yy]))

        else:
            # Just to confirm
            print("warning: undo - invalid mode")
            pass

        del (self2.undoarr[xlen-1])
        # Continue if cont flag is on
        if not (mode & CONTFLAG): break

    #print self2.initial_undo_size, len(self2.undoarr)
    if self2.initial_undo_size == len(self2.undoarr):
        self2.set_changed(False)
    else:
        self2.set_changed(True)

    self2.invalidate()
    self2.mained.update_statusbar("Undo %d done." % xlen)

# ------------------------------------------------------------------------

def redo(self2, keyh):

    xlen = len(self2.redoarr)
    if xlen == 0:
        self2.mained.update_statusbar("Nothing to redo.")
        return

    # reverse actions till first non CONTFLAG
    revredo = [];
    while True:
        xarridx = len(self2.redoarr)
        if xarridx == 0 : break
        xx, yy, mode, line = self2.redoarr[xarridx - 1]
        xx = int(xx); yy = int(yy);

        #print "redo", mode, "line '", line, "'"
        revredo.append((xx, yy, mode, line))
        del (self2.redoarr[xarridx - 1])

        mode2 = 0
        if len(self2.redoarr):
            xx2, yy2, mode2, line2 = self2.redoarr[len(self2.redoarr)-1]

        if not mode2 & CONTFLAG:
            break

    # Just for show
    #for xx, yy, mode, line in revredo:
    #    print "rev", mode, xx, yy, "line '", line, "'"

    while True:
        xlen2 = len(revredo)
        if xlen2 == 0: break

        xx, yy, mode, line = revredo[xlen2-1]
        mode2 = mode & CONTMASK
        #print "redo", mode2, xx, yy, "line '", line, "'"
        if mode2 == MODIFIED:                   # Line change
            keyh.pad_list(self2, yy)
            self2.undoarr.append((xx, yy, mode, self2.text[yy]))
            self2.text[yy] = line
            self2.gotoxy(xx+1, yy)

        elif mode2 == ADDED:                    # Redo Addition
            keyh.pad_list(self2, yy)
            self2.undoarr.append((xx, yy, mode, self2.text[yy]))
            text = self2.text[:yy]
            text.append(line)
            text += self2.text[yy:]
            self2.text = text
            self2.gotoxy(xx+1, yy)
        elif mode2 == DELETED:                  # Redo Deletion
            #keyh.pad_list(self2, yy)
            self2.undoarr.append((xx, yy, mode, self2.text[yy]))
            del (self2.text[yy])
        elif mode2 == NOOP:                     # Place Holder
            self2.undoarr.append((xx, yy, mode, self2.text[yy]))
        else:
            # Just to confirm
            print("warninig: redo - invalid mode")
            pass

        del (revredo[xlen2-1])

        # Continue if cont flag is on
        if not (mode & CONTFLAG):  break

    # Not true, needs to account for old changes ...
    # but it works on simple cases, and no harm comes when the flag is wrong
    if self2.initial_redo_size == len(self2.redoarr):
        self2.set_changed(False)
    #else:

    self2.invalidate()
    self2.set_changed(True)
    self2.mained.update_statusbar("Redo %d done." % xlen)

# EOF
