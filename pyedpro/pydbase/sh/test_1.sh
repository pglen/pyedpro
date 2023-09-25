#!/bin/bash

mkdir -p data
rm -f data/*
echo -n "Creating data ... "
for aa in  {1..5}
do
    ./pydbase.py -k kkk$aa -a ddd$aa
    echo -n "$aa "
done

echo " OK"
echo "Dumping to screen:"
./pydbase.py -m
