#!/usr/bin/env python

# Action Handler for find

from __future__ import absolute_import
from __future__ import print_function

import re, string, warnings, sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from pedlib import  pedconfig
from pedlib import  pedundo
from pedlib.pedutil import *

strhist = [] #strhist.append("aa")
stridx = 0
dialog = None

# -------------------------------------------------------------------------

def find(self, self2, replace = False):

    global stridx, dialog

    self.reptxt = ""

    warnings.simplefilter("ignore")

    entry = Gtk.Entry();
    xll = len(strhist)
    if xll:
        stridx =  xll - 1
        entry.set_text(strhist[stridx]);
    #print ("stridx", stridx)

    if replace:
        head = "pyedpro: Find / Replace"
    else:
        head = "pyedpro: Find in text"

    dialog = Gtk.Dialog(head,
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)
    dialog.replace = replace
    dialog.set_position(Gtk.WindowPosition.CENTER)

    try:
        dialog.set_icon_from_file(get_img_path("pyedpro_sub.png"))
    except:
        print("Cannot load find dialog icon", sys.exc_info())

    self.dialog = dialog

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    dialog.entry = entry
    entry.set_activates_default(True)

    if  self2.oldsearch == "":
            self2.oldsearch = pedconfig.conf.sql.get_str("src")

            if  self2.oldsearch == None:
                self2.oldsearch = ""

    if  self2.oldrep == "":
            self2.oldrep = pedconfig.conf.sql.get_str("rep")

            if  self2.oldrep == None:
                self2.oldrep = ""

    # See if we have a selection for search
    if self2.xsel != -1:
        xssel = min(self2.xsel, self2.xsel2)
        xesel = max(self2.xsel, self2.xsel2)
        yssel = min(self2.ysel, self2.ysel2)
        yesel = max(self2.ysel, self2.ysel2)

        if yssel == yesel:
            self2.oldsearch = self2.text[yssel][xssel:xesel]

    entry.set_text(self2.oldsearch)

    #dialog.vbox.pack_start(label4, 0, 0, 0)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(entry, True, True, 0)
    hbox2.pack_start(label7, 0, 0, 0)

    dialog.vbox.pack_start(Gtk.Label("Alt_Left / Alt_Right -> History Left/Right"), 0, 0 , 4)
    dialog.vbox.pack_start(Gtk.Label("Alt_1->C_Func Alt_2->Py_Def Alt_3->Asm_Lab Alt_4->Def"), 0, 0, 4)

    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.checkbox = Gtk.CheckButton.new_with_mnemonic("Use _regular expression")
    dialog.checkbox2 = Gtk.CheckButton.new_with_mnemonic("Case In_sensitive")

    dialog.vbox.pack_start(label5, 0, 0, 0)

    hbox = Gtk.HBox()
    hbox.pack_start(label1, 0, 0, 0)
    hbox.pack_start(dialog.checkbox, 0, 0, 0)
    hbox.pack_start(label2, 0, 0, 0)
    hbox.pack_start(dialog.checkbox2, 0, 0, 0)
    hbox.pack_start(label3, 0, 0, 0)

    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label8, 0, 0, 0)

    label30 = Gtk.Label("   ");  label31 = Gtk.Label("   ")
    label32 = Gtk.Label("   ");  label33 = Gtk.Label("   ")
    #label34 = Gtk.Label("   ");  label35 = Gtk.Label("   ")

    dialog.checkbox3 = Gtk.CheckButton.new_with_mnemonic("Search _All Buffers")
    dialog.checkbox4 = Gtk.CheckButton.new_with_mnemonic("Search _Files")
    dialog.checkbox4.set_tooltip_text("Search files in current dir")
    dialog.checkbox5 = Gtk.CheckButton.new_with_mnemonic("Search _Extended")
    dialog.checkbox5.set_tooltip_text("Recurse into one level of subdir")

    dialog.checkbox.set_active(pedconfig.conf.sql.get_int("regex"))
    dialog.checkbox2.set_active(pedconfig.conf.sql.get_int("nocase"))
    dialog.checkbox3.set_active(pedconfig.conf.sql.get_int("allbuf"))
    #dialog.checkbox4.set_active(pedconfig.conf.sql.get_int("allfil"))

    hbox4 = Gtk.HBox()
    hbox4.pack_start(label30, 0, 0, 0);
    hbox4.pack_start(dialog.checkbox3, 0, 0, 0)
    hbox4.pack_start(label31, 0, 0, 0);
    hbox4.pack_start(dialog.checkbox4, 0, 0, 0)
    hbox4.pack_start(dialog.checkbox5, 0, 0, 0)
    hbox4.pack_start(label32, 0, 0, 0);
    dialog.vbox.pack_start(hbox4, 0, 0, 0)
    dialog.vbox.pack_start(label33, 0, 0, 0)

    if replace:
        dialog.repl = Gtk.Entry();  dialog.repl.set_text(self2.oldrep)
        dialog.repl.set_activates_default(True)
        label10 = Gtk.Label("   ");  label11 = Gtk.Label("   ")
        label12 = Gtk.Label("   ");  label13 = Gtk.Label("   ")
        hbox3 = Gtk.HBox()
        hbox3.pack_start(label10, 0, 0, 0)
        hbox3.pack_start(dialog.repl, True, True, 0)
        hbox3.pack_start(label11, 0, 0, 0)
        dialog.vbox.pack_start(hbox3, 0, 0, 0)
        dialog.vbox.pack_start(label12, 0, 0, 0)

    dialog.connect("key-press-event", find_keypress)

    dialog.show_all()
    response = dialog.run()
    self2.oldsearch = entry.get_text()
    self.srctxt = entry.get_text()
    if replace:
        self.reptxt = dialog.repl.get_text()

    if len(strhist):
        if strhist[len(strhist)-1] != self.srctxt:
            strhist.append(self.srctxt)
    else:
        strhist.append(self.srctxt)

    #print("post", strhist)

    warnings.simplefilter("default")
    dialog.destroy()

    if response != Gtk.ResponseType.ACCEPT:
        return

    if  dialog.checkbox4.get_active() or dialog.checkbox5.get_active():
        #print("Searching all files")
        #dialog.checkbox2.set_active(False)      # Force case sensitive
        dialog.checkbox3.set_active(False)       # Force one
        find_show_file(self, self2, dialog )

    elif dialog.checkbox3.get_active():
        nn = self2.mained.notebook.get_n_pages();
        cnt = 0; cnt2 = 0
        while True:
            if cnt >= nn: break
            ppp = self2.mained.notebook.get_nth_page(cnt)
            self.xnum = cnt * 4
            find_show(self, ppp.area)
            cnt += 1
    else:
        self.xnum = 0
        find_show(self, self2)

#// -----------------------------------------------------------------------
#// Find history

def load_find_history(flag):

    global strhist

    if flag:
        cnt = 0
        for aa in strhist:
            strx = "hist%d" % cnt
            if strhist[cnt]:
                pedconfig.conf.sql.put(strx, strhist[cnt])
                #print("save find_history", strx, strhist[cnt])
            cnt+=1
    else:
        for aa in range(30):
            strx = "hist%d" % aa
            hist = pedconfig.conf.sql.get_str(strx)
            if hist:
                strhist.append(hist)
                #print("load find_history", strx, hist)

# ------------------------------------------------------------------------

def find_keypress(area, event):

    global stridx, strhist, dialog

    #print   ("find keypress", area, event)
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.state  & Gdk.ModifierType.MOD1_MASK:
            #print("stridx", stridx)
            #for aa in strhist:
            #    print (aa)
            if event.keyval == Gdk.KEY_Up or \
                    event.keyval == Gdk.KEY_Right:
                #print   ("find dlg keypress, alt UP or right key", stridx)
                if stridx < len(strhist) - 1:
                    stridx += 1
                    dialog.entry.set_text(strhist[stridx]);

            if event.keyval == Gdk.KEY_Down or \
                    event.keyval == Gdk.KEY_Left:
                #print ("find dlg keypress, alt DOWN or left", stridx)
                if stridx > 0:
                    stridx -= 1
                    dialog.entry.set_text(strhist[stridx]);

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_X or \
                    event.keyval == Gdk.KEY_x:
                    area.destroy()

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_1 or \
                    event.keyval == Gdk.KEY_1:
                    #print("find dlg keypress, Alt-1 pressed")
                    dialog.entry.set_text("^[a-z].*\(.*\)")
                    dialog.checkbox.set_active(1)
                    dialog.checkbox2.set_active(0)
                    dialog.checkbox3.set_active(0)

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_2 or \
                    event.keyval == Gdk.KEY_2:
                    #print("find dlg keypress, Alt-2 pressed")
                    dialog.entry.set_text("^def.*[a-z].*\(.*\):")
                    dialog.checkbox.set_active(1)
                    dialog.checkbox2.set_active(0)
                    dialog.checkbox3.set_active(0)

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_3 or \
                    event.keyval == Gdk.KEY_3:
                    #print("find dlg keypress, Alt-3 pressed")
                    dialog.entry.set_text("^[a-z].*:")
                    dialog.checkbox.set_active(1)
                    dialog.checkbox2.set_active(0)
                    dialog.checkbox3.set_active(0)

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_4 or \
                    event.keyval == Gdk.KEY_4:
                    #print("find dlg keypress, Alt-3 pressed")
                    dialog.entry.set_text("")
                    dialog.checkbox.set_active(0)
                    dialog.checkbox2.set_active(1)
                    dialog.checkbox3.set_active(0)

# -------------------------------------------------------------------------

def find_show(self, self2):

    #print "find_show", "'" + self.srctxt + "'" + self2.fname

    warnings.simplefilter("ignore")
    self.regex = None

    if self.srctxt == "":
        self2.mained.update_statusbar("Must specify search string.")
        return

    if self.dialog.checkbox.get_active():
        self.dialog.checkbox2.set_active(False)
        try:
            self.regex = re.compile(self.srctxt)
        except re.error as msg:
            #print  sys.exc_info()
            pedync.message("\n   Error in regular expression: \n\n"\
                            "    '%s' -- %s" % (self.srctxt, msg),\
                            None, Gtk.MESSAGE_ERROR)
            return

    win2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    #win2.set_position(Gtk.WindowPosition.CENTER)
    #win2.set_transient_for(self2.mained.mywin)
    win2.set_transient_for(None)

    try:
        win2.set_icon_from_file(get_img_path("pyedpro_sub.png"))
    except:
        print("Cannot load icon for find dialog")

    ff = os.path.basename(self2.fname)
    if self.dialog.replace:
        tit = "%s Search '%s' -- Replace '%s'" % \
            (ff, self.srctxt, self.reptxt)
    else:
        tit = "%s Searching '%s'" % (ff, self.srctxt)

    win2.set_title(tit)
    win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

    win2.connect("key-press-event", area_key, self)
    win2.connect("key-release-event", area_key, self)
    win2.connect("focus-in-event", area_focus, self, self2)
    win2.connect("unmap", area_destroy, self)

    oldxx = pedconfig.conf.sql.get_int("srcx")
    oldyy = pedconfig.conf.sql.get_int("srcy")
    oldww = pedconfig.conf.sql.get_int("srcw")
    oldhh = pedconfig.conf.sql.get_int("srch")

    #print "win2 oldconfig (x y w h) xnum", oldxx, oldyy, oldww, oldhh, self.xnum

    if True or oldww == 0 or oldhh == 0 or oldxx  == 0 or oldyy == 0:
        # Position it out of the way
        sxx, syy = self2.mained.mywin.get_position()
        wxx, wyy = self2.mained.mywin.get_size()
        myww = 3 * wxx / 8; myhh = 3 * wyy / 8
        win2.set_default_size(myww, myhh)
        #win2.move(sxx + wxx - (myww  + self.xnum), \
        #                    syy + wyy - (myhh + self.xnum))
        win2.move(sxx + wxx - (myww + 8 + self.xnum), \
                            syy + 8 + self.xnum)
    else:
        # Restore old size / location
        win2.set_default_size(oldww, oldhh)
        #win2.move(oldxx + self.xnum, oldyy + self.xnum)
        win2.move(oldxx, oldyy)

    vbox = Gtk.VBox()

    win2.treestore = None
    win2.tree = create_tree(self, win2, self.srctxt)
    win2.tree.set_headers_visible(False)
    win2.tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    hbox4 = Gtk.HBox()
    hbox4.pack_start(Gtk.Label("   "), 1, 0, 0)

    if self.dialog.replace:
        butt2 = Gtk.Button.new_with_mnemonic(" Change _One ")
        butt2.connect("clicked", chg_one, self, self2, win2)
        butt3 = Gtk.Button.new_with_mnemonic(" Change _Selected ");
        butt3.connect("clicked", chg_sel, self, self2, win2)
        butt4 = Gtk.Button.new_with_mnemonic(" Change _All ");
        butt4.connect("clicked", chg_all, self, self2, win2)
        hbox4.pack_start(butt2, 0, 0, 4)
        hbox4.pack_start(butt3, 0, 0, 4)
        hbox4.pack_start(butt4, 0, 0, 4)
    else:
        butt2 = Gtk.Button.new_with_mnemonic(" _Copy all to clipboard")
        butt2.connect("clicked", cp_all, self, self2, win2)
        #butt3 = Gtk.Button.new_with_mnemonic(" No op button");
        #butt3.connect("clicked", cp_all, self, self2, win2)
        #butt4 = Gtk.Button.new_with_mnemonic(" Unallocated button ");
        #butt4.connect("clicked", cp_all, self, self2, win2)
        hbox4.pack_start(butt2, 0, 0, 2)

    hbox4.pack_start(Gtk.Label("   "), 1, 0, 2)

    #vbox.pack_start(Gtk.Label("   "), 0, 0, 0)
    vbox.pack_start(hbox4, 0, 0, 4)
    #vbox.pack_start( Gtk.Label("   "), 0, 0, 0)

    #lab4a = Gtk.Label(" Alt-C to copy all  ");
    #vbox.pack_start(lab4a, 0, 0, 0)

    #self.tree.connect("row-activated",  tree_sel, self, self2)
    win2.tree.connect("cursor-changed",  tree_sel_row, self, self2)

    stree = Gtk.ScrolledWindow()
    stree.add(win2.tree)
    vbox.pack_start(stree, True, True, 0)

    win2.add(vbox)

    # ---------------------------------------------------------------------
    # The actual search is done in the document

    was, cnt2, before, after = self2.search(self.srctxt, self.regex,
                self.dialog.checkbox2.get_active(),
                    self.dialog.checkbox.get_active())

    update_treestore(self, win2, self2.accum, was)
    self2.mained.update_statusbar("Found %d matches. %d before %d after" \
                                          % (cnt2, before, after), True)

    pedconfig.conf.sql.put("src", self.srctxt)
    pedconfig.conf.sql.put("regex", self.dialog.checkbox.get_active())
    pedconfig.conf.sql.put("nocase", self.dialog.checkbox2.get_active())
    pedconfig.conf.sql.put("allbuf", self.dialog.checkbox3.get_active())
    pedconfig.conf.sql.put("allfil", self.dialog.checkbox4.get_active())

    if self.reptxt != "":
        pedconfig.conf.sql.put("rep", self.reptxt)

    win2.tree.grab_focus()
    #warnings.simplefilter("ignore")

    #print("cnt2:", cnt2)
    # close if multiselect and no hits
    if self.dialog.checkbox3.get_active():
        if cnt2 == 0:
            #print ("closing this one")
            win2.destroy()
            self2.mained.update_statusbar("Window closed on no matches.")
        else:
            win2.show_all()
    else:
        win2.show_all()


# ------------------------------------------------------------------------

def find_show_file(self, self2, dialog):

    #print "find_show", "'" + self.srctxt + "'" + self2.fname

    global matchfiles

    casex = dialog.checkbox2.get_active()
    recurse = dialog.checkbox5.get_active()

    matchfiles = []
    warnings.simplefilter("ignore")
    self.regex = None

    if self.srctxt == "":
        self2.mained.update_statusbar("Must specify search string.")
        return

    if self.dialog.checkbox.get_active():
        self.dialog.checkbox2.set_active(False)
        try:
            self.regex = re.compile(self.srctxt)
        except re.error as msg:
            #print  sys.exc_info()
            pedync.message("\n   Error in regular expression: \n\n"\
                            "    '%s' -- %s" % (self.srctxt, msg),\
                            None, Gtk.MESSAGE_ERROR)
            return

    win2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    win2.set_position((Gtk.WindowPosition.CENTER))

    #win2.set_transient_for(self2.mained.mywin)
    win2.set_transient_for(None)

    try:
        win2.set_icon_from_file(get_img_path("pyedpro_sub.png"))
    except:
        print("Cannot load icon for find dialog")

    ff = os.path.basename(self2.fname)
    dd = os.getcwd()
    if len(dd) > 24:
        dd = " ... " + dd[-24:]

    tit = "Searching '%s' for '%s'" % (dd, self.srctxt)

    win2.set_title(tit)
    win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

    win2.connect("key-press-event", area_key2, self, win2)
    win2.connect("key-release-event", area_key2, self, win2)
    win2.connect("focus-in-event", area_focus, self, self2)
    win2.connect("unmap", area_destroy, self)

    '''
    oldxx = pedconfig.conf.sql.get_int("srcx")
    oldyy = pedconfig.conf.sql.get_int("srcy")
    oldww = pedconfig.conf.sql.get_int("srcw")
    oldhh = pedconfig.conf.sql.get_int("srch")
    '''

    #print "win2 oldconfig (x y w h) xnum", oldxx, oldyy, oldww, oldhh, self.xnum

    if True or oldww == 0 or oldhh == 0 or oldxx  == 0 or oldyy == 0:
        # Position it out of the way
        sxx, syy = self2.mained.mywin.get_position()
        wxx, wyy = self2.mained.mywin.get_size()
        myww = 5 * wxx / 8; myhh = 5 * wyy / 8
        win2.set_default_size(myww, myhh)
        #win2.move(sxx + wxx - (myww  + self.xnum), \
        #                    syy + wyy - (myhh + self.xnum))
    else:
        # Restore old size / location
        win2.set_default_size(oldww, oldhh)
        #win2.move(oldxx + self.xnum, oldyy + self.xnum)
        win2.move(oldxx, oldyy)

    vbox = Gtk.VBox()

    win2.treestore = None
    win2.tree = create_tree(self, win2, self.srctxt)
    win2.tree.set_headers_visible(False)
    win2.tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    hbox = Gtk.HBox()
    lab4 = Gtk.Label("  ");
    hbox.pack_start(lab4, 1,0,0)
    butt = Gtk.Button("Load All Matched Files")
    butt.connect("clicked", loadfiles, win2.tree)
    hbox.pack_start(butt, 0,0,0)
    lab4a = Gtk.Label("  ");
    hbox.pack_start(lab4a, 1,0,0)
    vbox.pack_start(hbox, 0, 0, 4)

    win2.tree.connect("row-activated",   tree_sel2, self, self2, win2)
    win2.tree.connect("cursor-changed",  tree_sel_row2, self, self2)
    #win2.connect("unmap", area_destroy, self)

    stree = Gtk.ScrolledWindow()
    stree.add(win2.tree)
    vbox.pack_start(stree, True, True, 0)
    win2.add(vbox)

    ddd = []; ddd3 = []
    # What not to search
    filter = [".pyc", ".exe", ".obj", ".o", ".elf", ".bin", ".jpg",
                    ".png", ".svg", ".old", ".pickle", ".lst", ]
    ddd2 = os.listdir(".")
    for aa in ddd2:
        # Filter the obvious candidates:
        extx = os.path.splitext(aa)[1]
        if not extx in filter :
            ddd.append(aa)

    flist = []
    matches = 0

    for filename in ddd:
        if filename[0] == ".":
            continue
        if os.path.isfile(filename):
            flist.append(filename)
        elif os.path.isdir(filename):
            if recurse:
                #print("Dir: ", filename)
                ddd4 = os.listdir(filename)
                for bb in ddd4:
                    nnn = filename + os.sep + bb
                    if os.path.isfile(nnn):
                        # Filter the obvious candidates:
                        extx = os.path.splitext(nnn)[1]
                        if not extx in filter:
                            flist.append(nnn)
        else:
            print("Skipped searching: ", filename)
            pass

    #print("flist", flist)

    for filename in flist:
        filestat = os.stat(filename)
        #print("stat", filestat)
        if filestat.st_size < 100000:
            #print("Seaching: ", filename)
            rrr = findinfile(self.srctxt, filename, casex)
            if rrr:
                matches += 1
                #print ("found: rrr", rrr, )
                #ddd3.append(rrr)
                matchfiles.append(filename)
                ddd3.append("%s matches %s times" % (filename, len(rrr)) )
                # Limit finds:
                lim = 5
                for aa in rrr:
                    ddd3.append("         %s" % aa)
                    if lim == 0:
                        break
                    lim = lim - 1
        else:
            if pedconfig.conf.verbose:
                print("Not searching large file:", filename)

    # ---------------------------------------------------------------------
    #was, cnt2 = self2.search(self.srctxt, self.regex, self.dialog.checkbox2.get_active(),
    #                self.dialog.checkbox.get_active())

    update_treestore(self, win2, ddd3, 0)

    self2.mained.update_statusbar("Found %d matching files total of %d matches."
                                        % (matches, len(ddd3)), True)

    pedconfig.conf.sql.put("src", self.srctxt)
    pedconfig.conf.sql.put("regex", self.dialog.checkbox.get_active())
    pedconfig.conf.sql.put("nocase", self.dialog.checkbox2.get_active())
    pedconfig.conf.sql.put("allbuf", self.dialog.checkbox3.get_active())
    pedconfig.conf.sql.put("allfil", self.dialog.checkbox4.get_active())

    if self.reptxt != "":
        pedconfig.conf.sql.put("rep", self.reptxt)

    win2.tree.grab_focus()
    #warnings.simplefilter("ignore")
    win2.show_all()

def loadfiles(butt, tree):
    #print("loading files", butt, tree)
    global matchfiles
    for aa in matchfiles:
        #print("Match", aa)
        pedconfig.conf.pedwin.openfile(aa)

# ------------------------------------------------------------------------

def area_destroy(win2, self):

    '''# What a mess ... getting window coordinates. Fulile attempts below
    oldxx, oldyy = win2.get_position()
    oldww, oldhh = win2.get_size()
    #print "old save coord", oldxx, oldyy, oldww, oldhh

    xx,yy,ww,hh = win2.get_allocation()
    #print "save alloc", xx, yy, ww, hh

    aa,bb,cc,dd,ee = Gtk.gdk.Window.get_geometry(win2.window)
    #print "save geom",aa,bb,cc,dd'''

    # Finally, gdk delivers an up to date position
    oldxx, oldyy = win2.get_position()
    oldww, oldhh = win2.get_size()
    #print "save coord", oldxx, oldyy, oldww, oldhh

    pedconfig.conf.sql.put("srcx", oldxx)
    pedconfig.conf.sql.put("srcy", oldyy)
    pedconfig.conf.sql.put("srcw", oldww)
    pedconfig.conf.sql.put("srch", oldhh)

'''
# -------------------------------------------------------------------------
# Locate line:

def src_line2(self, self2, line, cnt):

    idx = 0; idx2 = 0;
    mlen = len(self.srctxt)
    accum = []

    while True:
        if self.dialog.checkbox2.get_active():
            idx = line.lower().find(self.srctxt.lower(), idx)
            idx2 = idx
        elif self.dialog.checkbox.get_active():
            line2 = line[idx:]
            #print "line2", line2
            if line2 == "":
                idx = -1
                break
            res = self.regex.search(line2)
            #print res, res.start(), res.end()
            if res:
                idx = res.start() + idx
                # Null match, ignore it ('*' with zero length match)
                if res.end() == res.start():
                    #print "null match", idx, res.start(), res.end()
                    # Proceed no matter what
                    if res.end() != 0:
                        idx = res.end() + 1
                    else:
                         idx += 1
                    continue

                idx2 = res.end() + idx
                mlen = res.end() - res.start()
                #print "match", line2[res.start():res.end()]
            else:
                idx = -1
                break
        else:
            idx = line.find(self.srctxt, idx)
            idx2 = idx

        if  idx >= 0:
            line2 =  str(idx) + ":"  + str(cnt) +\
                     ":" + str(mlen) + " " + line
            #cnt2 += 1
            #self2.accum.append(line2)
            accum.append(line2)
            idx = idx2 + 1
        else:
            break

    return accum
'''

# -------------------------------------------------------------------------

def tree_sel_row(xtree, self, self2):

    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected_rows()
    # In muti selection, only process first
    for aa in xiter:
        xstr = xmodel.get_value(xmodel.get_iter(aa), 0)
        #print "Selected:", xstr
        break

    # Get back numbers (the C++ way)
    #idx = xstr.find(":");          xxx = xstr[:idx]
    #idx2 = xstr.find(":", idx+1);  yyy = xstr[idx+1:idx2]
    #idx3 = xstr.find(" ", idx2+1); mlen = xstr[idx2+1:idx3]

    # Get back numbers the python way
    try:
        bb = xstr.split(" ")[0].split(":")
    except:
        pass

    # Confirm results:
    # print "TREE sel", bb

    try:
        if int(bb[2]) == 0:
            bb[2] = 1
        self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
        self2.walk_func()
    except:
        pass

def tree_sel2(xtree, self, self2, par1, par2, par3):

    #print( self2, par1, par2, par3)

    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected_rows()
    # In muti selection, only process first
    for aa in xiter:
        xstr = xmodel.get_value(xmodel.get_iter(aa), 0)
        #print ("selSelected:", xstr)
        if xstr[0] != " ":
            idx = str.find(xstr, " matches")
            #print ("Selected: '%s'" % xstr[:idx] )
            rrr = pedconfig.conf.pedwin.openfile(xstr[:idx])
            print (rrr)
            par3.destroy()
        break
    pass

def tree_sel_row2(xtree, self, self2):

    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected_rows()
    # In muti selection, only process first
    for aa in xiter:
        xstr = xmodel.get_value(xmodel.get_iter(aa), 0)
        #print ("Selected:", xstr)
        break

    # Get back numbers (the C++ way)
    #idx = xstr.find(":");          xxx = xstr[:idx]
    #idx2 = xstr.find(":", idx+1);  yyy = xstr[idx+1:idx2]
    #idx3 = xstr.find(" ", idx2+1); mlen = xstr[idx2+1:idx3]

    # Get back numbers the python way
    try:
        bb = xstr.split(" ")[0].split(":")
    except:
        pass

    # Confirm results:
    # print "TREE sel", bb

    try:
        #self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
        pass
    except:
        pass

# Focus on the current window
def area_focus(area, event, self, self2):
    #print "area_focus"
    nn = self2.notebook.get_n_pages();
    for aa in range(nn):
        vcurr = self2.notebook.get_nth_page(aa)
        if vcurr.area == self2:
            self2.notebook.set_current_page(aa)
            self2.mained.mywin.set_focus(vcurr.area)

# ------------------------------------------------------------------------
# Call key handler

def area_key(area, event, self):

    #print("area_key", event)

    # Do key down:
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            area.destroy()

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Return:
            #print "Ret"
            area.destroy()

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            self.alt = True;

        if event.keyval >= Gdk.KEY_1 and \
                event.keyval <= Gdk.KEY_9:
            pass
            #print("pedwin Alt num", event.keyval - Gdk.KEY__1)

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if self.alt:
                area.destroy()

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            self.alt = False;

# ------------------------------------------------------------------------
# Call key handler

def area_key2(area, event, self, win2):

    #print "area_key", event
    # Do key down:
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            area.destroy()

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Return:

            ''' root = win2.treestore.get_iter_first()
            while root is not None:
                xstr = win2.tree.get_model().get_value(root, 0)
                print (root, xstr)
                root = win2.treestore.iter_next(root) '''

            #print ("Ret key")
            sel = win2.tree.get_selection()
            xstr = ""
            xmodel, xiter = sel.get_selected_rows()
            # In muti selection, only process first
            for aa in xiter:
                xstr = xmodel.get_value(xmodel.get_iter(aa), 0)
                if xstr[0] == " ":
                    #print ("Please select a file name field:", xstr)
                    #pedconfig.conf.pedwin.update_statusbar(
                    #    "Please select a file name line instead of a match line.")

                    # Walk back ...
                    root =  xmodel.get_iter(aa)
                    while root is not None:
                        xstr = win2.tree.get_model().get_value(root, 0)
                        #print (root, xstr)
                        if xstr[0] != " ":
                            break
                        root = win2.treestore.iter_previous(root)
                break

            idx = str.find(xstr, " matches")
            #print ("Selected: '%s'" % xstr[:idx] )
            pedconfig.conf.pedwin.openfile(xstr[:idx])

            area.destroy()

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            self.alt = True;

        if event.keyval >= Gdk.KEY_1 and \
                event.keyval <= Gdk.KEY_9:
            pass
            #print("pedwin Alt num", event.keyval - Gdk.KEY__1)

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if self.alt:
                area.destroy()

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            self.alt = False;

# Tree handlers
def start_tree(self, win2):

    if not win2.treestore:
        win2.treestore = Gtk.TreeStore(str)

    # Delete previous contents
    try:
        while True:
            root = win2.treestore.get_iter_first()
            win2.treestore.remove(root)
    except:
        #print  sys.exc_info()
        pass

    piter = win2.treestore.append(None, ["Searching .."])
    win2.treestore.append(piter, ["None .."])

# -------------------------------------------------------------------------
def create_tree(self, win2, match, text = None):

    start_tree(self, win2)

    # create the TreeView using treestore
    tv = Gtk.TreeView(win2.treestore)
    tv.set_enable_search(True)

    # create a CellRendererText to render the data
    cell = Gtk.CellRendererText()

    # create the TreeViewColumn to display the data
    #tvcolumn = Gtk.TreeViewColumn("Matches for '" + match + "'")
    tvcolumn = Gtk.TreeViewColumn()

    # add the cell to the tvcolumn and allow it to expand
    tvcolumn.pack_start(cell, True)

    # set the cell "text" attribute to column 0 - retrieve text
    # from that column in treestore
    tvcolumn.add_attribute(cell, 'text', 0)

    # add tvcolumn to treeview
    tv.append_column(tvcolumn)

    return tv

def update_treestore(self, win2, text, was):

    #print "was", was

    # Delete previous contents
    try:
        while True:
            root = win2.treestore.get_iter_first()
            win2.treestore.remove(root)
    except:
        pass
        #print  sys.exc_info()
    if not text:
        win2.treestore.append(None, ["No Match",])
        return

    cnt = 0; piter2 = None; next = False
    try:
        for line in text:
            piter = win2.treestore.append(None, [cut_lead_space(line)])
            if next:
                next = False; piter2 = piter
            if cnt == was:
                next = True
            cnt += 1
    except:
        pass
        #print  sys.exc_info()

    if piter2:
        win2.tree.set_cursor(win2.treestore.get_path(piter2))
    else:
        root = win2.treestore.get_iter_first()
        win2.tree.set_cursor(win2.treestore.get_path(root))

# -------------------------------------------------------------------------
# Copy all hits to clipboard

def  cp_all(butt, self, self2, win2, iter = None):

    #print("Copy all to clip")
    win2.tree.get_selection().select_all()

    sel = win2.tree.get_selection()
    xmodel, xiter = sel.get_selected_rows()

    cumm  = ""
    for aa in xiter:
        iter = xmodel.get_iter(aa)
        xstr = xmodel.get_value(iter, 0)

        #print("got %s" % xstr);
        cc = xstr.split(" ")
        bb = cc[0].split(":")
        dd =  xstr[len(cc[0]) + 1:]
        #print("str '%s'" % dd);
        cumm += dd + "\n"

    disp = Gdk.Display().get_default()
    clip = Gtk.Clipboard.get_default(disp)
    clip.set_text(cumm, len(cumm))

    self2.mained.update_statusbar("Copied hits to clipboard.", True)
    win2.destroy()

# -------------------------------------------------------------------------
# Change current item in the list

def chg_one(butt, self, self2, win2, iter = None):

    single = (iter == None)
    sel = win2.tree.get_selection()
    xmodel, xiter = sel.get_selected_rows()

    for aa in xiter:
        iter = xmodel.get_iter(aa)
        sel.select_path(xmodel.get_path(iter))

    # Iter from wrappers?
    if iter:
        sel.select_path(xmodel.get_path(iter))
    else:
        # In muti selection, only process first
        for aa in xiter:
            iter = xmodel.get_iter(aa)
            sel.select_path(xmodel.get_path(iter))
            break

    if iter == None:
        self2.mained.update_statusbar("Nothing selected.")
        return

    if single:
        self2.undoarr.append((0, 0, pedundo.NOOP, ""))

    xstr = xmodel.get_value(iter, 0)
    bb = xstr.split(" ")[0].split(":")

    if pedconfig.conf.pgdebug > 2:
        print("ch_one", bb)

    try:
        # Is this a valid entry?
        pos = int(bb[0])
        if int(bb[2]) >= 1:
            # Is this a non null replacement?
            self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
            self.cut(self2, True, False)
            self.clip_cb(None, self.reptxt, self2, False)

            if pedconfig.conf.pgdebug > 1:
                print ("Changed to:", self2.text[int(bb[1])])

    except:
        print("Invalid change line (most likely cursor line)", sys.exc_info())
        pass

    sel.unselect_all()

    if single:
        # Re-read list. Dirty hack, but makes it cleaner
        was, cnt2 = self2.search(self.srctxt, self.regex, self.dialog.checkbox2.get_active(),
                    self.dialog.checkbox.get_active())
        update_treestore(self, win2, self2.accum, was-1)

    return next

# -------------------------------------------------------------------------
#

def chg_all(butt, self, self2, win2):
    win2.tree.get_selection().select_all()
    chg_sel(butt, self, self2, win2)

def chg_sel(butt, self, self2, win2):
    iters = []; cnt2 = 0
    sel = win2.tree.get_selection()
    xmodel, xiter = sel.get_selected_rows()

    # Create a list of changes
    for aa in xiter:
        iter = xmodel.get_iter(aa)
        iters.append(iter)

    sel.unselect_all()
    self2.undoarr.append((0, 0, pedundo.NOOP, ""))

    # Change in reverse order, so we do not create gaps
    iters.reverse()
    for iter in iters:
        chg_one(butt, self, self2, win2, iter)
        if cnt2 % 10 == 0:
            usleep(1)
        cnt2 += 1
    self2.mained.update_statusbar("Changed %d items" % cnt2)
    win2.destroy()

def wclose(butt,self):
    #print "xclose"
    pass

def wprev(butt,self):
    #print "wprev"
    pass

def wnext(butt,self):
    #print "wnext"
    pass

# EOF
