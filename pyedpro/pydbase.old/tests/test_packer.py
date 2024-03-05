#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

# Test for pydbase

packer = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""

    global packer
    packer = pypacker.packbin()

    try:
        # Fresh start
        pass
    except:
        #print(sys.exc_info())
        pass

varp = 12
org =  "1234"
longz = "12340-9540987sdkljsdfakjbsdfkbds[p]" \
        "[jfaskljhfsdkljfdskjlsadfdasd], dsadsdd"

compz = ["12340-9540987sdkljsdfakjbsdfkbds", [varp],
                ["jfaskljhfsdkljfdskjlsadfdasd"], "dsadsdd"]

dictz = [ {"z123409540987sdkljsdfakjbsdfkbds": varp},
                ["jfaskljhfsdkljfdskjlsadfdasd"], "dsadsdd"]

def test_packer(capsys):

    ddd = packer.encode_data("", org)
    print(ddd)
    captured = capsys.readouterr()

    out = "pg s1 's' s4 '1234' \n"
    assert captured.out == out

def test_enc_dec(capsys):

    ddd = packer.encode_data("", org)
    dec = packer.decode_data(ddd)
    assert org == dec[0]

def test_longz(capsys):

    ddd = packer.encode_data("", longz)
    dec = packer.decode_data(ddd)
    assert longz == dec[0]

def test_compz(capsys):

    ddd = packer.encode_data("", compz)
    dec = packer.decode_data(ddd)
    assert compz == dec[0]

def test_dictz(capsys):

    ddd = packer.encode_data("", dictz)
    eee = \
        "pg s1 'a' a174 'pg s3 'das' d90 'pg s1 'a' a73 "\
        "'pg s1 't' t56 'pg s2 'si' s32 'z123409540987sdkljsdfakjbsdfkbds'"\
        " i4 12 ' ' ' a45 'pg s1 's' s28 'jfaskljhfsdkljfdskjlsadfdasd' '"\
        " s7 'dsadsdd' ' "

    assert ddd == eee
    dec = packer.decode_data(ddd)
    assert dictz == dec[0]

def test_packer_complex(capsys):

    org = [11, ["ss", "dd"], "rr"]
    ddd = packer.encode_data("", org)
    #print(ddd)
    #captured = capsys.readouterr()
    eee = packer.decode_data(ddd)
    assert org == eee[0]


# EOF
