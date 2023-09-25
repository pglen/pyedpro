mkdir -p data
#rm -f data/*

for aa in  {1..50}
do
    ./pychain.py -v -a $(./randstr.sh -n $(($RANDOM%60 + 2)))
done

