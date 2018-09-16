#!/usr/bin/env python

# Action Handler for find

import re, string

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject


import peddoc, pedync, pedconfig
from pedutil import *
from pedundo import *

strhist = []
stridx = 0
myentry = None

# -------------------------------------------------------------------------
                                    
def find(self, self2, replace = False):

    global myentry
    self.reptxt = ""
        
    if replace:
        head = "pyedit: Find / Replace"
    else:
        head = "pyedit: Find in text"
    
    dialog = gtk.Dialog(head,
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(gtk.RESPONSE_ACCEPT)
    dialog.replace = replace
    dialog.set_position(gtk.WIN_POS_CENTER)
    try:
        dialog.set_icon_from_file(get_img_path("pyedit_sub.png"))
    except:
        print "Cannot load find dialog icon", sys.exc_info()
        
    self.dialog = dialog
    
    # Spacers
    label1 = gtk.Label("   ");  label2 = gtk.Label("   ") 
    label3 = gtk.Label("   ");  label4 = gtk.Label("   ") 
    label5 = gtk.Label("   ");  label6 = gtk.Label("   ") 
    label7 = gtk.Label("   ");  label8 = gtk.Label("   ") 

    warnings.simplefilter("ignore")
    entry = gtk.Entry(); 
    myentry = entry
    warnings.simplefilter("default")
    
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
    dialog.vbox.pack_start(label4)  

    hbox2 = gtk.HBox()
    hbox2.pack_start(label6, False)  
    hbox2.pack_start(entry)  
    hbox2.pack_start(label7, False)  

    dialog.vbox.pack_start(hbox2)

    dialog.checkbox = gtk.CheckButton("Use _regular expression")
    dialog.checkbox2 = gtk.CheckButton("Case In_sensitive")
    
    dialog.checkbox.set_active(pedconfig.conf.sql.get_int("regex"))
    dialog.checkbox2.set_active(pedconfig.conf.sql.get_int("nocase"))
                
    dialog.vbox.pack_start(label5)  

    hbox = gtk.HBox()
    hbox.pack_start(label1);  hbox.pack_start(dialog.checkbox)
    hbox.pack_start(label2);  hbox.pack_start(dialog.checkbox2)
    hbox.pack_start(label3);  
    dialog.vbox.pack_start(hbox)
    dialog.vbox.pack_start(label8)  

    label30 = gtk.Label("   ");  label31 = gtk.Label("   ") 
    label32 = gtk.Label("   ");  label33 = gtk.Label("   ") 
    label34 = gtk.Label("   ");  label35 = gtk.Label("   ") 
    
    dialog.checkbox3 = gtk.CheckButton("Search _All Buffers")
    #dialog.checkbox4 = gtk.CheckButton("Hello")
    hbox4 = gtk.HBox()
    hbox4.pack_start(label30);  hbox4.pack_start(dialog.checkbox3)
    #hbox4.pack_start(label31);  hbox4.pack_start(dialog.checkbox4)
    hbox4.pack_start(label32);  
    dialog.vbox.pack_start(hbox4)
    dialog.vbox.pack_start(label33)  
    
    if replace:    
        dialog.repl = gtk.Entry();  dialog.repl.set_text(self2.oldrep)
        dialog.repl.set_activates_default(True)
        label10 = gtk.Label("   ");  label11 = gtk.Label("   ") 
        label12 = gtk.Label("   ");  label13 = gtk.Label("   ") 
        hbox3 = gtk.HBox()
        hbox3.pack_start(label10, False)  
        hbox3.pack_start(dialog.repl)  
        hbox3.pack_start(label11, False)  
        dialog.vbox.pack_start(hbox3)  
        dialog.vbox.pack_start(label12)          
      
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
        
    dialog.destroy()

    if response != gtk.RESPONSE_ACCEPT:   
        return

    if  dialog.checkbox3.get_active():
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
    
            
def find_keypress(area, event):
    global stridx, strhist, myentry
    #print   "find keypress", area, event
    if  event.type == gtk.gdk.KEY_PRESS:
        if event.state  & gtk.gdk.MOD1_MASK:
            if event.keyval == gtk.keysyms.Up or \
                    event.keyval == gtk.keysyms.Right:
                #print   "find keypress, alt UP or left key"
                if stridx < len(strhist) -1:
                    stridx += 1
                    myentry.set_text(strhist[stridx]);
                    
            if event.keyval == gtk.keysyms.Down or \
                    event.keyval == gtk.keysyms.Left:
                #print   "find keypress, alt DOWN or right key"
                if stridx > 0:
                    stridx -= 1
                    myentry.set_text(strhist[stridx]);
            
# -------------------------------------------------------------------------
    
def find_show(self, self2):

    #print "find_show", "'" + self.srctxt + "'" + self2.fname

    self.regex = None
    
    if self.srctxt == "":
        self2.mained.update_statusbar("Must specify search string")
        return          
        
    if self.dialog.checkbox.get_active():
        self.dialog.checkbox2.set_active(False)
        try:
            self.regex = re.compile(self.srctxt)
        except re.error, msg:
            #print  sys.exc_info()        
            pedync.message("\n   Error in regular expression: \n\n"\
                            "    '%s' -- %s" % (self.srctxt, msg),\
                            None, gtk.MESSAGE_ERROR)
            return                    

    win2 = gtk.Window()
    #win2.set_position(gtk.WIN_POS_CENTER)
    try:
        win2.set_icon_from_file(get_img_path("pyedit_sub.png"))
    except:
        print "Cannot load icon"
    
    ff = os.path.basename(self2.fname)        
    if self.dialog.replace:
        tit = "%s Search '%s' -- Replace '%s'" % \
            (ff, self.srctxt, self.reptxt)
    else:
        tit = "%s Searching '%s'" % (ff, self.srctxt)        
                
    win2.set_title(tit)
    
    win2.set_events(    
                    gtk.gdk.POINTER_MOTION_MASK |
                    gtk.gdk.POINTER_MOTION_HINT_MASK |
                    gtk.gdk.BUTTON_PRESS_MASK |
                    gtk.gdk.BUTTON_RELEASE_MASK |
                    gtk.gdk.KEY_PRESS_MASK |
                    gtk.gdk.KEY_RELEASE_MASK |
                    gtk.gdk.FOCUS_CHANGE_MASK )

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
        sxx, syy = self2.mained.window.get_position()
        wxx, wyy = self2.mained.window.get_size()
        myww = 3 * wxx / 8; myhh = 3 * wyy / 8
        win2.set_default_size(myww, myhh)
        win2.move(sxx + wxx - (myww  + self.xnum), \
                            syy + wyy - (myhh + self.xnum))        
    else:
        # Restore old size / location
        win2.set_default_size(oldww, oldhh)
        #win2.move(oldxx + self.xnum, oldyy + self.xnum)        
        win2.move(oldxx, oldyy)        
	    
    vbox = gtk.VBox()
            
    win2.treestore = None
    win2.tree = create_tree(self, win2, self.srctxt)
    win2.tree.set_headers_visible(False)
    win2.tree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
    if self.dialog.replace:
        butt2 = gtk.Button(" Change _One ")
        butt2.connect("clicked", chg_one, self, self2, win2)
        butt3 = gtk.Button(" Change _Selected "); 
        butt3.connect("clicked", chg_sel, self, self2, win2)
        butt4 = gtk.Button(" Change _All "); 
        butt4.connect("clicked", chg_all, self, self2, win2)
        
        lab1 = gtk.Label("   "); lab2 = gtk.Label("   ");
        
        hbox4 = gtk.HBox()
        hbox4.pack_start(lab1)
        hbox4.pack_start(butt2, False)
        hbox4.pack_start(butt3, False)
        hbox4.pack_start(butt4, False)
        hbox4.pack_start(lab2)
    
        lab3 = gtk.Label("   "); 
        
        vbox.pack_start(lab3, False)           
        vbox.pack_start(hbox4, False)           
        
    lab4 = gtk.Label("   ");
    vbox.pack_start(lab4, False)           
    
    #self.tree.connect("row-activated",  tree_sel, self, self2)
    win2.tree.connect("cursor-changed",  tree_sel_row, self, self2)

    stree = gtk.ScrolledWindow()
    stree.add(win2.tree)
    vbox.pack_start(stree)           
                            
    win2.add(vbox)
    win2.show_all()
    
    # ---------------------------------------------------------------------
    was, cnt2 = self2.search(self.srctxt, self.regex, self.dialog.checkbox2.get_active(), 
                    self.dialog.checkbox.get_active())
        
    update_treestore(self, win2, self2.accum, was)
    self2.mained.update_statusbar("Found %d matches." % cnt2)
            
    pedconfig.conf.sql.put("src", self.srctxt)                
    pedconfig.conf.sql.put("regex", self.dialog.checkbox.get_active())
    pedconfig.conf.sql.put("nocase", self.dialog.checkbox2.get_active())
    
    if self.reptxt != "":       
        pedconfig.conf.sql.put("rep", self.reptxt)
                    
    win2.tree.grab_focus()

def area_destroy(win2, self):

    '''# What a mess ... getting window coordinates. Fulile attempts below
    oldxx, oldyy = win2.get_position()
    oldww, oldhh = win2.get_size()
    #print "old save coord", oldxx, oldyy, oldww, oldhh     
    
    xx,yy,ww,hh = win2.get_allocation()
    #print "save alloc", xx, yy, ww, hh     
    
    aa,bb,cc,dd,ee = gtk.gdk.Window.get_geometry(win2.window) 
    #print "save geom",aa,bb,cc,dd'''

    # Finally, gdk delivers an up to date position    
    oldxx, oldyy = gtk.gdk.Window.get_position(win2.window) 
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
        self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
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
            self2.mained.window.set_focus(vcurr.area)
    
# Call key handler
def area_key(area, event, self):

    #print "area_key", event
    # Do key down:
    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Escape:
            #print "Esc"
            area.destroy()

    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Return:
            #print "Ret"
            area.destroy()

        if event.keyval == gtk.keysyms.Alt_L or \
                event.keyval == gtk.keysyms.Alt_R:
            self.alt = True;
    
        if event.keyval >= gtk.keysyms._1 and \
                event.keyval <= gtk.keysyms._9:
            pass
            #print "pedwin Alt num", event.keyval - gtk.keysyms._1
        
        if event.keyval == gtk.keysyms.x or \
                event.keyval == gtk.keysyms.X:
            if self.alt:
                area.destroy()
                                  
    elif  event.type == gtk.gdk.KEY_RELEASE:
        if event.keyval == gtk.keysyms.Alt_L or \
              event.keyval == gtk.keysyms.Alt_R:
            self.alt = False;

# Tree handlers
def start_tree(self, win2):

    if not win2.treestore:
        win2.treestore = gtk.TreeStore(str)
    
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
    tv = gtk.TreeView(win2.treestore)
    tv.set_enable_search(True)

    # create a CellRendererText to render the data
    cell = gtk.CellRendererText()

    # create the TreeViewColumn to display the data
    #tvcolumn = gtk.TreeViewColumn("Matches for '" + match + "'")
    tvcolumn = gtk.TreeViewColumn()

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
# Change current item in the list    

def chg_one(butt, self, self2, win2, iter = None):

    single = (iter == None)
    sel = win2.tree.get_selection()        
    xmodel, xiter = sel.get_selected_rows()
    
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
        self2.mained.update_statusbar("Nothing selected")        
        return
    
    if single:
        self2.undoarr.append((0, 0, NOOP, ""))
      
    xstr = xmodel.get_value(iter, 0)    
    bb = xstr.split(" ")[0].split(":")
    
    #print "ch_one", bb    
    self2.gotoxy(int(bb[0]), int(bb[1]), int(bb[2]), True)
    self.cut(self2, True, False)
    self.clip_cb(None, self.reptxt, self2, False)
                        
    newstr = self2.text[int(bb[1])]
    #print "newstr", newstr
                          
    sel.unselect_all()
    
    if single:
        # Re-read list. Dirty hack, but makes it cleaner
        was, cnt2 = self2.search(self.srctxt, self.regex, self.dialog.checkbox2.get_active(), 
                    self.dialog.checkbox.get_active())
        update_treestore(self, win2, self2.accum, was-1)
    
    return next

# -------------------------------------------------------------------------

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
    self2.undoarr.append((0, 0, NOOP, ""))
    
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
    
   





































































