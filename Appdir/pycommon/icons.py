#!/usr/bin/env python3

import os, sys, getopt, signal, random, time, warnings

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
if realinc not in sys.path:
    sys.path.append(realinc)

from pgutils import  *
from pggui import  *
from pgsimp import  *

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf


# wget -q http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html -O /dev/stdout | grep '</td></tr><tr><td>.*</td><td>' | sed 's/.*<td>\(.[^<]*\).*/"\1",/'

icons = [
    "application-exit",
    "appointment-new",
    "call-start",
    "call-stop",
    "contact-new",
    "document-new",
    "document-open",
    "document-open-recent",
    "document-page-setup",
    "document-print",
    "document-print-preview",
    "document-properties",
    "document-revert",
    "document-save",
    "document-save-as",
    "document-send",
    "edit-clear",
    "edit-copy",
    "edit-cut",
    "edit-delete",
    "edit-find",
    "edit-find-replace",
    "edit-paste",
    "edit-redo",
    "edit-select-all",
    "edit-undo",
    "folder-new",
    "format-indent-less",
    "format-indent-more",
    "format-justify-center",
    "format-justify-fill",
    "format-justify-left",
    "format-justify-right",
    "format-text-direction-ltr",
    "format-text-direction-rtl",
    "format-text-bold",
    "format-text-italic",
    "format-text-underline",
    "format-text-strikethrough",
    "go-bottom",
    "go-down",
    "go-first",
    "go-home",
    "go-jump",
    "go-last",
    "go-next",
    "go-previous",
    "go-top",
    "go-up",
    "help-about",
    "help-contents",
    "help-faq",
    "insert-image",
    "insert-link",
    "insert-object",
    "insert-text",
    "list-add",
    "list-remove",
    "mail-forward",
    "mail-mark-important",
    "mail-mark-junk",
    "mail-mark-notjunk",
    "mail-mark-read",
    "mail-mark-unread",
    "mail-message-new",
    "mail-reply-all",
    "mail-reply-sender",
    "mail-send",
    "mail-send-receive",
    "media-eject",
    "media-playback-pause",
    "media-playback-start",
    "media-playback-stop",
    "media-record",
    "media-seek-backward",
    "media-seek-forward",
    "media-skip-backward",
    "media-skip-forward",
    "object-flip-horizontal",
    "object-flip-vertical",
    "object-rotate-left",
    "object-rotate-right",
    "process-stop",
    "system-lock-screen",
    "system-log-out",
    "system-run",
    "system-search",
    "system-reboot",
    "system-shutdown",
    "tools-check-spelling",
    "view-fullscreen",
    "view-refresh",
    "view-restore",
    "view-sort-ascending",
    "view-sort-descending",
    "window-close",
    "window-new",
    "zoom-fit-best",
    "zoom-in",
    "zoom-original",
    "zoom-out",
    "accessories-character-map",
    "accessories-dictionary",
    "accessories-text-editor",
    "help-browser",
    "multimedia-volume-control",
    "preferences-desktop-accessibility",
    "preferences-desktop-font",
    "preferences-desktop-keyboard",
    "preferences-desktop-locale",
    "preferences-desktop-multimedia",
    "preferences-desktop-screensaver",
    "preferences-desktop-theme",
    "preferences-desktop-wallpaper",
    "system-file-manager",
    "system-software-install",
    "system-software-update",
    "utilities-system-monitor",
    "utilities-terminal",
    "applications-development",
    "applications-engineering",
    "applications-games",
    "applications-graphics",
    "applications-internet",
    "applications-multimedia",
    "applications-office",
    "applications-other",
    "applications-science",
    "applications-system",
    "applications-utilities",
    "preferences-desktop",
    "preferences-desktop-peripherals",
    "preferences-desktop-personal",
    "preferences-other",
    "preferences-system",
    "preferences-system-network",
    "system-help",
    "audio-input-microphone",
    "battery",
    "camera-photo",
    "camera-video",
    "camera-web",
    "computer",
    "drive-harddisk",
    "drive-optical",
    "drive-removable-media",
    "input-gaming",
    "input-keyboard",
    "input-mouse",
    "input-tablet",
    "media-flash",
    "media-floppy",
    "media-optical",
    "media-tape",
    "modem",
    "multimedia-player",
    "network-wired",
    "network-wireless",
    "pda",
    "phone",
    "printer",
    "scanner",
    "video-display",
    "emblem-documents",
    "emblem-downloads",
    "emblem-favorite",
    "emblem-important",
    "emblem-mail",
    "emblem-photos",
    "emblem-readonly",
    "emblem-shared",
    "emblem-symbolic-link",
    "emblem-synchronized",
    "emblem-system",
    "emblem-unreadable",
    "face-angry",
    "face-cool",
    "face-crying",
    "face-devilish",
    "face-embarrassed",
    "face-kiss",
    "face-laugh",
    "face-monkey",
    "face-plain",
    "face-raspberry",
    "face-sad",
    "face-sick",
    "face-smile",
    "face-smile-big",
    "face-smirk",
    "face-surprise",
    "face-tired",
    "face-uncertain",
    "face-wink",
    "face-worried",
    "audio-x-generic",
    "font-x-generic",
    "image-x-generic",
    "package-x-generic",
    "text-html",
    "text-x-generic",
    "text-x-generic-template",
    "text-x-script",
    "video-x-generic",
    "x-office-address-book",
    "x-office-calendar",
    "x-office-document",
    "x-office-presentation",
    "x-office-spreadsheet",
    "folder-remote",
    "network-server",
    "network-workgroup",
    "start-here",
    "user-bookmarks",
    "user-desktop",
    "user-home",
    "user-trash",
    "appointment-soon",
    "audio-volume-high",
    "audio-volume-low",
    "audio-volume-medium",
    "audio-volume-muted",
    "battery-caution",
    "battery-low",
    "dialog-error",
    "dialog-information",
    "dialog-password",
    "dialog-question",
    "dialog-warning",
    "folder-drag-accept",
    "folder-open",
    "folder-visiting",
    "image-loading",
    "image-missing",
    "mail-attachment",
    "mail-unread",
    "mail-read",
    "mail-replied",
    "mail-signed",
    "mail-signed-verified",
    "media-playlist-repeat",
    "media-playlist-shuffle",
    "network-error",
    "network-idle",
    "network-offline",
    "network-receive",
    "network-transmit",
    "network-transmit-receive",
    "printer-error",
    "printer-printing",
    "security-high",
    "security-medium",
    "security-low",
    "software-update-available",
    "software-update-urgent",
    "sync-error",
    "sync-synchronizing",
    "task-due",
    "task-past-due",
    "user-available",
    "user-away",
    "user-idle",
    "user-offline",
    "user-trash-full",
    "weather-clear",
    "weather-clear-night",
    "weather-few-clouds",
    "weather-few-clouds-night",
    "weather-fog",
    "weather-overcast",
    "weather-severe-alert",
    "weather-showers",
    "weather-showers-scattered",
    "weather-snow",
    "weather-storm"
]


class IconViewWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self)
        self.set_title("%d icon%c" % (len(icons), '' if len(icons) < 2 else 's'))
        #self.set_default_size(660, 400)

        liststore = Gtk.ListStore(Pixbuf, str)
        iconview = Gtk.IconView.new()
        iconview.set_model(liststore)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(1)

        for icon in sorted(icons):

            if len(sys.argv) > 1 and sys.argv[1]:
                # filter
                if  not sys.argv[1].lower() in icon.lower():
                    continue

            try:
                pixbuf = Gtk.IconTheme.get_default().load_icon(icon, 32, 0)
                liststore.append([pixbuf, icon])
            except Exception as inst:
                print(inst)

        swnd = Gtk.ScrolledWindow()
        swnd.add(iconview)
        self.add(swnd)


if __name__ == '__main__':

    win = IconViewWindow()
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

    #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG, Gtk.ICON_SIZE_BUTTON)
    #window.set_icon(ic.get_pixbuf())

    #www = Gdk.Screen.width(); hhh = Gdk.Screen.height();
    disp2 = Gdk.Display()
    disp = disp2.get_default()
    #print( disp)
    scr = disp.get_default_screen()
    ptr = disp.get_pointer()
    mon = scr.get_monitor_at_point(ptr[1], ptr[2])
    geo = scr.get_monitor_geometry(mon)
    www = geo.width; hhh = geo.height
    xxx = geo.x;     yyy = geo.y

    # Resort to old means of getting screen w / h
    if www == 0 or hhh == 0:
        www = Gdk.screen_width(); hhh = Gdk.screen_height();

    if www / hhh > 2:
        win.set_default_size(5*www/8, 7*hhh/8)
    else:
        win.set_default_size(7*www/8, 7*hhh/8)

    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

