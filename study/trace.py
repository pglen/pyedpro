import sys

def trace(frame, event, arg):
    print("%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno))
    return trace

def test():
    print("Line 8")
    print("Line 9")

sys.settrace(trace)
test()
