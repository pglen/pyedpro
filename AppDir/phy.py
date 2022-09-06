#!/usr/bin/python

import math

# Calc PHY by oscillating around decreasing delta. This method can be used to
# untangle every mathematical formula.

delta   = 0.001         # Initial delta  (arbitrary)
aaa     = 1.6           # Start from  something (arbitrary)
last    = 0             # Last compare state

# This is the FORMULA
#  pow(aaa, 2) == aaa + 1

for aa in range(200):
    if pow(aaa, 2) < aaa + 1:
        last = True
        aaa += delta    # Travel UP
    else:
        # Oscillating?
        if last:
            delta /= 2  # Successive approximation
        last = False
        aaa -= delta    # Travel down

    # Print details if desired
    #print(aaa, pow(aaa, 2) < aaa + 1)

# Print result
print("PHY:", aaa)


