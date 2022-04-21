#!/usr/bin/env python

# Levenstein distance. Converted from CPP

#import re, string, gtk, glib, gobject

from __future__ import print_function
#from six.moves import range
darr = []; 
MXDIM   =   36
 
#//****************************
#// Get minimum of three values
#//****************************

def  Minimum(a, b, c):
    
    mi = a;
    if b < mi:
        mi = b
    if c < mi:
        mi = c
        
    return mi

#//****************************
#// Show Matrix
#//****************************

def show_mx(darr):
    cnt = 0
    for ii in darr:
        cnt2 = 0
        for iii in ii:
            print(darr[cnt][cnt2], end=' ')
            cnt2 += 1
        print()
        cnt += 1 
    print()   

#//****************************
#// Create Matrix
#//****************************

def create_mx():

    global darr
    
    # Create two dimentional list
    for ii in range(MXDIM):
        darr2 = []
        for iii in range(MXDIM):
            darr2.append(0)
        darr.append(darr2[:])
   
#//*****************************
#// Compute Levenshtein distance
#//*****************************

def     Distance (s, t):
    
    global darr

    n = len(s);  m = len(t);

    if n > MXDIM or m > MXDIM:
        print("Levenshtine -- Warn: Array Dim exceeded ", s, t)
        return MXDIM
        
    #print "'" + s+ "'", "'" + t + "'"
    #print "n", n, "m", m

    #// If any of them is empty ... return len() of the other
    if (n == 0):  return m;
    if (m == 0):  return n;
    
    cost = 0
    
    #// Step 1     Create matrix
    if len(darr) == 0:
        create_mx()
        
    #// Step 2      Fill matrix
    for ii in range(n+1):
        darr[ii][0] = ii
    for ii in range(m+1):
        darr[0][ii] = ii
      
    #// Step 3 Eval matrix
    for ii in range(1, n+1):
        s_i = s[ii-1]
        for iii in range(1, m+1):
            t_j = t[iii - 1]
            if (s_i == t_j):
                cost = 0
            else:  
                cost = 1
            above = darr[ii-1][iii]         # GetAt (d,i-1,j, n);
            left  = darr[ii][iii-1]         # GetAt (d,i, j-1, n);
            diag =  darr[ii-1][iii-1]       # GetAt (d, i-1,j-1, n);
            cell = Minimum(above + 1, left + 1, diag + cost)
            darr[ii][iii] = cell            # PutAt (d, i, j, n, cell);
    result = darr[n][m]                
    return result;
            































