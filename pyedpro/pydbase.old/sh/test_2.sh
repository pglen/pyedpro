#!/bin/bash

mkdir -p data
rm -f data/*

for aa in  {1..10}
do
    ./pydbase.py -w -r
done

./pydbase.py -m $1
