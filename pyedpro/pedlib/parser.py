#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import sys, os, re

# Our modules
import stack, lexer

'''
The parser needs several variables to operate.
  Quick summary of variables:
     Token definitions, Lexer tokens, Parser functions,
      Parser states, Parse state table.
See pangparser.py for documentation and examples.
'''

# Quick into: The lexer creates a stack of tokens. The parser scans
# the tokens, and walks the state machine for matches. If match
# is encountered, the parser calls the function in the state table,
# and / or changes state. Reduce is called after the state has been
# successfully digested. For more info see lex / yacc literature.

_gl_cnt = 0
def unique():             # create a unique temporary number
    global _gl_cnt; _gl_cnt+= 10
    return _gl_cnt

# This variable controls the display of the default action.
# The default action is executed when there is no rule for the
# expression. Mostly useful for debugging the grammar.

_show_default_action = False

# May be redefined, included here for required initial states:

ANYSTATE    = [-2, "anystate"]
REDUCE      = [-1, "reduce"]
IGNORE      = [unique(), "ignore"]
INIT        = [unique(), "init"]

# ------------------------------------------------------------------------
# This parser creates no error conditions. Bad for languages, good
# for text parsing. Warnings can be generated by enabling the
# 'show_default' action.
# The parser is not fully recursive, so states need to be nested by
# hand. The flat parser is an advantage for text processing.

class Parse():

    def __init__(self, data, xstack, pvg = None):

        self.fstack = stack.Stack()
        self.fsm = INIT; self.contflag = 0
        self.pvg = pvg
        self.pardict = {}

        # Create parse dictionary:
        for pt in parsetable:
            if pt[0] != None:
                if pt[0][1] not in self.pardict:
                    self.pardict[pt[0][1]] = dict()     # Add if new
                dd = self.pardict[pt[0][1]]
                if pt[2]:
                    #print "pt2", pt[2]
                    dd[ pt[2]] = pt[:]
                else:
                    self.add_class(dd, pt)
            else:
                for aa in pt[1]:
                    if aa[1] not in self.pardict:
                        self.pardict[aa[1]] = dict()  # Add if new
                    dd  = self.pardict[aa[1]]
                    if pt[2]:
                        #print "pt2", pt[2]
                        dd[ pt[2] ] = pt[:]
                    else:
                        self.add_class(dd, pt)

        '''for sss in self.pardict.iterkeys():
            print "Key:", sss
            for cc in self.pardict[sss].iterkeys():
                print "   Subkey:", cc
                print self.pardict[sss][cc][2:]'''

        while True:
            tt = xstack.get2()  # Gen Next token
            if not tt:
                break
            self.parse_item2(data, tt)

    def add_class(self, dd, pt):
        for aa in pt[3]:
            dd[ aa ] = pt[:]

    # This is the new routine, dictionary driven
    # About ten times as fast

    def parse_item2(self, data, tt):

        #print "parse_item", data, tt[0], tt[1].start(), tt[1].end()
        mmm = tt[1];
        self.strx = data[mmm.start():mmm.end()]
        #print "parser:", tt[0], "=", "'" + self.strx + "'"
        if self.pvg.show_state:
            print("state:", self.fsm, "str:", "'" + self.strx + "' token:", tt[0])
        try:
            curr = self.pardict[self.fsm[1]]
        except:
            print("no state on", tt[0], self.strx)
        try:
            item = curr[tt[0][0]]
        except:
            if self.pvg.show_parse:
                # show context
                bbb = mmm.start() - 5;  eee = mmm.end()+ 5
                cont = data[bbb:mmm.start()] + "'" +  self.strx + "'" + \
                        data[mmm.end():eee]

                print("no key on", tt[0], cont)
            return

        #print "item:", item

        if item[4] != None:
            item[4](self, tt, item)

        if item[5] == REDUCE:
            # This is an actionless reduce ... rare
            self.reduce(tt)

        elif item[5] == IGNORE:
            pass
        else:
            #print " Setting new state", pt[3], self.strx
            self.fstack.push([self.fsm, self.contflag, tt, self.strx])
            self.fsm = item[5]
            self.contflag = item[6]

    # This is the old routine
    def parse_item(self, data, tt):

        #print data, tt[0], tt[1].start(), tt[1].end()
        mmm = tt[1];
        self.strx = data[mmm.start():mmm.end()]

        #print "Scanning in state:", self.fsm,
        #print  "for", tt[0][1] + "=\"" + self.strx + "\""
        match = False


        # Scan parse table:
        for pt in parsetable:
            statematch = 0; classmatch = False

            if pt[0] == None:
                if self.fsm in pt[1]:
                    statematch = 1
            elif pt[0][0] == self.fsm[0]:
                   statematch = 1

            if not statematch:
                #print "Not in state: ", pt[0][0]
                continue

            # See if we have a class match
            if pt[3] != None:
                if tt[0][0] in pt[3]:
                    classmatch = True

            #print "tt[0][0]=", tt[0][0], "tt[0][1]=", tt[0][1], "pt[2]", pt[2]
            if classmatch or tt[0][0] == pt[2]:
                #print " matching table entry ", pt[0], pt[1]
                match = True
                if pt[4] != None:
                    pt[4](self, tt, pt)

                if pt[5] == REDUCE:
                    # This is an actionless reduce ... rare
                    self.reduce(tt)

                elif pt[5] == IGNORE:
                    pass
                else:
                    #print " Setting new state", pt[3], self.strx
                    self.fstack.push([self.fsm, self.contflag, tt, self.strx])
                    self.fsm = pt[5]
                    self.contflag = pt[6]
                # Done working, next token
                break;

        if not match:
            if _show_default_action:
                print(" default action on",  tt[0], "'" + self.strx + "'", \
                "Pos:", mmm.start())

    def popstate(self):
        self.fsm, self.contflag, self.ttt, self.stry = self.fstack.pop()

if __name__ == "__main__":
    print("This module was not meant to operate as main.")

# EOF





