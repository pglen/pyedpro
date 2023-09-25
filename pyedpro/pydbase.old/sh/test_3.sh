#!/bin/bash

# Write process ID and data

mkdir -p data
for aa in  {1..12}
do
    ./pydbase.py -k $$ -a $(./randstr.sh $(($RANDOM%10 + 2)))
    sleep 0.1
done
