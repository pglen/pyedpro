#!/usr/bin/env python

# Key Handler for the editor. Extracted to a separate module
# for easy update. The key handler is table driven, so new key
# assignments can be made with ease

#import gtk
from __future__ import absolute_import
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from . import acthand

# Grabbed modifier defines from GTK
#
#  ... Turns out Gtk.gdk 2.6+ defines these (above) constants as ...
#      Gtk.gdk.*_MASK
# Anyway, it was an exercise in grabbin' 'C' into python.

GDK_SHIFT_MASK      = 1 << 0
GDK_LOCK_MASK	    = 1 << 1
GDK_CONTROL_MASK    = 1 << 2
GDK_MOD1_MASK	    = 1 << 3
GDK_MOD2_MASK	    = 1 << 4
GDK_MOD3_MASK	    = 1 << 5
GDK_MOD4_MASK	    = 1 << 6
GDK_MOD5_MASK	    = 1 << 7
GDK_BUTTON1_MASK    = 1 << 8
GDK_BUTTON2_MASK    = 1 << 9
GDK_BUTTON3_MASK    = 1 << 10
GDK_BUTTON4_MASK    = 1 << 11
GDK_BUTTON5_MASK    = 1 << 12

#  /* The next few modifiers are used by XKB, so we skip to the end.
#   * Bits 15 - 25 are currently unused. Bit 29 is used internally.
#   */

GDK_SUPER_MASK    = 1 << 26
GDK_HYPER_MASK    = 1 << 27
GDK_META_MASK     = 1 << 28

GDK_RELEASE_MASK  = 1 << 30
GDK_MODIFIER_MASK = 0x5c001fff

# ------------------------------------------------------------------------
# Handle keys:

class KeyHand:

    ctrl = 0; alt = 0; shift = 0

    def __init__(self):

        self.act = acthand.ActHand()
        self.act.keyhand = self

        # Here one can customize the key / function assignments
        self.reg_keytab = [
            [Gdk.KEY_Up, self.act.up],
            [Gdk.KEY_KP_Up, self.act.up],
            [Gdk.KEY_Down, self.act.down],
            [Gdk.KEY_KP_Down, self.act.down],
            [Gdk.KEY_Left, self.act.left],
            [Gdk.KEY_KP_Left, self.act.left],
            [Gdk.KEY_Right, self.act.right],
            [Gdk.KEY_KP_Right, self.act.right],
            [Gdk.KEY_Page_Up, self.act.pgup],
            [Gdk.KEY_KP_Page_Up, self.act.pgup],
            [Gdk.KEY_Page_Down, self.act.pgdn],
            [Gdk.KEY_KP_Page_Down, self.act.pgdn],
            [Gdk.KEY_Home, self.act.home],
            [Gdk.KEY_KP_Home, self.act.home],
            [Gdk.KEY_End, self.act.end],
            [Gdk.KEY_KP_End, self.act.end],
            [Gdk.KEY_Delete, self.act.delete],
            [Gdk.KEY_KP_Delete, self.act.delete],
            [Gdk.KEY_BackSpace, self.act.bs],
            [Gdk.KEY_Return, self.act.ret],
            [Gdk.KEY_KP_Enter, self.act.ret],
            [Gdk.KEY_Escape, self.act.esc],
            [Gdk.KEY_Insert, self.act.ins],
            [Gdk.KEY_KP_Insert, self.act.ins],

            [Gdk.KEY_Tab, self.act.tab],
            [Gdk.KEY_ISO_Left_Tab, self.act.tab],

            [Gdk.KEY_F1, self.act.f1],
            [Gdk.KEY_F2, self.act.f2],
            [Gdk.KEY_F3, self.act.f3],
            [Gdk.KEY_F4, self.act.f4],
            [Gdk.KEY_F5, self.act.f5],
            [Gdk.KEY_F6, self.act.f6],
            [Gdk.KEY_F7, self.act.f7],
            [Gdk.KEY_F8, self.act.f8],
            [Gdk.KEY_F9, self.act.f9],
            [Gdk.KEY_F10, self.act.f10],
            [Gdk.KEY_F11, self.act.f11],
            #[Gdk.KEY_F12, self.act.f12],
            ]

        # Separate keytab on ctrl for easy customization. May call functions
        # in any other keytabs. (if sensitive to mod key, separate actions result)

        self.ctrl_keytab = [
            [Gdk.KEY_Tab, self.act.ctrl_tab],
            [Gdk.KEY_Up, self.act.up],
            [Gdk.KEY_KP_Up, self.act.up],
            [Gdk.KEY_Down, self.act.down],
            [Gdk.KEY_KP_Down, self.act.down],
            [Gdk.KEY_Left, self.act.left],
            [Gdk.KEY_KP_Left, self.act.left],
            [Gdk.KEY_Right, self.act.right],
            [Gdk.KEY_KP_Right, self.act.right],
            [Gdk.KEY_Page_Up, self.act.pgup],
            [Gdk.KEY_KP_Page_Up, self.act.pgup],
            [Gdk.KEY_Page_Down, self.act.pgdn],
            [Gdk.KEY_KP_Page_Down, self.act.pgdn],
            [Gdk.KEY_Home, self.act.home],
            [Gdk.KEY_KP_Home, self.act.home],
            [Gdk.KEY_End, self.act.end],
            [Gdk.KEY_KP_End, self.act.end],
            [Gdk.KEY_Delete, self.act.delete],
            [Gdk.KEY_KP_Delete, self.act.delete],
            [Gdk.KEY_BackSpace, self.act.bs],
            [Gdk.KEY_F6, self.act.f6],
            [Gdk.KEY_F10, self.act.f10],
            [Gdk.KEY_a, self.act.ctrl_a],
            [Gdk.KEY_A, self.act.ctrl_a],
            [Gdk.KEY_b, self.act.ctrl_b],
            [Gdk.KEY_B, self.act.ctrl_b],
            [Gdk.KEY_c, self.act.ctrl_c],
            [Gdk.KEY_D, self.act.ctrl_d],
            [Gdk.KEY_d, self.act.ctrl_d],
            [Gdk.KEY_C, self.act.ctrl_c],
            [Gdk.KEY_e, self.act.ctrl_e],
            [Gdk.KEY_E, self.act.ctrl_e],
            [Gdk.KEY_f, self.act.ctrl_f],
            [Gdk.KEY_F, self.act.ctrl_f],
            [Gdk.KEY_h, self.act.ctrl_h],
            [Gdk.KEY_H, self.act.ctrl_h],
            [Gdk.KEY_i, self.act.ctrl_i],
            [Gdk.KEY_I, self.act.ctrl_i],
            [Gdk.KEY_j, self.act.ctrl_j],
            [Gdk.KEY_J, self.act.ctrl_j],
            [Gdk.KEY_k, self.act.ctrl_k],
            [Gdk.KEY_K, self.act.ctrl_k],
            [Gdk.KEY_l, self.act.ctrl_l],
            [Gdk.KEY_L, self.act.ctrl_l],
            [Gdk.KEY_m, self.act.ctrl_m],
            [Gdk.KEY_M, self.act.ctrl_m],
            [Gdk.KEY_g, self.act.ctrl_g],
            [Gdk.KEY_G, self.act.ctrl_g],
            [Gdk.KEY_r, self.act.ctrl_r],
            [Gdk.KEY_R, self.act.ctrl_r],
            [Gdk.KEY_t, self.act.ctrl_t],
            [Gdk.KEY_T, self.act.ctrl_t],
            [Gdk.KEY_u, self.act.ctrl_u],
            [Gdk.KEY_U, self.act.ctrl_u],
            [Gdk.KEY_v, self.act.ctrl_v],
            [Gdk.KEY_V, self.act.ctrl_v],
            [Gdk.KEY_x, self.act.ctrl_x],
            [Gdk.KEY_X, self.act.ctrl_x],
            [Gdk.KEY_y, self.act.ctrl_y],
            [Gdk.KEY_Y, self.act.ctrl_y],
            [Gdk.KEY_z, self.act.ctrl_z],
            [Gdk.KEY_Z, self.act.ctrl_z],
            [Gdk.KEY_1, self.act.ctrl_1],
            [Gdk.KEY_2, self.act.ctrl_2],
            [Gdk.KEY_3, self.act.ctrl_3],
            [Gdk.KEY_4, self.act.ctrl_4],
            [Gdk.KEY_5, self.act.ctrl_5],
            [Gdk.KEY_6, self.act.ctrl_6],
            [Gdk.KEY_7, self.act.ctrl_7],
            [Gdk.KEY_8, self.act.ctrl_8],
            [Gdk.KEY_9, self.act.ctrl_9],
            [Gdk.KEY_0, self.act.ctrl_0],
            [Gdk.KEY_space, self.act.ctrl_space],
            ]

        # Separate keytab on ctrl - alt for easy customization.
        # Do upper and lower for catching shift in the routine

        self.ctrl_alt_keytab = [

            [Gdk.KEY_a, self.act.ctrl_alt_a],
            [Gdk.KEY_A, self.act.ctrl_alt_a],

            [Gdk.KEY_b, self.act.ctrl_alt_b],
            [Gdk.KEY_B, self.act.ctrl_alt_b],

            [Gdk.KEY_c, self.act.ctrl_alt_c],
            [Gdk.KEY_C, self.act.ctrl_alt_c],
            [Gdk.KEY_h, self.act.ctrl_alt_h],
            [Gdk.KEY_H, self.act.ctrl_alt_h],
            [Gdk.KEY_j, self.act.ctrl_alt_j],
            [Gdk.KEY_J, self.act.ctrl_alt_j],
            [Gdk.KEY_k, self.act.ctrl_alt_k],
            [Gdk.KEY_K, self.act.ctrl_alt_k],

            [Gdk.KEY_r, self.act.ctrl_alt_r],
            [Gdk.KEY_R, self.act.ctrl_alt_r],
        ]

        # Separate keytab on alt for easy customization.

        self.alt_keytab = [
            [Gdk.KEY_Up, self.act.up],
            [Gdk.KEY_KP_Up, self.act.up],
            [Gdk.KEY_Down, self.act.down],
            [Gdk.KEY_KP_Down, self.act.down],
            [Gdk.KEY_Left, self.act.left],
            [Gdk.KEY_KP_Left, self.act.left],
            [Gdk.KEY_Right, self.act.right],
            [Gdk.KEY_KP_Right, self.act.right],
            [Gdk.KEY_Page_Up, self.act.pgup],
            [Gdk.KEY_KP_Page_Up, self.act.pgup],
            [Gdk.KEY_Page_Down, self.act.pgdn],
            [Gdk.KEY_KP_Page_Down, self.act.pgdn],
            [Gdk.KEY_Home, self.act.home],
            [Gdk.KEY_KP_Home, self.act.home],
            [Gdk.KEY_End, self.act.end],
            [Gdk.KEY_KP_End, self.act.end],
            [Gdk.KEY_Delete, self.act.delete],
            [Gdk.KEY_KP_Delete, self.act.delete],
            [Gdk.KEY_BackSpace, self.act.bs],
            [Gdk.KEY_a, self.act.alt_a],
            [Gdk.KEY_A, self.act.alt_a],
            [Gdk.KEY_b, self.act.alt_b],
            [Gdk.KEY_B, self.act.alt_b],
            [Gdk.KEY_c, self.act.alt_c],
            [Gdk.KEY_C, self.act.alt_c],
            [Gdk.KEY_d, self.act.alt_d],
            [Gdk.KEY_D, self.act.alt_d],
            [Gdk.KEY_f, self.act.alt_f],
            [Gdk.KEY_F, self.act.alt_f],
            [Gdk.KEY_g, self.act.alt_g],
            [Gdk.KEY_G, self.act.alt_g],
            [Gdk.KEY_i, self.act.alt_i],
            [Gdk.KEY_I, self.act.alt_i],
            [Gdk.KEY_j, self.act.alt_j],
            [Gdk.KEY_J, self.act.alt_j],
            [Gdk.KEY_k, self.act.alt_k],
            [Gdk.KEY_K, self.act.alt_k],
            [Gdk.KEY_l, self.act.alt_l],
            [Gdk.KEY_L, self.act.alt_l],
            [Gdk.KEY_o, self.act.alt_o],
            [Gdk.KEY_O, self.act.alt_o],
            [Gdk.KEY_q, self.act.alt_q],
            [Gdk.KEY_Q, self.act.alt_q],
            [Gdk.KEY_y, self.act.alt_y],
            [Gdk.KEY_Y, self.act.alt_y],
            [Gdk.KEY_p, self.act.f5],
            [Gdk.KEY_P, self.act.f5],
            [Gdk.KEY_n, self.act.f6],
            [Gdk.KEY_N, self.act.f6],
            [Gdk.KEY_r, self.act.ctrl_y],
            [Gdk.KEY_R, self.act.ctrl_y],
            [Gdk.KEY_s, self.act.alt_s],
            [Gdk.KEY_S, self.act.alt_s],
            [Gdk.KEY_t, self.act.alt_t],
            [Gdk.KEY_T, self.act.alt_t],
            [Gdk.KEY_u, self.act.ctrl_z],
            [Gdk.KEY_U, self.act.ctrl_z],
            [Gdk.KEY_v, self.act.alt_v],
            [Gdk.KEY_V, self.act.alt_v],
            [Gdk.KEY_w, self.act.alt_w],
            [Gdk.KEY_W, self.act.alt_w],
            [Gdk.KEY_z, self.act.alt_z],
            [Gdk.KEY_Z, self.act.alt_z],
            #[Gdk.KEY_bracketleft, self.act.ctrl_u],
            #[Gdk.KEY_bracketright, self.act.ctrl_alt_l],
            ]

    # When we get focus, we start out with no modifier keys
    def reset(self):
        self.ctrl = 0; self.alt = 0; self.shift = 0

    # Main entry point for handling keys:
    def handle_key(self, self2, area, event):

        #print "key event",  int(event.type), int(event.state),
        #print event.keyval, hex(event.keyval)
        #print event.state, event.string

        self.state2 = int(event.state)
        self.handle_key2(self2, area, event)

    # Internal entry point for handling keys:
    def handle_key2(self, self2, area, event):
        if self2.record:
            if event.keyval == Gdk.KEY_F7 or \
                    event.keyval == Gdk.KEY_F8:
                #print "avoiding record/play recursion", event
                pass
            else:
                #print "rec", event, event.type, int(event.type)
                var = (int(event.type), int(event.keyval), int(event.state),\
                       event.window, event.string, self.shift, self.ctrl, self.alt)
                self2.recarr.append(var)

        ret = self.handle_modifiers(self2, area, event)
        # Propagate to document (just for easy access)
        self2.ctrl = self.ctrl
        self2.alt = self.alt
        self2.shift = self.shift
        if ret: return

        if  event.type == Gdk.EventType.KEY_PRESS:
            if self2.nokey:
                if  (self.ctrl == True) and \
                    (event.keyval == Gdk.KEY_space):
                    self2.mained.update_statusbar("Keyboard enabled.")
                    self2.nokey = False
                else:
                    self2.mained.update_statusbar(\
                        "Keyboard disabled. Press Ctrl-Space to enable.")
                    if event.keyval == Gdk.KEY_Escape:
                        self2.mained.update_statusbar("ESC")
                return

        #print "executing key ", \
        #    event, event.type, event.keyval, event.window

        # Call the appropriate handlers. Note the priority.
        if self.ctrl and self.alt:
            self.handle_ctrl_alt_key(self2, area, event)
        elif self.alt:
            self.handle_alt_key(self2, area, event)
        elif self.ctrl:
            self.handle_ctrl_key(self2, area, event)
        else:
            self.handle_reg_key(self2, area, event)

    # --------------------------------------------------------------------
    # Note that it does not handle stacked control keys - just on / off

    def handle_modifiers(self, self2, area, event):

        ret = False

        # This turned out to be a bust ... let the OS feed me the right state
        # However, we still interpret them so the key is discarded
        # The key state was inconsistent, as the key is not fed when there is
        # no focus. For example alt-tab - the focus goes away on tab -
        # alt release is never fed to us. See Below.
        # Also, if you want to interpret Left-Alt or Right-Alt,
        # (or L/R shift/control), here is the place to do it.

        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                #print "Alt down"
                #self2.flash(True)
                #self.alt = True;
                ret = True
            elif event.keyval == Gdk.KEY_Control_L or \
                    event.keyval == Gdk.KEY_Control_R:
                #print "Ctrl down"
                #self.ctrl = True;
                ret = True
            if event.keyval == Gdk.KEY_Shift_L or \
                  event.keyval == Gdk.KEY_Shift_R:
                #print "shift down"
                #self.shift = True;
                ret = True

        # Do key up
        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                #print "Alt up"
                #self2.flash(False)
                #self.alt = False;
                ret = True
            if event.keyval == Gdk.KEY_Control_L or \
                  event.keyval == Gdk.KEY_Control_R:
                #print "Ctrl up"
                #self.ctrl = False;
                ret = True
            if event.keyval == Gdk.KEY_Shift_L or \
                  event.keyval == Gdk.KEY_Shift_R:
                #print "shift up"
                #self.shift = False;
                ret = True

        #if event.state & GDK_SHIFT_MASK:
        #if event.state & Gdk.EventType.SHIFT_MASK:
        if self.state2 & Gdk.ModifierType.SHIFT_MASK:
            self.shift = True
        else:
            self.shift = False

        #if event.state & GDK_MOD1_MASK:
        if self.state2  & Gdk.ModifierType.MOD1_MASK:
            self.alt = True
        else:
            self.alt = False

        #if event.state & GDK_CONTROL_MASK:
        if self.state2  & Gdk.ModifierType.CONTROL_MASK:
            self.ctrl = True
        else:
            self.ctrl = False

        return ret

    # --------------------------------------------------------------------
    # Control Alt keytab

    def handle_ctrl_alt_key(self, self2, area, event):
        self._handle_key(self2, area, event, self.ctrl_alt_keytab)

    # --------------------------------------------------------------------
    # Control keytab

    def handle_ctrl_key(self, self2, area, event):
        self._handle_key(self2, area, event, self.ctrl_keytab)

    # --------------------------------------------------------------------
    # Regular keytab

    def handle_reg_key(self, self2, area, event):
        # Handle multi key press counts by resetting if not that key
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval != Gdk.KEY_Home:
                self.act.was_home = 0
            if event.keyval != Gdk.KEY_End:
                self.act.was_end = 0

        self._handle_key(self2, area, event, self.reg_keytab)

    # --------------------------------------------------------------------
    # Alt key

    def handle_alt_key(self, self2, area, event):
        if  event.type == Gdk.EventType.KEY_PRESS:
            #print "alt hand", event
            if event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_9:
                print ("Keyhand Alt num", event.keyval - Gdk.KEY_1)
                num = event.keyval - Gdk.KEY_1
                if num >  self2.notebook.get_n_pages() - 1:
                    self2.mained.update_statusbar("Invalid tab (page) index.")
                else:
                    old = self2.notebook.get_current_page()
                    if old == num:
                        self2.mained.update_statusbar("Already at page %d ..." % old)
                    else:
                        self2.notebook.set_current_page(num)

            elif event.keyval == Gdk.KEY_0:
                self2.appwin.mywin.set_focus(self2.appwin.treeview)
            else:
                self._handle_key(self2, area, event, self.alt_keytab)

    # Internal key handler. Keytab preselected by caller
    def _handle_key(self, self2, area, event, xtab):
        #print event
        ret = False
        if  event.type == Gdk.EventType.KEY_PRESS:
            gotkey = False
            for kk, func in xtab:
                if event.keyval == kk:
                    gotkey = True
                    func(self2)
                    break
            # No key assignment found, assume char
            if not gotkey:
               if event.keyval == Gdk.KEY_F12:
                    if self.shift:
                        self2.showtab(True)
                    elif self.ctrl:
                        self2.hexview(True)
                    elif self.alt:
                        self2.showcol(True)
                    else:
                        self2.flash(True)
               else:
                    self.act.add_key(self2, event)

        if  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_F12:
                    if self.shift:
                        self2.showtab(False)
                    if self.ctrl:
                        self2.hexview(False)
                    elif self.alt:
                        self2.showcol(False)
                    else:
                        self2.flash(False)

        return ret





















































































