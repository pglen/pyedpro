import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk, Gdk

# This would typically be its own file

curarr = (Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR ),
    Gdk.Cursor(Gdk.CursorType.X_CURSOR ),
    Gdk.Cursor(Gdk.CursorType.BOGOSITY ),
    Gdk.Cursor(Gdk.CursorType.RIGHTBUTTON ),
    Gdk.Cursor(Gdk.CursorType.RTL_LOGO ),
    Gdk.Cursor(Gdk.CursorType.SAILBOAT ),
    Gdk.Cursor(Gdk.CursorType.SB_DOWN_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SB_H_DOUBLE_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SB_LEFT_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SB_RIGHT_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SB_UP_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SB_V_DOUBLE_ARROW ),
    Gdk.Cursor(Gdk.CursorType.SHUTTLE ),
    Gdk.Cursor(Gdk.CursorType.BOTTOM_LEFT_CORNER ),
    Gdk.Cursor(Gdk.CursorType.SIZING ),
    Gdk.Cursor(Gdk.CursorType.SPIDER ),
    Gdk.Cursor(Gdk.CursorType.SPRAYCAN ),
    Gdk.Cursor(Gdk.CursorType.STAR ),
    Gdk.Cursor(Gdk.CursorType.TARGET ),
    Gdk.Cursor(Gdk.CursorType.TCROSS ),
    Gdk.Cursor(Gdk.CursorType.TOP_LEFT_ARROW ),
    Gdk.Cursor(Gdk.CursorType.TOP_LEFT_CORNER ),
    Gdk.Cursor(Gdk.CursorType.TOP_RIGHT_CORNER ),
    Gdk.Cursor(Gdk.CursorType.TOP_SIDE ),
    Gdk.Cursor(Gdk.CursorType.BOTTOM_RIGHT_CORNER ),
    Gdk.Cursor(Gdk.CursorType.TOP_TEE ),
    Gdk.Cursor(Gdk.CursorType.TREK ),
    Gdk.Cursor(Gdk.CursorType.UL_ANGLE ),
    Gdk.Cursor(Gdk.CursorType.UMBRELLA ),
    Gdk.Cursor(Gdk.CursorType.UR_ANGLE ),
    Gdk.Cursor(Gdk.CursorType.WATCH ),
    Gdk.Cursor(Gdk.CursorType.XTERM ),
    Gdk.Cursor(Gdk.CursorType.LAST_CURSOR ),
    Gdk.Cursor(Gdk.CursorType.BOTTOM_SIDE ),
    Gdk.Cursor(Gdk.CursorType.BOTTOM_TEE ),
    Gdk.Cursor(Gdk.CursorType.ARROW ),
    Gdk.Cursor(Gdk.CursorType.BOX_SPIRAL ),
    Gdk.Cursor(Gdk.CursorType.CENTER_PTR ),
    Gdk.Cursor(Gdk.CursorType.CIRCLE ),
    Gdk.Cursor(Gdk.CursorType.CLOCK ),
    Gdk.Cursor(Gdk.CursorType.COFFEE_MUG ),
    Gdk.Cursor(Gdk.CursorType.CROSS ),
    Gdk.Cursor(Gdk.CursorType.CROSS_REVERSE ),
    Gdk.Cursor(Gdk.CursorType.CROSSHAIR ),
    Gdk.Cursor(Gdk.CursorType.DIAMOND_CROSS ),
    Gdk.Cursor(Gdk.CursorType.DOT ),
    Gdk.Cursor(Gdk.CursorType.BASED_ARROW_DOWN ),
    Gdk.Cursor(Gdk.CursorType.DOTBOX ),
    Gdk.Cursor(Gdk.CursorType.DOUBLE_ARROW ),
    Gdk.Cursor(Gdk.CursorType.DRAFT_LARGE ),
    Gdk.Cursor(Gdk.CursorType.DRAFT_SMALL ),
    Gdk.Cursor(Gdk.CursorType.DRAPED_BOX ),
    Gdk.Cursor(Gdk.CursorType.EXCHANGE ),
    Gdk.Cursor(Gdk.CursorType.FLEUR ),
    Gdk.Cursor(Gdk.CursorType.GOBBLER ),
    Gdk.Cursor(Gdk.CursorType.GUMBY ),
    Gdk.Cursor(Gdk.CursorType.HAND1 ),
    Gdk.Cursor(Gdk.CursorType.BASED_ARROW_UP ),
    Gdk.Cursor(Gdk.CursorType.HAND2 ),
    Gdk.Cursor(Gdk.CursorType.HEART ),
    Gdk.Cursor(Gdk.CursorType.ICON ),
    Gdk.Cursor(Gdk.CursorType.IRON_CROSS ),
    Gdk.Cursor(Gdk.CursorType.LEFT_PTR ),
    Gdk.Cursor(Gdk.CursorType.LEFT_SIDE ),
    Gdk.Cursor(Gdk.CursorType.LEFT_TEE ),
    Gdk.Cursor(Gdk.CursorType.LEFTBUTTON ),
    Gdk.Cursor(Gdk.CursorType.LL_ANGLE ),
    Gdk.Cursor(Gdk.CursorType.LR_ANGLE ),
    Gdk.Cursor(Gdk.CursorType.BOAT ),
    Gdk.Cursor(Gdk.CursorType.MAN ),
    Gdk.Cursor(Gdk.CursorType.MIDDLEBUTTON ),
    Gdk.Cursor(Gdk.CursorType.MOUSE ),
    Gdk.Cursor(Gdk.CursorType.PENCIL ),
    Gdk.Cursor(Gdk.CursorType.PIRATE ),
    Gdk.Cursor(Gdk.CursorType.PLUS ),
    Gdk.Cursor(Gdk.CursorType.QUESTION_ARROW ),
    Gdk.Cursor(Gdk.CursorType.RIGHT_PTR ),
    Gdk.Cursor(Gdk.CursorType.RIGHT_SIDE ),
    Gdk.Cursor(Gdk.CursorType.RIGHT_TEE ),
    )


curnames = ( \
    "none",
    "default",
    "help",
    "pointer",
    "context-menu",
    "progress",
    "wait",
    "cell",
    "crosshair",
    "text",
    "vertical-text",
    "alias",
    "copy",
    "no-drop",
    "move",
    "not-allowed",
    "grab",
    "grabbing",
    "all-scroll",
    "col-resize",
    "row-resize",
    "n-resize",
    "e-resize",
    "s-resize",
    "w-resize",
    "ne-resize",
    "nw-resize",
    "sw-resize",
    "se-resize",
    "ew-resize",
    "ns-resize",
    "nesw-resize",
    "nwse-resize",
    "zoom-in",
    "zoom-out",
)


class MainWindow(Gtk.Window):

    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.set_size_request(200, 200)
        vbox = Gtk.FlowBox()
        self.connect("unmap", self.exit_app)
        '''for aa in range(len(curarr)):
            if curarr[aa].get_image():
                image = Gtk.Image.new_from_pixbuf(curarr[aa].get_image())
                image.set_tooltip_text("%s" % str(curarr[aa].get_cursor_type() ))
                vbox.insert(image, aa)
            else:
                print ("No image %s" % str(curarr[aa].get_cursor_type() ))
        '''

        disp =
        for aa in range(len(curnames)):
            print(curnames[aa])
            new_from_name(disp, curnames[aa])


        self.add(vbox)
        self.show_all()

    def exit_app(self, parm):
        Gtk.main_quit()


# -----------------------------------------------------------------------

if __name__ == "__main__":

    mw = MainWindow()
    Gtk.main()

