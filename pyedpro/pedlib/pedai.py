#!/usr/bin/env python3

import signal, os, time, sys, subprocess, platform, socket
import ctypes, datetime, sqlite3, warnings, threading
import json
import select

try:
    import requests
except:
    pass

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *

from pyvguicom.pggui import *
from pyvguicom.pgsimp import *
from pyvguicom.pgbutt import *
from pyvguicom.pgsel import *
from pyvguicom.browsewin import *

try:
    import httpx
except:
    #print("cannot import httpx")
    pass
try:
    #from    ollama import Ollama
    import  ollama
except:
    #print("cannot import ollama")
    pass

try:
    # This will change once the pydbase is out of dev stage
    np = os.path.split(__file__)[0] + os.sep + '..' + os.sep + ".." + os.sep + ".."
    #print(np)
    #np =  '..' + os.sep + "pydbase"
    sys.path.append(np)
    np += os.sep + "pydbase"
    sys.path.append(np)

    #print(sys.path)
    #print(os.getcwd())
    from pydbase import twincore
except:
    np =  os.path.split(__file__)[0] + os.sep + '..' + os.sep + "pydbase"
    sys.path.append(np)
    print(sys.path[-3:])

    from pydbase import twincore
    #put_exception("Cannot Load twincore")

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "llama3",
    "keep_alive": "5m",
    "stream": True,
    }

# ------------------------------------------------------------------------

class pgAI(Gtk.VBox):

    def __init__(self):

        self.sock = None
        self. wasin = True
        self.stop = False
        #vbox = Gtk.VBox()
        Gtk.VBox.__init__(self)

        self.exename  = "ollama"
        self.modelname = "llama3.2:1b"

        vbox5 = Gtk.VBox()
        hbox13a = Gtk.HBox()
        hbox13b = Gtk.HBox()

        #frame4 = Gtk.Frame();
        #scrolled_window = Gtk.ScrolledWindow()
        #frame4.add(scrolled_window)
        #vbox5.pack_start(frame4, 1, 1, 0)
        #vpaned.add(vbox5)

        self.tv = Gtk.TextView()
        self.tv.set_wrap_mode(Gtk.WrapMode.WORD)

        hbox2 = Gtk.HBox()
        #self.entry = Gtk.Entry()
        self.entry = Gtk.TextView()
        self.lab2 = self.entry.get_buffer()
        scroll2 = Gtk.ScrolledWindow()
        scroll2.set_size_request(-1, 100)
        scroll2.add(self.entry)
        frame = Gtk.Frame()
        #frame.set_label_widget(Gtk.Label(label="  Enter Text:  "))
        frame.add(scroll2)

        #hbox2.pack_start(Gtk.Label(label = "   "), 0, 0, 0)
        hbox2.pack_start(frame, 1, 1, 0)
        #hbox2.pack_start(Gtk.Label(label = "   "), 0, 0, 0)

        vbox5.pack_start(hbox2, 0, 0, 0)

        hbox13b.pack_start(Gtk.Label(label="  "), 1, 1, 0)
        hbox13b.pack_start(Gtk.Label(label=" Model: "), 0, 0, 0)
        self.modelN = Gtk.Entry()
        self.modelN.set_text(self.modelname)
        self.modelN.set_width_chars(12)

        hbox13b.pack_start(self.modelN, 0, 0, 0)
        hbox13b.pack_start(Gtk.Label(label=" Exe: "), 0, 0, 0)
        self.exeN = Gtk.Entry()
        self.exeN.set_width_chars(12)
        self.exeN.set_text(self.exename)
        hbox13b.pack_start(self.exeN, 0, 0, 0)

        hbox13b.pack_start(Gtk.Label(label="  "), 1, 1, 0)

        hbox13a.pack_start(Gtk.Label(label="  "), 1, 1, 0)
        butt11 = smallbutt(" [_Send ] ", self.send2, "Send query to ollama")
        hbox13a.pack_start(butt11, 0, 0, 0)
        butt11 = smallbutt(" [ Sto_p ] ", self.stopfunc, "Stop ollama query")
        hbox13a.pack_start(butt11, 0, 0, 0)
        butt11 = smallbutt(" [ Sta_rt Server ] ", self.server, "Start ollama server")
        hbox13a.pack_start(butt11, 0, 0, 0)
        hbox13a.pack_start(Gtk.Label(label="  "), 1, 1, 0)

        vbox5.pack_start(hbox13b, 0, 0, 0)
        vbox5.pack_start(hbox13a, 0, 0, 0)

        #self.butt = Gtk.Button.new_with_mnemonic("_Send")
        #self.butt.connect("clicked", self.send2)
        #hbox2.pack_start(self.butt, 0, 0, 2)

        self.lab = self.tv.get_buffer()
        self.lab.set_text("AI content will show here.")
        #self.lab = Gtk.Label(label="AI Content")
        #self.lab.set_line_wrap(True)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.tv)
        #scroll.get_vadjustment().set_upper(1000)
        #self.lab.set_line_wrap_mode(Pango.WrapMode.CHAR)
        vbox5.pack_start(scroll, 1, 1, 0)

        self.pack_start(vbox5, 1, 1, 0)
        #self.set_focus_child(self.entry)
        #self.grab_focus()
        self.connect("focus-in-event", self._focus)

        #GLib.timeout_add(100, self.init)

    def _focus(self, arg2):
        print("Focus")

    def init(self):
        print("timer fired")
        #self.entry.grab_focus()
        self.set_focus_child(self.entry)
        self.grab_focus()
        #self.set_focus(self.entry)

    def stopfunc(self, arg2):
        self.stop = True

    def connect_server(self, arg2): #prompt, context):
        pass

    def server(self, arg2):
        self.lab.set_text("")
        try:
            self.exename = self.exeN.get_text()
            ret = subprocess.Popen([self.exename, "serve", ])
        except:
            self.lab.set_text("Server said: '%s'" % (str(sys.exc_info())) )
        pass

        #print(ret)

    #def send(self, arg2): #prompt, context):
    #    #self.modelname = self.modelN.get_text()
    #    prompt = self.entry.get_text()
    #    self.lab.set_text("Query: '%s' model: '%s'" % (prompt, self.modelname))
    #    print("modelname", self.modelname)
    #
    #    usleep(20)
    #    self.stop = False
    #    try:
    #        r = requests.post('http://localhost:11434/api/generate',
    #                          json={
    #                              'model': self.modelname,
    #                              'prompt': prompt,
    #                          },
    #                          stream=True)
    #        r.raise_for_status()
    #        cnt = 1
    #        self.lab.set_text("")
    #        usleep(20)
    #        for line in r.iter_lines():
    #            print(line)
    #            body = json.loads(line)
    #            response_part = body.get('response', '')
    #            # the response streams one token at a time, print that as we receive it
    #            print(response_part, end='', flush=True)
    #
    #            old = self.lab.get_text(self.lab.get_start_iter(),
    #                                self.lab.get_end_iter(), False)
    #            #self.lab.set_text(old + response_part)
    #            self.lab.insert(self.lab.get_end_iter(),  response_part)
    #            #usleep(20)
    #            mark = self.lab.create_mark(None, self.lab.get_end_iter(), "end")
    #            self.tv.scroll_to_mark(mark, 0., False, 0., 0.)
    #
    #            #if cnt % 5 == 0:
    #            #    self.lab.set_text(self.lab.get_text() + "\n")
    #            if self.stop:
    #                self.lab.set_text(old + "\n ... Stopped ...\n")
    #                break
    #
    #            usleep(2)
    #            cnt += 1
    #            if 'error' in body:
    #                raise Exception(body['error'])
    #
    #            if body.get('done', False):
    #                return body['context']
    #    except:
    #        self.lab.set_text(str(sys.exc_info()[1]))
    #        print(sys.exc_info())
    #

    def addstr(self, resp):
        self.lab.insert(self.lab.get_end_iter(), resp)
        mark = self.lab.create_mark(None, self.lab.get_end_iter(), "end")
        self.tv.scroll_to_mark(mark, 0., False, 0., 0.)

    def send2(self, but):
        #print("but:", but)

        old = self.lab2.get_text(self.lab2.get_start_iter(),
                                    self.lab2.get_end_iter(), False)

        if not old:
            self.lab.set_text("Please input a query.")
            return

        self.lab.set_text(old)

        localhost = "127.0.0.1"; port = 11434
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((localhost, port))
        except:
            print( "Cannot connect to:", localhost + ":" + str(port), sys.exc_info()[1])
            self.lab.set_text(str(sys.exc_info()))
            raise

        #print("sock:", self.sock)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.modelname = self.modelN.get_text()
        jsonstr={
                    "model":  self.modelname,
                    "prompt": old,
                    "stream": True
                },

        body = json.dumps(jsonstr)
        body = str(body)[1:-1]
        #print("body", body)

        headers = \
        "POST /api/generate HTTP/1.1\r\n" + \
        "Host: localhost:11434\r\n" + \
        "Content-Length: %d\r\n" % (len(body)) + \
        "Content-Type: application/json\r\n" + \
        "\r\n"
        qqq = (headers + body).encode("ascii")
        #print("qqq =", qqq)
        try:
            ret = self.sock.send(qqq)
        except:
            print(sys.exc_info())
            self.lab.set_text(str(sys.exc_info()))
            return

        #print("send ret:", ret)
        #self.sock.setblocking(0)
        initial = True
        self.stop = False
        while True:
            usleep(10)
            if self.stop:
                break
            # Windows are going away ... stop
            if not self.tv.get_realized():
                break
            try:
                rr, ww, xx = select.select([self.sock, ], [], [], 0.01)
                if not rr:
                    continue
            except:
                print("exc: sel", sys.exc_info())
            retx = None
            try:
                retx = self.sock.recv(4096)
            except BlockingIOError:
                pass
            except:
                print("exc rec:", sys.exc_info())
                break
            if not retx:
                continue
            retx2 = retx.decode()
            #print("got: ['%s']" % retx2)
            ooo = {}
            if initial:
                self.lab.set_text("")
                initial = False
                idx = retx2.find("\r\n" * 2)
                retx2 = retx2[idx:]
                #print ("ini body: '%s'" % body)
            idx  = retx2.find("{"); idx2 = retx2.rfind("}")
            body = retx2[idx:idx+idx2-1]
            try:
                ooo = json.loads(body)
            except:
                print("exc: json", sys.exc_info(), body)
                self.stop = True
            #print("Json:", ooo)
            if ooo.get("done"):
                self.stop = True
                break
            if ooo.get("error"):
                self.stop = True
                break
            try:
                resp = ooo.get('response',"")
                if pedconfig.conf.verbose:
                    print ("resp: '%s'" % resp)
                self.addstr(resp)
            except:
                self.stop = True
                break
        #print("final:", ooo)
        try:
            cnt = ooo.get('eval_count')
            dur = ooo.get('eval_duration') / 1000000000
            self.addstr("\n%d tokens, %.2f seconds (%.2f toks/sec)" % \
                        (cnt, dur, cnt / dur) )
        except:
            pass
        self.sock.close()

    def __del__(self):
        #print("AI del")
        if self.sock:
            self.sock.close()

#print(dir(ollama))

# EOF
