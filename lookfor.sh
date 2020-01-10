#!/bin/bash
if [ "$1" == "" ] ; then
        echo "Usage: ./lookfor.sh needle haystack_wildcard"
        exit
fi

wild="*.py"

if [ "$2" != "" ] ; then
    wild=$2
fi

echo "Looking for:" \"$1\" in \"$wild\"
find . -name "$wild" -exec grep -H "$1" {} \;















