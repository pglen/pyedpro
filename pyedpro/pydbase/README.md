# pydbase (see blockcain at the end)

## High speed database with key / data

  The motivation was to create a no frills way of saving / retrieving data.
It is fast, and the time test shows that this is an order of magnitude
faster than most mainstream databases. This is due to the engine's simplicity.
It avoids expensive computations in favor of quickly saving data.

### Fast data save / retrieve

Mostly ready for production. All tests pass. Please use caution, as this is new.
The command line tester can drive most aspects of this API; and it is somewhat
complete. It is also  good way to see the API / Module in action.

## API

  The module 'twincore' uses two data files and a lock file. The file
 names are generated from the base name of the data file;
name.pydb for data; name.pidx for the index, name.lock for the lock file.
 In case of frozen process the lock file times out in xx seconds
and breaks the lock. If the locking process (id in lockfile) does
not exist, the lock breaks immediately.

Setting verbosity and debug level:

    twincore.core_quiet   = quiet
    twincore.core_verbose = verbose
    twincore.core_pgdebug = pgdebug
    twincore.core_showdel = sdelx

 (Setting before data creation will display mesages from the construtor)

Example db creation:

    core = twincore.TwinCore(datafile_name)

Some basic ops:

    dbsize = core.getdbsize()

    core.save_data(keyx, datax)
    rec_arr = core.retrieve(keyx, ncount)
    print("rec_arr", rec_arr)

### Structure of the data:

    32 byte header, starting with FILESIG

    4 bytes    4 bytes          4 bytes         Variable
    ------------------------------------------------------------
    RECSIG     Hash_of_key      Len_of_key      DATA_for_key
    RECSEP     Hash_of_payload  Len_of_payload  DATA_for_payload

        .
        .

    RECSIG     Hash_of_key      Len_of_key      DATA_for_key
    RECSEP     Hash_of_payload  Len_of_payload  DATA_for_payload

    where:
    RECSIG="RECB" (record begin here)
    RECSEP="RECS" (record separated here)
    RECDEL="RECX" (record deleted)

    Deleted records are marked with the RECSIG mutated from RECB to RECX

      Vacuum will remove the deleted records; Make sure your database has no
    pending ops; or non atomic opts;

        (like: find keys - delete keys in two ops)

      New data is appended to the end, no duplicate filtering is done.
    Retrieval is searched from reverse, the latest record with this key
    is retrieved first. Most of the times this behavior is what we
    want; also the record history is kept this way, also a desirable
    behavior.

## The db exerciser executable script 'pydbase.py':

   The file pydbase.py exercises most of the twincore functionality. It also
provides examples of how to drive it.

 The command line utility's help response:

    Usage: pydebase.py [options] [arg_key arg_data]
     Options: -h         help (this screen)   -|-  -i   show deleted on dump
              -V         print version        -|-  -q   quiet on
              -d         debug level (0-10)   -|-  -v   increment verbosity level
              -r         randomize data       -|-  -w   write fixed record(s)
              -z         dump backwards(s)    -|-  -i   show deleted record(s)
              -U         Vacuum DB            -|-  -R   reindex / recover DB
              -I         DB Integrity check   -|-  -c   set check integrity flag
              -s         Skip to count recs   -|-  -K   list keys only
              -y  key    find by key          -|-  -m   dump data to console
              -o  offs   get data from offset -|-  -e  offs   delete at offset
              -u  rec    delete at position   -|-  -g  num    get number of recs.
              -k  key    key to save          -|-  -a  str    data to save
              -S         print num recs       -|-  -D  key    delete by key
              -n  num    number of records    -|-  -t  key    retrieve by key
              -p  num    skip number of records on get
              -l  lim    limit number of records on get
              -x  max    limit max number of records to get
              -f  file   input or output file (default: 'data/pydbase.pydb')
    The default action is to dump records to screen in reverse order.
    On the command line, use quotes for multi word arguments.

### Comparison to other databases:

 This comparison is to show the time it takes to write 500 records.
In the tests the record size is about the same (Hello, 1  /vs/ "Hello", 1)
Please see the sqlite_test.sql for details of data output;

The test can be repeated with running the 'time.sh' script file.
Please note the the time.sh clears all files test_data/* for a fair test.

        sqlite time test, writing 500 records ...
        real	0m1.730s
        user	0m0.110s
        sys	0m0.455s

        pydbase time test, writing 500 records ...
        real	0m0.120s
        user	0m0.075s
        sys	0m0.044s

        -rw-r--r-- 1 peterglen users  4032 Feb  7 15:35 pydb_test.pidx
        -rw-r--r-- 1 peterglen users 15032 Feb  7 15:35 pydb_test.pydb
        -rw-r--r-- 1 peterglen users 20480 Feb  7 15:35 sqlite_test.db

  Please mind the fact that the sqlite engine has to do a lot of parsing which we
skip doing; That is why pydbase is more than an order of magnitude faster ...

### Saving more complex data

  The database saves a key / value pair. However, the key can be mutated to contain
meta data. (for example adding a string in front of it.)
[like: CUST_  for customer data / details]
Also the key can be made unique by adding a UUID to it.

  The data can consist of any text / binary. The library pypacker.py can pack any data
into a string; A copy of pypacker is included here.

## pypacker.py

 This module can pack arbitrary python data into a string; which can be used to store
anything in the pydbase key / data sections.

Example from running testpacker.py:

        org: (1, 2, 'aa', ['bb', b'dd'])
        packed: pg s4 'iisa' i4 1 i4 2 s2 'aa' a29 'pg s2 'sb' s2 'bb' b4 'ZGQ=' '
        unpacked: [1, 2, 'aa', ['bb', b'dd']]
        rec_arr: pg s4 'iisa' i4 1 i4 2 s2 'aa' a29 'pg s2 'sb' s2 'bb' b4 'ZGQ=' '
        rec_arr_upacked: [1, 2, 'aa', ['bb', b'dd']]
        (Note: the decode returns an array of data; use data[0] to get the original)

  There is also the option of using pypacker on the key itself. Because the key
is identified by its hash, there is no speed penalty; Note that the hash is a 32 bit
one; collisions are possible, however unlikely; To compensate, make sure you compare the
key proper with the returned key.

## PyTest

 The pytest passes with no errors; Run it from the tests/ directory.

 The following (and more) test are created / executed:

    collected 24 items

    test_bindata.py .                                                        [  4%]
    test_create.py .....                                                     [ 25%]
    test_del.py .                                                            [ 29%]
    test_dump.py .                                                           [ 33%]
    test_find.py ..                                                          [ 41%]
    test_findrec.py ..                                                       [ 50%]
    test_getrec.py .                                                         [ 54%]
    test_integrity.py .                                                      [ 58%]
    test_multi.py .                                                          [ 62%]
    test_packer.py ......                                                    [ 87%]
    test_randdata.py .                                                       [ 91%]
    test_reindex.py .                                                        [ 95%]
    test_vacuum.py .                                                         [100%]

## Maintenance

  The DB can rebuild its index and purge all deleted records. In the test utility
the options are:

        ./pydbase.py -U     for vacuum (add -v for verbosity)

  The database is re-built, the deleted entries are purged, the damaged data (if any)
  is saved into a separate file, created with the same base name as the data base,
  with the '.perr' extension.

        ./pydbase.py -R     for re-index

  The index is recreated; as of the current file contents. This is useful if
the index is lost (like copying the data only)

  If there is a data file without the index, the re-indexing is called
 automatically.   In case of deleted data file, pydbase will recognize
 the dangling index and nuke it by renaming it to
 orgfilename.pidx.dangle (Tue 07.Feb.2023 just deleted it);

  Note about the 'garbage' and 'old_tries' directory ... older stuff I
tried; some are really useful; For instance take a look at the
simplifier: an array of indexes to save offsets and lengths; The
simplifier makes one range out of overlapping or close to each other
ranges. (min. dist=4)

  The database grows with every record added to it. It does not check if
 the particular record already exists. It adds the new record version to
the end; Retrieving starts from the end, and the data retrieved
(for this particular key) is the last record saved. All the other records
of this key are also there in chronological (save) order. Miracle of
record history archived by default.

  To clean the old record history, one may delete all the records with
this same key, except the last one.

# Blockcain implementation

   The database is extended with a blockhcain implementation. The new class
is called twinchain; and it is a class derived from twincore.

  To drive the blockchain, just use the append method. Th database will calculate
all the hashes, integrate it into the existing chain with the new item getting
a backlink field. This field is calulated based upon the previous record's
hash and the previous record frozen date. This assures that identical data
will have a different hash, so data cannot be anticipated based upon its hash
alone.

To drive it:

        core = twinchain.TwinChain()    # Takes an optional file name
        #core.core_verbose = verbose    # Give details as it operates
        core.append("The payload")      # Arbitrary data

## Integrity check

   Two levels; Level one is checking if the record checksums are correct;
   Level two checks if the linkage is correct.

### TODO

    Speed this up by implementing this as a 'C' module

; EOF
