#!/bin/bash

# Generate a random sequence of chars on stdout

stringZ="abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ1234567890"

while getopts 'nc:h' opt; do
  case "$opt" in
    n)
      #echo "Processing option 'n'"
      stringZ="abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ 1234567890():/\_+=@#^&"
      ;;

    c)
    arg="$OPTARG"
      echo "Processing option 'c'" $arg
      ;;

    h)
      echo "use: randstr [-n] length"
      exit 0
      ;;

    ?)
      echo -e "Invalid command option.\nUsage: $(basename $0) [-n] maxlen"
      exit 1
      ;;
  esac
done

#echo $stringZ
lenx=${#stringZ}
#echo $lenx

shift "$(($OPTIND -1))"

for aa in $(seq 0 $(($1-1)))
    do
        mmm=$(($RANDOM % $lenx))
        #echo $aa, $mmm
        echo -n -e "${stringZ:$mmm:1}"
    done
echo