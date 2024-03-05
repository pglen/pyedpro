#!/bin/bash

# Wait for stuff to change, exec $1 $2 ...

while [ 1 ]; do
    echo "(re)Started monitor file(s) $2 $3 $4"
    inotifywait $2 $3 $4 > /dev/null 2>&1
    #echo Changed exec $1 $2
    $1 $2
    sleep 1
done

