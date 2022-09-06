# Plugin for pyedit. The plugin is reistered by puttig it in the
# ~/.pyedpro/plugins directory
# The only mandatory entry point for the module is init()
#
# The plugin receives all kinds of information, see examples and source
#
# Initial version: Fri 16.Jul.2021
#

import os.path

verbose = 0

base = os.path.basename(__file__)

def init():
    if verbose:
        print("Called init function for plugin:", base)
    pass

def keypress(keyx):
    #print("pressed a key in plugin", keyx.string, keyx.keyval, keyx.type)
    pass

def display(disp, cr):
    #print("updated display", disp)
    pass

def syntax(disp, cr):
    #print("draw syntax", disp, cr)
    #disp.draw_text(cr, disp.caret[0] * disp.cxx, disp.caret[1] * disp.cyy, "Disp_Update here")
    #disp.draw_text(cr, disp.caret[0], disp.caret[1], "hello");
    pass

def predraw(disp, cr):
    #print("predraw", disp, cr)
    # Override BG color ... dark  pink
    #cr.set_source_rgba(.255, .455, .555)
    #cr.rectangle( 0, 0, disp.www, disp.hhh)
    #cr.fill()
    #import pedcolor
    #disp.fgcolor  = pedcolor.str2float("#aabbcc")
    #print("setting", disp.fgcolor)
    pass
# EOF


