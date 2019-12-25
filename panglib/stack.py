#!/usr/bin/env python

class Stack():

    def __init__(self):
        self._store = []
        self.reset()

    def push(self, item):
        try:
            self._store.append(item)
        except Exception as xxx:
            print (xxx)
        self.cnt = self.cnt+1

    def last(self):
        xlen = len(self._store)
        if xlen == 0: return None
        item = self._store[xlen - 1]
        return item

    def first(self):
        xlen = len(self._store)
        if xlen == 0: return None
        item = self._store[0]
        return item

    def pop(self):
        if len(self._store) == 0: return None
        item = self._store.pop(len(self._store) - 1)
        return item

    def get(self):
        if len(self._store) == 0: return None
        item = self._store.pop(0)
        return item

    # Non destructive pop
    def pop2(self):
        if self.cnt <= 0: return None
        self.cnt = self.cnt - 1
        item = self._store[self.cnt]
        return item

    # Non destructive get
    def get2(self):
        if self.gcnt >= len(self._store): return None
        item = self._store[self.gcnt]
        self.gcnt = self.gcnt + 1
        return item

    # Start counters fresh
    def reset(self):
        self.cnt = 0
        self.gcnt = 0

    def stacklen(self):
        return len(self._store)

    def dump(self):
        cnt = 0; xlen = len(self._store)
        while cnt < xlen:
            print (self._store[cnt]);  cnt += 1

    def show(self):
        cnt = len(self._store) - 1
        while cnt >= 0:
            print (self._store[cnt]);  cnt -= 1

if __name__ == "__main__":
    print ("This module was not meant to operate as main.")

# EOF



