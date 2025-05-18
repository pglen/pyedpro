#!/usr/bin/env python3
from subprocess import PIPE,Popen
with Popen(['wmctrl','-d'],stdout=PIPE,universal_newlines=True) as proc:
    for o in proc.stdout.read().splitlines():
        p = o.split()
        if len(p) < 3:continue
        w,f = p[:2]
        if f == "*":print(w)
