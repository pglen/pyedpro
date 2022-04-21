import os, sys
from pyedpro import mainstart

if __name__ == '__main__':
    #print("Exe pyedpro with", sys.argv, os.getcwd())
    sys.exit(mainstart("pyedpro", sys.argv, sys.path))