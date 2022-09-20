#!/usr/bin/env python3
import time

while True:
    try:
        x = input("enter something...")
    except EOFError:
        break # no more input

    print(x)
    time.sleep(1)
