#!/usr/bin/env python

# Key Handler for the editor. Extracted to a separate module
# for easy update. The key handler is table driven, so new key
# assignments can be made with ease

#from __future__ import absolute_import

import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

#sys.path.append('..')

from pedlib import pedconfig
from pedlib import pedlog
from pedlib import pedsql
from pedlib import pedspell
from pedlib import pedcolor
from pedlib import pedfont
from pedlib import pedundo
from pedlib import pedplug

# Grabbed modifier defines from GTK
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

    #ctrl = 0; alt = 0; shift = 0; super = 0;

    def __init__(self, acth):

        #self.acth = pedconfig.conf.acth
        self.acth = acth
        self.reset()

        # Here one can customize the key / function assignments
        self.reg_keytab = [
            [Gdk.KEY_Up, self.acth.up],
            [Gdk.KEY_KP_Up, self.acth.up],
            [Gdk.KEY_Down, self.acth.down],
            [Gdk.KEY_KP_Down, self.acth.down],
            [Gdk.KEY_Left, self.acth.left],
            [Gdk.KEY_KP_Left, self.acth.left],
            [Gdk.KEY_Right, self.acth.right],
            [Gdk.KEY_KP_Right, self.acth.right],
            [Gdk.KEY_Page_Up, self.acth.pgup],
            [Gdk.KEY_KP_Page_Up, self.acth.pgup],
            [Gdk.KEY_Page_Down, self.acth.pgdn],
            [Gdk.KEY_KP_Page_Down, self.acth.pgdn],
            [Gdk.KEY_Home, self.acth.home],
            [Gdk.KEY_KP_Home, self.acth.home],
            [Gdk.KEY_End, self.acth.end],
            [Gdk.KEY_KP_End, self.acth.end],
            [Gdk.KEY_Delete, self.acth.delete],
            [Gdk.KEY_KP_Delete, self.acth.delete],
            [Gdk.KEY_BackSpace, self.acth.bs],
            [Gdk.KEY_Return, self.acth.ret],
            [Gdk.KEY_KP_Enter, self.acth.ret],
            [Gdk.KEY_Escape, self.acth.esc],
            [Gdk.KEY_Insert, self.acth.ins],
            [Gdk.KEY_KP_Insert, self.acth.ins],

            [Gdk.KEY_Tab, self.acth.tab],
            [Gdk.KEY_ISO_Left_Tab, self.acth.tab],

            [Gdk.KEY_F1, self.acth.f1],
            [Gdk.KEY_F2, self.acth.f2],
            [Gdk.KEY_F3, self.acth.f3],
            [Gdk.KEY_F4, self.acth.f4],
            [Gdk.KEY_F5, self.acth.f5],
            [Gdk.KEY_F6, self.acth.f6],
            [Gdk.KEY_F7, self.acth.f7],
            [Gdk.KEY_F8, self.acth.f8],
            [Gdk.KEY_F9, self.acth.f9],
            [Gdk.KEY_F10, self.acth.f10],
            [Gdk.KEY_F11, self.acth.f11],
            #[Gdk.KEY_F12, self.acth.f12],
            ]

        # Separate keytab on ctrl for easy customization. May call functions
        # in any other keytabs. (if sensitive to mod key, separate actions result)

        self.ctrl_keytab = [
            [Gdk.KEY_Tab, self.acth.ctrl_tab],
            [Gdk.KEY_Up, self.acth.up],
            [Gdk.KEY_KP_Up, self.acth.up],
            [Gdk.KEY_Down, self.acth.down],
            [Gdk.KEY_KP_Down, self.acth.down],
            [Gdk.KEY_Left, self.acth.left],
            [Gdk.KEY_KP_Left, self.acth.left],
            [Gdk.KEY_Right, self.acth.right],
            [Gdk.KEY_KP_Right, self.acth.right],
            [Gdk.KEY_Page_Up, self.acth.pgup],
            [Gdk.KEY_KP_Page_Up, self.acth.pgup],
            [Gdk.KEY_Page_Down, self.acth.pgdn],
            [Gdk.KEY_KP_Page_Down, self.acth.pgdn],
            [Gdk.KEY_Home, self.acth.home],
            [Gdk.KEY_KP_Home, self.acth.home],
            [Gdk.KEY_End, self.acth.end],
            [Gdk.KEY_KP_End, self.acth.end],
            [Gdk.KEY_Delete, self.acth.delete],
            [Gdk.KEY_KP_Delete, self.acth.delete],
            [Gdk.KEY_BackSpace, self.acth.bs],
            [Gdk.KEY_F6, self.acth.f6],
            [Gdk.KEY_F10, self.acth.f10],
            [Gdk.KEY_a, self.acth.ctrl_a],
            [Gdk.KEY_A, self.acth.ctrl_a],
            [Gdk.KEY_b, self.acth.ctrl_b],
            [Gdk.KEY_B, self.acth.ctrl_b],
            [Gdk.KEY_c, self.acth.ctrl_c],
            [Gdk.KEY_D, self.acth.ctrl_d],
            [Gdk.KEY_d, self.acth.ctrl_d],
            [Gdk.KEY_C, self.acth.ctrl_c],
            [Gdk.KEY_e, self.acth.ctrl_e],
            [Gdk.KEY_E, self.acth.ctrl_e],
            [Gdk.KEY_f, self.acth.ctrl_f],
            [Gdk.KEY_F, self.acth.ctrl_f],
            [Gdk.KEY_h, self.acth.ctrl_h],
            [Gdk.KEY_H, self.acth.ctrl_h],
            [Gdk.KEY_i, self.acth.ctrl_i],
            [Gdk.KEY_I, self.acth.ctrl_i],
            [Gdk.KEY_j, self.acth.ctrl_j],
            [Gdk.KEY_J, self.acth.ctrl_j],
            [Gdk.KEY_g, self.acth.ctrl_g],
            [Gdk.KEY_G, self.acth.ctrl_g],
            [Gdk.KEY_k, self.acth.ctrl_k],
            [Gdk.KEY_K, self.acth.ctrl_k],
            [Gdk.KEY_l, self.acth.ctrl_l],
            [Gdk.KEY_L, self.acth.ctrl_l],
            [Gdk.KEY_m, self.acth.ctrl_m],
            [Gdk.KEY_M, self.acth.ctrl_m],
            [Gdk.KEY_N, self.acth.ctrl_n],
            [Gdk.KEY_n, self.acth.ctrl_n],
            [Gdk.KEY_o, self.acth.ctrl_o],
            [Gdk.KEY_O, self.acth.ctrl_o],
            [Gdk.KEY_p, self.acth.ctrl_p],
            [Gdk.KEY_P, self.acth.ctrl_p],
            [Gdk.KEY_q, self.acth.ctrl_q],
            [Gdk.KEY_Q, self.acth.ctrl_q],
            [Gdk.KEY_r, self.acth.ctrl_r],
            [Gdk.KEY_R, self.acth.ctrl_r],
            [Gdk.KEY_t, self.acth.ctrl_t],
            [Gdk.KEY_T, self.acth.ctrl_t],
            [Gdk.KEY_u, self.acth.ctrl_u],
            [Gdk.KEY_U, self.acth.ctrl_u],
            [Gdk.KEY_v, self.acth.ctrl_v],
            [Gdk.KEY_V, self.acth.ctrl_v],
            [Gdk.KEY_w, self.acth.ctrl_w],
            [Gdk.KEY_W, self.acth.ctrl_w],
            [Gdk.KEY_x, self.acth.ctrl_x],
            [Gdk.KEY_X, self.acth.ctrl_x],
            [Gdk.KEY_y, self.acth.ctrl_y],
            [Gdk.KEY_Y, self.acth.ctrl_y],
            [Gdk.KEY_z, self.acth.ctrl_z],
            [Gdk.KEY_Z, self.acth.ctrl_z],
            [Gdk.KEY_1, self.acth.ctrl_num],
            [Gdk.KEY_2, self.acth.ctrl_num],
            [Gdk.KEY_3, self.acth.ctrl_num],
            [Gdk.KEY_4, self.acth.ctrl_num],
            [Gdk.KEY_5, self.acth.ctrl_num],
            [Gdk.KEY_6, self.acth.ctrl_num],
            [Gdk.KEY_7, self.acth.ctrl_num],
            [Gdk.KEY_8, self.acth.ctrl_num],
            [Gdk.KEY_9, self.acth.ctrl_num],
            [Gdk.KEY_0, self.acth.ctrl_num],
            [Gdk.KEY_space, self.acth.ctrl_space],
            ]

        # Separate keytab on right ctrl

        self.rctrl_keytab = [
            [Gdk.KEY_Tab, self.acth.ctrl_tab],
            [Gdk.KEY_Up, self.acth.up],
            [Gdk.KEY_KP_Up, self.acth.up],
            [Gdk.KEY_Down, self.acth.down],
            [Gdk.KEY_KP_Down, self.acth.down],
            [Gdk.KEY_Left, self.acth.left],
            [Gdk.KEY_KP_Left, self.acth.left],
            [Gdk.KEY_Right, self.acth.right],
            [Gdk.KEY_KP_Right, self.acth.right],
            [Gdk.KEY_Page_Up, self.acth.pgup],
            [Gdk.KEY_KP_Page_Up, self.acth.pgup],
            [Gdk.KEY_Page_Down, self.acth.pgdn],
            [Gdk.KEY_KP_Page_Down, self.acth.pgdn],
            [Gdk.KEY_Home, self.acth.home],
            [Gdk.KEY_KP_Home, self.acth.home],
            [Gdk.KEY_End, self.acth.end],
            [Gdk.KEY_KP_End, self.acth.end],
            [Gdk.KEY_Delete, self.acth.delete],
            [Gdk.KEY_KP_Delete, self.acth.delete],
            [Gdk.KEY_BackSpace, self.acth.bs],
            [Gdk.KEY_F6, self.acth.f6],
            [Gdk.KEY_F10, self.acth.f10],
            [Gdk.KEY_a, self.acth.rctrl_a],
            [Gdk.KEY_A, self.acth.rctrl_a],
            [Gdk.KEY_b, self.acth.rctrl_all],
            [Gdk.KEY_B, self.acth.rctrl_all],
            [Gdk.KEY_c, self.acth.rctrl_c],
            [Gdk.KEY_D, self.acth.rctrl_c],
            [Gdk.KEY_d, self.acth.rctrl_all],
            [Gdk.KEY_C, self.acth.rctrl_all],
            [Gdk.KEY_e, self.acth.rctrl_all],
            [Gdk.KEY_E, self.acth.rctrl_all],
            [Gdk.KEY_f, self.acth.rctrl_f],
            [Gdk.KEY_F, self.acth.rctrl_f],
            [Gdk.KEY_g, self.acth.rctrl_all],
            [Gdk.KEY_G, self.acth.rctrl_all],
            [Gdk.KEY_h, self.acth.rctrl_h],
            [Gdk.KEY_H, self.acth.rctrl_h],
            [Gdk.KEY_i, self.acth.rctrl_i],
            [Gdk.KEY_I, self.acth.rctrl_i],
            [Gdk.KEY_j, self.acth.rctrl_all],
            [Gdk.KEY_J, self.acth.rctrl_all],
            [Gdk.KEY_k, self.acth.rctrl_all],
            [Gdk.KEY_K, self.acth.rctrl_all],
            [Gdk.KEY_l, self.acth.rctrl_l],
            [Gdk.KEY_L, self.acth.rctrl_l],
            [Gdk.KEY_m, self.acth.rctrl_all],
            [Gdk.KEY_M, self.acth.rctrl_all],
            [Gdk.KEY_N, self.acth.rctrl_all],
            [Gdk.KEY_n, self.acth.rctrl_all],
            [Gdk.KEY_o, self.acth.rctrl_all],
            [Gdk.KEY_O, self.acth.rctrl_all],
            [Gdk.KEY_p, self.acth.rctrl_all],
            [Gdk.KEY_P, self.acth.rctrl_all],
            [Gdk.KEY_q, self.acth.rctrl_all],
            [Gdk.KEY_Q, self.acth.rctrl_all],
            [Gdk.KEY_r, self.acth.rctrl_r],
            [Gdk.KEY_R, self.acth.rctrl_r],
            [Gdk.KEY_t, self.acth.rctrl_t],
            [Gdk.KEY_T, self.acth.rctrl_t],
            [Gdk.KEY_u, self.acth.rctrl_all],
            [Gdk.KEY_U, self.acth.rctrl_all],
            [Gdk.KEY_v, self.acth.rctrl_all],
            [Gdk.KEY_V, self.acth.rctrl_all],
            [Gdk.KEY_w, self.acth.rctrl_w],
            [Gdk.KEY_W, self.acth.rctrl_w],
            [Gdk.KEY_x, self.acth.rctrl_all],
            [Gdk.KEY_X, self.acth.rctrl_all],
            [Gdk.KEY_y, self.acth.rctrl_all],
            [Gdk.KEY_Y, self.acth.rctrl_all],
            [Gdk.KEY_z, self.acth.rctrl_all],
            [Gdk.KEY_Z, self.acth.rctrl_all],
            [Gdk.KEY_1, self.acth.rctrl_num],
            [Gdk.KEY_2, self.acth.rctrl_num],
            [Gdk.KEY_3, self.acth.rctrl_num],
            [Gdk.KEY_4, self.acth.rctrl_num],
            [Gdk.KEY_5, self.acth.rctrl_num],
            [Gdk.KEY_6, self.acth.rctrl_num],
            [Gdk.KEY_7, self.acth.rctrl_num],
            [Gdk.KEY_8, self.acth.rctrl_num],
            [Gdk.KEY_9, self.acth.rctrl_num],
            [Gdk.KEY_0, self.acth.rctrl_num],
            [Gdk.KEY_space, self.acth.ctrl_space],
            ]

        # Separate keytab on right alt

        self.right_alt_keytab = [

            [Gdk.KEY_Up, self.acth.top],
            [Gdk.KEY_KP_Up, self.acth.top],
            [Gdk.KEY_Down, self.acth.bottom],
            [Gdk.KEY_KP_Down, self.acth.bottom],

            [Gdk.KEY_Left, self.acth.home],
            [Gdk.KEY_KP_Left, self.acth.home],
            [Gdk.KEY_Right, self.acth.end],
            [Gdk.KEY_KP_Right, self.acth.end],
            ]

        # On my system, the following come to super:
        #       abcgghijklmnoqstuvwxyz

        self.super_keytab = [
            [Gdk.KEY_a, self.acth.super_a],
            [Gdk.KEY_A, self.acth.super_a],
            [Gdk.KEY_b, self.acth.super_b],
            [Gdk.KEY_B, self.acth.super_b],
            ]

        self.super_alt_keytab = [
            [Gdk.KEY_a, self.acth.super_a],
            [Gdk.KEY_A, self.acth.super_a],
            [Gdk.KEY_b, self.acth.super_b],
            [Gdk.KEY_B, self.acth.super_b],
            ]

        self.super_ctrl_alt_keytab = [
            [Gdk.KEY_a, self.acth.super_a],
            [Gdk.KEY_A, self.acth.super_a],
            [Gdk.KEY_b, self.acth.super_b],
            [Gdk.KEY_B, self.acth.super_b],
            ]

        # Separate keytab on ctrl - alt for easy customization.
        # Do upper and lower for catching shift in the routine

        self.ctrl_alt_keytab = [

            [Gdk.KEY_a, self.acth.ctrl_alt_a],
            [Gdk.KEY_A, self.acth.ctrl_alt_a],
            [Gdk.KEY_b, self.acth.ctrl_alt_b],
            [Gdk.KEY_B, self.acth.ctrl_alt_b],
            [Gdk.KEY_c, self.acth.ctrl_alt_c],
            [Gdk.KEY_C, self.acth.ctrl_alt_c],
            [Gdk.KEY_d, self.acth.ctrl_alt_d],
            [Gdk.KEY_D, self.acth.ctrl_alt_d],
            [Gdk.KEY_e, self.acth.ctrl_alt_e],
            [Gdk.KEY_E, self.acth.ctrl_alt_e],
            [Gdk.KEY_f, self.acth.ctrl_alt_f],
            [Gdk.KEY_F, self.acth.ctrl_alt_f],
            [Gdk.KEY_g, self.acth.ctrl_alt_g],
            [Gdk.KEY_G, self.acth.ctrl_alt_g],
            [Gdk.KEY_h, self.acth.ctrl_alt_h],
            [Gdk.KEY_H, self.acth.ctrl_alt_h],
            [Gdk.KEY_j, self.acth.ctrl_alt_j],
            [Gdk.KEY_J, self.acth.ctrl_alt_j],
            [Gdk.KEY_k, self.acth.ctrl_alt_k],
            [Gdk.KEY_K, self.acth.ctrl_alt_k],
            [Gdk.KEY_t, self.acth.ctrl_alt_t],
            [Gdk.KEY_T, self.acth.ctrl_alt_t],

            [Gdk.KEY_r, self.acth.ctrl_alt_r],
            [Gdk.KEY_R, self.acth.ctrl_alt_r],
            [Gdk.KEY_v, self.acth.ctrl_alt_v],
            [Gdk.KEY_V, self.acth.ctrl_alt_v],

            [Gdk.KEY_1, self.acth.ctrl_alt_num],
            [Gdk.KEY_2, self.acth.ctrl_alt_num],
            [Gdk.KEY_3, self.acth.ctrl_alt_num],
            [Gdk.KEY_4, self.acth.ctrl_alt_num],
            [Gdk.KEY_5, self.acth.ctrl_alt_num],
            [Gdk.KEY_6, self.acth.ctrl_alt_num],
            [Gdk.KEY_7, self.acth.ctrl_alt_num],
            [Gdk.KEY_8, self.acth.ctrl_alt_num],
            [Gdk.KEY_9, self.acth.ctrl_alt_num],
            [Gdk.KEY_0, self.acth.ctrl_alt_num],
        ]

        # Separate keytab on alt for easy customization.

        self.alt_keytab = [
            [Gdk.KEY_Up, self.acth.up],
            [Gdk.KEY_KP_Up, self.acth.up],
            [Gdk.KEY_Down, self.acth.down],
            [Gdk.KEY_KP_Down, self.acth.down],
            [Gdk.KEY_Left, self.acth.left],
            [Gdk.KEY_KP_Left, self.acth.left],
            [Gdk.KEY_Right, self.acth.right],
            [Gdk.KEY_KP_Right, self.acth.right],
            [Gdk.KEY_Page_Up, self.acth.pgup],
            [Gdk.KEY_KP_Page_Up, self.acth.pgup],
            [Gdk.KEY_Page_Down, self.acth.pgdn],
            [Gdk.KEY_KP_Page_Down, self.acth.pgdn],
            [Gdk.KEY_Home, self.acth.home],
            [Gdk.KEY_KP_Home, self.acth.home],
            [Gdk.KEY_End, self.acth.end],
            [Gdk.KEY_KP_End, self.acth.end],
            [Gdk.KEY_Delete, self.acth.delete],
            [Gdk.KEY_KP_Delete, self.acth.delete],
            [Gdk.KEY_BackSpace, self.acth.bs],
            [Gdk.KEY_a, self.acth.alt_a],
            [Gdk.KEY_A, self.acth.alt_a],
            [Gdk.KEY_b, self.acth.alt_b],
            [Gdk.KEY_B, self.acth.alt_b],
            [Gdk.KEY_c, self.acth.alt_c],
            [Gdk.KEY_C, self.acth.alt_c],
            [Gdk.KEY_d, self.acth.alt_d],
            [Gdk.KEY_D, self.acth.alt_d],
            [Gdk.KEY_f, self.acth.alt_f],
            [Gdk.KEY_F, self.acth.alt_f],
            [Gdk.KEY_g, self.acth.alt_g],
            [Gdk.KEY_G, self.acth.alt_g],
            [Gdk.KEY_i, self.acth.alt_i],
            [Gdk.KEY_I, self.acth.alt_i],
            [Gdk.KEY_j, self.acth.alt_j],
            [Gdk.KEY_J, self.acth.alt_j],
            [Gdk.KEY_k, self.acth.alt_k],
            [Gdk.KEY_K, self.acth.alt_k],
            [Gdk.KEY_l, self.acth.alt_l],
            [Gdk.KEY_L, self.acth.alt_l],
            [Gdk.KEY_o, self.acth.alt_o],
            [Gdk.KEY_O, self.acth.alt_o],
            [Gdk.KEY_q, self.acth.alt_q],
            [Gdk.KEY_Q, self.acth.alt_q],
            [Gdk.KEY_y, self.acth.alt_y],
            [Gdk.KEY_Y, self.acth.alt_y],
            [Gdk.KEY_p, self.acth.f5],
            [Gdk.KEY_P, self.acth.f5],
            [Gdk.KEY_n, self.acth.f6],
            [Gdk.KEY_N, self.acth.f6],
            [Gdk.KEY_r, self.acth.ctrl_y],
            [Gdk.KEY_R, self.acth.ctrl_y],
            [Gdk.KEY_s, self.acth.alt_s],
            [Gdk.KEY_S, self.acth.alt_s],
            [Gdk.KEY_t, self.acth.alt_t],
            [Gdk.KEY_T, self.acth.alt_t],
            [Gdk.KEY_u, self.acth.ctrl_z],
            [Gdk.KEY_U, self.acth.ctrl_z],
            [Gdk.KEY_v, self.acth.alt_v],
            [Gdk.KEY_V, self.acth.alt_v],
            [Gdk.KEY_w, self.acth.alt_w],
            [Gdk.KEY_W, self.acth.alt_w],
            [Gdk.KEY_x, self.acth.alt_x],
            [Gdk.KEY_X, self.acth.alt_x],
            [Gdk.KEY_z, self.acth.alt_z],
            [Gdk.KEY_Z, self.acth.alt_z],
            #[Gdk.KEY_bracketleft, self.acth.ctrl_u],
            #[Gdk.KEY_bracketright, self.acth.ctrl_alt_l],
            ]

    # When we get focus, we start out with no modifier keys
    def reset(self):
        self.ctrl = False;      self.alt = False; self.shift = False
        self.super = False;     self.rsuper = False;
        self.ralt = False;      self.lalt = False;
        self.rctrl = False;      self.lctrl = False;
        self.rshift = False;    self.lshift = False;

    # --------------------------------------------------------------------
    # This is the main entry point for handling keys:

    def handle_key(self, self2, area, event):

        #print ("KEY:",   event.keyval  )

        # Ramp up debug level
        if pedconfig.conf.pgdebug > 6:
             print( "key val ",  event.keyval, "key name", event.string)
        if pedconfig.conf.pgdebug > 7:
            print( "key event",  event.type)
        if pedconfig.conf.pgdebug > 8:
            print( "key state",  event.state)

        if pedconfig.conf.show_keys:
            print ("KEY:", event.keyval, hex(event.keyval), event.string, event.type)
            if pedconfig.conf.verbose:
                print ("KEYSTR:", event.state, event.string)
        try:
            pedplug.keypress(self, event)
        except:
            print("plugin failed", sys.exc_info())

        self.state2 = int(event.state)
        self.handle_key2(self2, area, event)

    # Internal entry point for handling keys:
    def handle_key2(self, self2, area, event):
        if self2.record:
            if event.keyval == Gdk.KEY_F7 or \
                    event.keyval == Gdk.KEY_F8:
                #print( "avoiding record/play recursion", event)
                pass
            else:
                # event.window --- tried to pump keys to other
                # windows ... nope did not work
                # However NOT putting GTK data in the array .. allowed the
                # pickle function work OK for serializing (saving) macros

                #print( "rec", event, event.type, int(event.type))
                var = (int(event.type), int(event.keyval), int(event.state),\
                       event.string, self.shift, self.ctrl, self.alt)
                self2.recarr.append(var)

        # Ignore it, the KB driver calculates it for us. Update status bar though.
        if event.keyval == Gdk.KEY_Caps_Lock:
            if event.type == Gdk.EventType.KEY_PRESS:
                if self.state2 & Gdk.ModifierType.LOCK_MASK:
                    self2.caps = False
                else:
                    self2.caps = True
                self2.update_bar2()
            #print("caps lock", self2.caps, Gdk.EventType.KEY_PRESS )
            return

        if event.keyval == Gdk.KEY_Scroll_Lock:
            if event.type == Gdk.EventType.KEY_PRESS:

                #print("scroll lock", event.keyval, event.string, \
                #    self.state2, hex(self.state2))

                self2.scr = not self2.scr
                self2.update_bar2()
            return

        ret = self.handle_modifiers(self2, area, event)

        # Propagate to document (just for easy access)
        self2.ctrl = self.ctrl
        self2.alt = self.alt
        self2.shift = self.shift
        self2.super = self.super
        self2.rsuper = self.rsuper

        if ret: return

        if pedconfig.conf.pgdebug > 5:
            print("mods", "ctrl ",  self.ctrl, "alt ", self.alt,  "rctrl", self.rctrl)
            print("    ", "super", self.super, "ralt", self.ralt, "rsuper", self.rsuper)

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

        #print( "executing key ", \)
        #    event, event.type, event.keyval, event.window

        # Call the appropriate handlers. Note the priority.
        if self.ralt:
            self.alt = self2.alt = False
            ret =  self.handle_right_alt_key(self2, area, event)
            # Was a new combo ... done
            if ret:
                return

        # Key priorities are derived fro the order of tests
        if self.super and self.ctrl and self.alt:
            self.handle_super_ctrl_alt_key(self2, area, event)
        elif self.super and self.alt:
            self.handle_super_alt_key(self2, area, event)
        elif self.ctrl and self.alt:
            self.handle_ctrl_alt_key(self2, area, event)
        elif self.super:
            self.handle_super_key(self2, area, event)
        elif self.alt:
            self.handle_alt_key(self2, area, event)
        elif self.rctrl:
            self.handle_rctrl_key(self2, area, event)
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
            if event.keyval == Gdk.KEY_Alt_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Alt R down")
                self.ralt = True
                ret = True

            if event.keyval == Gdk.KEY_Shift_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Shift R down")
                self.rshift = True
                ret = True

            if event.keyval == Gdk.KEY_Control_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Control R down")
                self.rctrl = True
                ret = True

            if event.keyval == Gdk.KEY_Super_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Super R down")
                self.rsuper = True
                ret = True

            # ------------------------------------------------------------

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                #print( "Alt down")
                #self2.flash(True)
                #self.alt = True;
                ret = True
            elif event.keyval == Gdk.KEY_Control_L or \
                    event.keyval == Gdk.KEY_Control_R:
                #print( "Ctrl down")
                #self.ctrl = True;
                ret = True
            if event.keyval == Gdk.KEY_Shift_L or \
                  event.keyval == Gdk.KEY_Shift_R:
                #print( "shift down")
                #self.shift = True;
                ret = True

        # Do key up
        elif  event.type == Gdk.EventType.KEY_RELEASE:

            if event.keyval == Gdk.KEY_Alt_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Alt R up")
                self.ralt = False
                ret = True

            if event.keyval == Gdk.KEY_Shift_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Shift R up")
                self.rshift = False
                ret = True

            if event.keyval == Gdk.KEY_Control_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Control R up")
                self.rctrl = False
                ret = True

            if event.keyval == Gdk.KEY_Super_R:
                if pedconfig.conf.pgdebug > 6:
                    print( "Super R up")
                self.rsuper = False
                ret = True

            # ------------------------------------------------------------

            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                #print( "Alt up")
                #self2.flash(False)
                #self.alt = False;
                ret = True
            if event.keyval == Gdk.KEY_Control_L or \
                  event.keyval == Gdk.KEY_Control_R:
                #print( "Ctrl up")
                #self.ctrl = False;
                ret = True
            if event.keyval == Gdk.KEY_Shift_L or \
                  event.keyval == Gdk.KEY_Shift_R:
                #print( "shift up")
                #self.shift = False;
                ret = True

            #if self.state2  & Gdk.ModifierType.LOCK_MASK:
            #    ret = True

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

        #if event.state & GDK_MOD4_MASK:
        #if self.state2  & GDK_MOD4_MASK:
        if self.state2  & GDK_SUPER_MASK:
            self.super = True
        else:
            self.super = False

        #if event.state & GDK_CONTROL_MASK:
        if self.state2  & Gdk.ModifierType.CONTROL_MASK:
            self.ctrl = True
        else:
            self.ctrl = False

        return ret

    def handle_right_alt_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_right_alt_key",self.ctrl, self.shift)
        ret = self._handle_key(self2, area, event, self.right_alt_keytab)
        return ret

    # --------------------------------------------------------------------
    # Control Alt keytab

    def handle_ctrl_alt_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_ctrl_alt_key")
        self._handle_key(self2, area, event, self.ctrl_alt_keytab)

    # --------------------------------------------------------------------
    # Super keytabs

    def handle_super_alt_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_super_alt_key")
        self._handle_key(self2, area, event, self.super_alt_keytab)

    def handle_super_ctrl_alt_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_super_ctrl_alt_key")
        self._handle_key(self2, area, event, self.super_ctrl_alt_keytab)

    def handle_super_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_super_key")
        self._handle_key(self2, area, event, self.super_keytab)

    # --------------------------------------------------------------------
    # Control keytab

    def handle_ctrl_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_ctrl_key")
        self._handle_key(self2, area, event, self.ctrl_keytab)

    def handle_rctrl_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_ctrl_key")
        self._handle_key(self2, area, event, self.rctrl_keytab)

    # --------------------------------------------------------------------
    # Regular keytab

    def handle_reg_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_ctrl_key")
        # Handle multi key press counts by resetting if not that key
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval != Gdk.KEY_Home:
                self.acth.was_home = 0
            if event.keyval != Gdk.KEY_End:
                self.acth.was_end = 0

        self._handle_key(self2, area, event, self.reg_keytab)

    # --------------------------------------------------------------------
    # Alt key

    def handle_alt_key(self, self2, area, event):
        if pedconfig.conf.pgdebug > 5:
            print("handle_alt_key")
        if  event.type == Gdk.EventType.KEY_PRESS:
            if pedconfig.conf.pgdebug > 5:
                print( "alt hand", event)

            if event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_9:
                if pedconfig.conf.pgdebug > 5:
                    print( "Keyhand Alt num", event.keyval - Gdk.KEY_1)
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
        self2.curr_event = event
        #print( event)
        ret = True
        if  event.type == Gdk.EventType.KEY_PRESS:
            gotkey = False
            for kk, func in xtab:
                if event.keyval == kk:
                    gotkey = True
                    self2.lastkey = kk
                    func(self2)
                    break
            # No key assignment found, assume char
            if not gotkey:
                ret = False
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
                    self.acth.add_key(self2, event)

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

        #print("handle key", ret)
        return ret

# EOF
