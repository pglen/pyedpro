#!/bin/bash

D1=./locale/de_DE/LC_MESSAGES
D2=./locale/zh_CN/LC_MESSAGES

mkdir -p $D1
mkdir -p $D2

msgfmt po/de_DE.po -o $D1/pyedpro.mo
msgfmt po/zh_CN.po -o $D2/pyedpro.mo


