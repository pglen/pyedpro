mkdir -p data
rm -f data/*

for aa in  {1..500}
do
    ./pydbase.py -k $$ -a $(./randstr.sh $(($RANDOM%10 + 2)))
done

