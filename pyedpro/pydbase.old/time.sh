#!/bin/bash

# Create two sets of databases, populate and time the creation

DDD=test_data
mkdir -p $DDD
rm -f $DDD/*;

echo -n "sqlite time test, writing 500 records ... "
time sqlite3 $DDD/sqlite_test.db < sqlite_test.sql

echo -n "pydbase time test, writing 500 records ... "
time ./pydbase.py -k "Hello" -a "1" -n 500 -f $DDD/pydb_test.pydb

# this ls shows you data size efficiency
ls -l $DDD

# un Comment this if you want to see / hide the data
#rm -f $DDD/*;

# EOF
