#!/bin/bash

while [ 1 ]
do
	for file in test_data/*
		do
		    sum1="$(md5sum "$file")"
		    sleep .1
		    sum2="$(md5sum "$file")"
		    if [ "$sum1" != "$sum2" ] ; then
		            ls test_data
		    fi
     done
done
