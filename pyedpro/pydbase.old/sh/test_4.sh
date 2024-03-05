#!/bin/bash

# Start a lot of processes (test pydbase)

mkdir -p data
rm -f data/*

echo Started test with 1200 processes \(please wait for completion\)
for aa in  {1..100}
do
    ./sh/test_3.sh &
done
echo When done, execute ./pydbase.py -I for integrity check
