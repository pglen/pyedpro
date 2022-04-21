import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, WebKit2

window = Gtk.Window()
window.set_default_size(800, 600)
window.connect("destroy", Gtk.main_quit)

vbox = Gtk.VBox()

scrolled_window = Gtk.ScrolledWindow()
webview = WebKit2.WebView()
webview.load_uri("https://google.cl")
scrolled_window.add(webview)

vbox.pack_start(Gtk.Label("Hello"), 0, 0, 0)
vbox.pack_start(Gtk.Label("Hello2"), 0, 0, 0)
vbox.pack_start(scrolled_window, 1, 1, 0)

window.add(vbox)

window.show_all()
Gtk.main()
