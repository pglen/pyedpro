#!/usr/bin/env python

# Action Handler for find

import time, os, re, string, warnings
import  gtk

def ofd(fname = None):

    dialog = gtk.Dialog("pyedit: Open File",
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                    
    dialog.set_default_response(gtk.RESPONSE_ACCEPT)
    dialog.set_position(gtk.WIN_POS_CENTER)
    
    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)

    dialog.set_default_size(800, 600)

    # Spacers
    label1  = gtk.Label("   ");  label2 = gtk.Label("   ") 
    label3  = gtk.Label("   ");  label4 = gtk.Label("   ") 
    label5  = gtk.Label("   ");  label6 = gtk.Label("   ") 
    label7  = gtk.Label("   ");  label8 = gtk.Label("   ") 
    label10 = gtk.Label("   ");  
    
    dialog.label11 = gtk.Label("   ") 
    dialog.label12 = gtk.Label("   ") 

    dialog.pbox = gtk.HBox()
    fill_path(dialog)
   
    dialog.vbox.pack_start(label4, False)  
    dialog.vbox.pack_start(dialog.pbox, False)  
    dialog.vbox.pack_start(label10, False)  
    
    warnings.simplefilter("ignore")
    dialog.entry = gtk.Entry(); 
    warnings.simplefilter("default")
    
    dialog.entry.set_activates_default(True)
    dialog.entry.set_text(fname)
    
    hbox2 = gtk.HBox()
    hbox2.pack_start(label6, False)  
    hbox2.pack_start(dialog.entry)  
    hbox2.pack_start(label7, False)  
  
    dialog.vbox.pack_start(hbox2, False)
    dialog.vbox.pack_start(label8, False)  

    dialog.ts = gtk.ListStore(str, str, str, str)
    tview = create_ftree(dialog.ts)
            
    scroll = gtk.ScrolledWindow()
    
    tview.connect("row-activated",  tree_sel, dialog)
    tview.connect("cursor-changed",  tree_sel_row, dialog)
    dialog.tview = tview

    scroll.add(tview)
    
    frame2 = gtk.Frame(); frame2.add(scroll)

    hbox3 = gtk.HBox()
    hbox3.pack_start(label1, False)  
    hbox3.pack_start(frame2)  
    hbox3.pack_start(label2, False)  
  
    dialog.vbox.pack_start(hbox3)  
    dialog.vbox.pack_start(label3, False)  
    
    dialog.show_all()
    populate(dialog)    
    dialog.set_focus(tview)    
    #dialog.set_focus(dialog.entry)
    
    response = dialog.run()   
    
    if response == gtk.RESPONSE_ACCEPT:
        res = os.path.realpath(dialog.entry.get_text())
    else:
        res = ""        
    #print "response", response, "res", res    
    dialog.destroy()
    
    return res
 
def butt_click(butt, dialog):
    #print butt.path
    os.chdir(butt.path)
    populate(dialog)
      
def fill_path(dialog):

    cccc = dialog.pbox.get_children()
    for cc in cccc:
        dialog.pbox.remove(cc)
            
    cwd = os.getcwd(); 
    # Hack to detect windows:
    if cwd[1] == ":":
        darr = cwd.split("\\")    
    else:                   
        darr = cwd.split("/")    
    dialog.pbox.pack_start(dialog.label11)
    curr = ""
    for aa in darr:
        butt = gtk.Button(aa + "/")
        curr += aa + "/"; butt.path = curr
        butt.set_focus_on_click(False)
        butt.connect("clicked", butt_click, dialog)
        dialog.pbox.pack_start(butt, False)        
        
    dialog.pbox.pack_start(dialog.label12)
    dialog.show_all()
    
# ------------------------------------------------------------------------

def populate(dialog):

    fill_path(dialog)
    
    # Clear old contents:
    while True:
        root = dialog.ts.get_iter_first() 
        if not root:
            break 
        try:
            dialog.ts.remove(root)                           
        except:
            print "Exception on rm ts"

    ppp = ".."
    filestat = os.stat(ppp)
    piter = dialog.ts.append(row=None)      
    dialog.ts.set(piter, 0, ppp)
    dialog.ts.set(piter, 1, filestat.st_size)
    dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
    dialog.ts.set(piter, 3, time.ctime(filestat.st_mtime))

    ddd2 = os.listdir(".")
    #ddd = sorted(ddd2)
    ddd2.sort()
    ddd = []
    
    for aa in ddd2:
        if os.path.splitext(aa)[1] != ".pyc":
            ddd.append(aa)                                    
          
    for filename in ddd:
        if filename[0] == ".":
            continue
        if os.path.isdir(filename):
            filestat = os.stat(filename)
            piter = dialog.ts.append(row=None)      
            #dialog.ts.set(piter, 0, "["+ filename + "]")
            #print filename,
            dialog.ts.set(piter, 0, filename )
            dialog.ts.set(piter, 1, filestat.st_size)
            dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
            dialog.ts.set(piter, 3, time.ctime(filestat.st_mtime))

    for filename in ddd:
        if filename[0] == ".":
            continue
        if not os.path.isdir(filename):
            filestat = os.stat(filename)
            piter = dialog.ts.append(row=None)      
            #print filename,
            dialog.ts.set(piter, 0, filename)
            dialog.ts.set(piter, 1, filestat.st_size)
            dialog.ts.set(piter, 2, mode2str(filestat.st_mode))
            dialog.ts.set(piter, 3, time.ctime(filestat.st_mtime))
    
    # --------------------------------------------------------------------
    
def create_ftree(ts, text = None):
        
    # create the tview using ts
    tv = gtk.TreeView(ts)

    # create a CellRendererText to render the data
    cell = gtk.CellRendererText()
    
    tvcolumn = gtk.TreeViewColumn('File')
    tvcolumn.set_min_width(240)
    tvcolumn.pack_start(cell, True)
    tvcolumn.add_attribute(cell, 'text', 0)
    tvcolumn.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
    tv.append_column(tvcolumn)

    cell2 = gtk.CellRendererText()
    tvcolumn2 = gtk.TreeViewColumn('Size')
    tvcolumn2.set_min_width(100)
    tvcolumn2.pack_start(cell2, True)
    tvcolumn2.add_attribute(cell2, 'text', 1)
    tv.append_column(tvcolumn2)

    cell3 = gtk.CellRendererText()
    tvcolumn3 = gtk.TreeViewColumn('Perm')
    tvcolumn3.set_min_width(120)
    tvcolumn3.pack_start(cell3, True)
    tvcolumn3.add_attribute(cell3, 'text', 2)
    tv.append_column(tvcolumn3)

    cell4 = gtk.CellRendererText()
    tvcolumn4 = gtk.TreeViewColumn('Modified')
    tvcolumn4.set_min_width(150)
    tvcolumn4.pack_start(cell4, True)
    tvcolumn4.add_attribute(cell4, 'text', 3)
    tv.append_column(tvcolumn4)

    return tv

def tree_sel_row(xtree, dialog):
    #print "tree_sel_row", xtree
    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    xstr = xmodel.get_value(xiter, 0)        
    
    #xstr2 = xmodel.get_value(xiter, 1)        
    #xstr3 = xmodel.get_value(xiter, 2)        
    #print xstr, xstr2, xstr3
        
    if os.path.isdir(xstr):
        dialog.entry.set_text("")
    else:
         dialog.entry.set_text(xstr)        
    
def tree_sel(xtree, xiter, xpath, dialog):
    #print "tree_sel", xtree, xiter, xpath
    sel = xtree.get_selection()
    xmodel, xiter = sel.get_selected()
    xstr = xmodel.get_value(xiter, 0)        
    
    #xstr2 = xmodel.get_value(xiter, 1)        
    #xstr3 = xmodel.get_value(xiter, 2)        
    #print xstr, xstr2, xstr3
        
    if xstr[0] == "[":
         xstr = xstr[1:len(xstr)-1]    
    if os.path.isdir(xstr):
        #print "dir", xstr
        os.chdir(xstr)
        populate(dialog)
    else:
        dialog.entry.set_text(xstr)        
        dialog.response(gtk.RESPONSE_ACCEPT)

# Call key handler
def area_key(area, event, self):

    #print "area_key", event
    # Do key down:
    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Escape:
            #print "Esc"
            return
            #area.destroy()

    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.Return:
            #print "Ret"
            return
            #area.destroy()

    if  event.type == gtk.gdk.KEY_PRESS:
        if event.keyval == gtk.keysyms.BackSpace:
            os.chdir("..")
            populate(self)            
            #print "BS"
   
        if event.keyval == gtk.keysyms.Alt_L or \
                event.keyval == gtk.keysyms.Alt_R:
            self.alt = True;
            
        if event.keyval == gtk.keysyms.x or \
                event.keyval == gtk.keysyms.X:
            if self.alt:
                area.destroy()
                                  
    elif  event.type == gtk.gdk.KEY_RELEASE:
        if event.keyval == gtk.keysyms.Alt_L or \
              event.keyval == gtk.keysyms.Alt_R:
            self.alt = False;
            
# ------------------------------------------------------------------------
def mode2str(mode):

    #print mode, oct(mode), hex(mode)
    
    dstr = " "
    if mode & 0x4000:
        dstr = "d" 
    
    estr = ""    
    for aa in range(3):
        xstr = ""
        if mode & 0x4: xstr += "r"
        else:        xstr += "-"
        if mode & 0x2: xstr += "w"    
        else:        xstr += "-"
        if mode & 0x1: xstr += "x"
        else:        xstr += "-"        
        mode = mode >> 3        
        estr = xstr + estr  # Reverse
        
    estr = dstr + estr
    return estr













