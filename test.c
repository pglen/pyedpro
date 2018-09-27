// -------------------------------------------------------------------------
// Bluepoint encryption routines.
//
//   How it works:
//
//     Strings are walked char by char with the loop:
//
//    for (loop = 0; loop < slen; loop++)
//        {
//        aa = str[loop]; aa = aa OP bb; str[loop] = aa
//        }
//
//    In other languages:
//         {
//         $aa = ord(substr($_[0], $loop, 1));
//         do something with $aa
//         substr($_[0], $loop, 1) = pack("c", $aa);
//         }
//
//   Flow:
//         generate vector
//         generate pass
//         walk forward with password cycling loop
//         walk backwards with feedback encryption
//          ... lots of intermediate steps ...
//         walk forward with feedback encryption
//
//  The process guarantees that a single bit change in the original text
//  will change every byte in the resulting block.
//
//  The bit propagation is such a high quality, that it beats current
//  industrial strength encryptions.
//
//  The process also guarantees that a single bit change in the cypher text
//  will change every byte in the decryptrd block.
//
//  Please see bit distribution study.
//
// -------------------------------------------------------------------------
//
// How to use:
//
//  !!! Make sure the passed buffer is even sized !!!
//
//  bluepoint2_encrypt($orig, $pass);                -- encrypted in place
//  bluepoint2_decrypt($cypher, $pass);              -- decrypted in place
//  $hash       = bluepoint2_hash($orig, $pass);
//  $crypthash  = bluepoint2_crypthash($orig, $pass);
//
// The reference implementation for version 2.0 contains a (default) sample
// clear text and a sample cypher text. (exec: test_blue2)
// Porting is correct if the new cypher text and hash is a duplicate of the following:
//
// orignal='abcdefghijklmnopqrstuvwxyz' pass='1234'
// ENCRYPTED: 
// -d7-a2-55-bf-ec-3c-f6-e5-2d-ef-06-93-79-91-eb-2d-2a-f1-69-4a-59-e9-48-6f-61-05
// END ENCRYPTED
// HASH:
// 3540310577 0xd304da31
// CRYPTHASH: 
// 3349887638 0xc7ab3a96
// HASH64:
// 17370781859372208493 0xf1116a1116ae116d
// CRYPTHASH64: 
// 16348308407135931823 0xe2e0dbe115de8daf

///////////////////////////////////////////////////////////////////////////

#include "stdio.h"
#include "string.h"
#include "stdlib.h"

#define DEF_DUMPHEX  1   // undefine this if you do not want bluepoint2_dumphex

///////////////////////////////////////////////////////////////////////////
// The following defines are used to test multi platform steps.
// These will generate a cypher text incompatible with other implementations
// FOR TESTING ONLY

//define NOROTATE        1   // uncomment this if you want no rotation
//define NOPASSCRYPT     1   // uncomment this if you want no pass crypt

#include "bluepoint2.h"

#define     ROTATE_LONG_LONG_RIGHT(x, n) (((x) >> (n))  | ((x) << (64 - (n))))
#define     ROTATE_LONG_LONG_LEFT(x, n) (((x) << (n))  | ((x) >> (64 - (n))))

#define     ROTATE_LONG_RIGHT(x, n) (((x) >> (n))  | ((x) << (32 - (n))))
#define     ROTATE_LONG_LEFT(x, n) (((x) << (n))  | ((x) >> (32 - (n))))

#define     ROTATE_SHORT_RIGHT(x, n) (((x) >> (n))  | ((x) << (16 - (n))))
#define     ROTATE_SHORT_LEFT(x, n) (((x) << (n))  | ((x) >> (16 - (n))))

#define     ROTATE_CHAR_RIGHT(x, n) (((x) >> (n))  | ((x) << (8 - (n))))
#define     ROTATE_CHAR_LEFT(x, n) (((x) << (n))  | ((x) >> (8 - (n))))

#define     PASSLIM 64

#include "bluemac.h"

static  void    do_encrypt(char *str, int slen, char *pass, int plen);
static  void    do_decrypt(char *str, int slen, char *pass, int plen);
static  void    prep_pass(char *pass, int plen, char *newpass);

//# -------------------------------------------------------------------------
//# These vars can be set to make a custom encryption:

static  char vector[]  = "crypt";       //# influence encryption algorythm
//static  const int passlim  = PASSLIM;   //# maximum key length (bytes)
char hector[]  = "eahfdlaskjhl9807089609kljhkljfsdhlf";

char    forward    = 0x55;      //# Constant propagated on forward pass
char    backward   = 0x5a;      //# Constant propagated on backward pass
char    addend     = 17;        //# Constant used adding to encrypted values

//# -------------------------------------------------------------------------
//# These vars can be set show op details

static int verbose    = 0;              //# Specify this to show working details
static int debug      = 0;              //# Specify this to show debug strings
static int functrace  = 0;              //# Specify this to show function args

//# -------------------------------------------------------------------------
//# These vars can be set to influence encryption

static  int     rounds = 96;             //# How many rounds. 
                                         //# Initial value is experimental

//# -------------------------------------------------------------------------
//# Following functions set values

int    bluepoint2_set_verbose(int flag)
{
    int old = verbose;
    verbose = flag;
    return old;
}

int    bluepoint2_set_debug(int flag)
{
    int old = debug;
    debug = flag;
    return old;
}

int    bluepoint2_set_functrace(int flag)
{
    int old = functrace;
    functrace = flag;
    return old;
}

int    bluepoint2_set_rounds(int xrounds)
{
    int old = rounds; rounds  =  xrounds;
    // Prevent no encryption
    if (rounds < 1) rounds = 1;
    return old;
}
       
//# -------------------------------------------------------------------------
//# Use: encrypt($str, $password);

int    bluepoint2_encrypt(char *buff, int blen, char *pass, int plen)

{
    int ret = 0; char newpass[PASSLIM + 2]; 
    int loop;

    if (blen % 2)
        {
        blen --; ret = 1;
        }
        
    if(plen == 0 || blen == 0)
        {
        return ret;
        }

   if(functrace)
       {
       printf("bluepoint2_encrypt len=%d\nbuff='%s'\n", blen, bluepoint2_dumphex(buff, blen));
       printf("plen=%d pass='%s'\n", plen, bluepoint2_dumphex(pass, plen) );
       }

    prep_pass(pass, plen, newpass);

     if(functrace)
           {
           printf("After prep_pass %d '%s\n", plen, bluepoint2_dumphex(newpass, plen));
           }
    
    for (loop = 0; loop < rounds; loop++)
        {
        do_encrypt(buff, blen, newpass, PASSLIM);
        }
        
    if(functrace)
        {
        printf("After LOOP %d '%s\n", blen, bluepoint2_dumphex(buff, blen));
        }
        
    return ret;
}

//# -------------------------------------------------------------------------
//# Use: bluepoint2_decrypt($str, $password);

int    bluepoint2_decrypt(char *buff, int blen, char *pass, int plen)

{
    int ret = 0; char newpass[PASSLIM + 2]; int loop;
    
    if (blen % 2)
        {
        blen --; ret = 1;
        }

    if(plen == 0 || blen == 0)
        {
        return ret;
        }

    if(functrace)
        {
        printf("bluepoint2_decrypt()\nbuff=%s\n",bluepoint2_dumphex(buff, blen));
        printf("pass=%s\n", bluepoint2_dumphex(pass, plen) );
        }

    prep_pass(pass, plen, newpass);

    for (loop = 0; loop < rounds; loop++)
        {
        do_decrypt(buff, blen, newpass, PASSLIM);
        }
    return ret;
}

///////////////////////////////////////////////////////////////////////////
// Prepare pass

void    prep_pass(char *pass, int plen, char *newpass)

{
    int loop; char vec2[PASSLIM];

    // Duplicate vector
    int vlen = strlen(vector);
    strcpy(vec2, vector);
    newpass[0] = 0;

    int loop2 = 0;
    for(loop = 0; loop < PASSLIM; loop++)
        {
        newpass[loop] = pass[loop2];
        // Increment, wrap
        loop2++; if (loop2 >= plen) loop2 = 0;
        }
    // Terminate
    newpass[PASSLIM] = 0;

    if(verbose)
        printf("prep_pass() newpass: %s\n", newpass);

#ifndef NOPASSCRYPT
    do_encrypt(vec2, vlen, vector, vlen);
#endif

    if(verbose)
        {
        printf("prep_pass() eVEC: ");
        bluepoint2_dumphex(vec2, vlen);
        printf("\n");
        }

#ifndef NOPASSCRYPT
    do_encrypt(newpass, PASSLIM, vec2, vlen);
#endif

}

//# -------------------------------------------------------------------------
//# Hash:
//# use: hashvalue = hash($str)
//#
//# Implementing the following 'C' code
//#
//#   ret_val ^= (unsigned long)*name;
//#   ret_val  = ROTATE_LONG_RIGHT(ret_val, 10);          /* rotate right */sub hash
//#

ulong   bluepoint2_hash(char *buff, int blen)

{
    unsigned long    sum = 0;
    int     loop;
    char    aa, aa2, aa3;

    for (loop = 0; loop < blen; loop++)
        {
        sum ^= (unsigned char)buff[loop];
        sum = ROTATE_LONG_RIGHT(sum, 10);          /* rotate right */
        }

    return sum;
}

unsigned long long   bluepoint2_hash64(char *buff, int blen)

{
    unsigned long long  sum = 0;
    int     loop;

    for (loop = 0; loop < blen; loop++)
        {
        sum ^= (unsigned char)buff[loop];
        sum = ROTATE_LONG_LONG_RIGHT(sum, 20);    /* rotate right */
        }
    return sum;
}

//# -------------------------------------------------------------------------
//# Crypt and hash:
//# use: crypthash = bluepoint2_crypthash($str, "pass")

ulong   bluepoint2_crypthash(char *buff, int blen, char *pass, int plen)

{
    unsigned long  sum = 0;

    // Duplicate buffer
    char *duplicate = (char *)malloc(blen + 4);
    if(!duplicate)
        {
        return(0LL);
        }
    memcpy(duplicate, buff, blen);

    bluepoint2_encrypt(duplicate, blen, pass, plen);
    sum = bluepoint2_hash(duplicate, blen);

    free(duplicate);
    return(sum);
}

unsigned long long bluepoint2_crypthash64(char *buff, int blen, char *pass, int plen)

{
    unsigned long long  sum = 0;

    // Duplicate buffer
    char *duplicate = (char *)malloc(blen + 4);
    if(!duplicate)
        {
        return(0LL);
        }
    memcpy(duplicate, buff, blen);

    bluepoint2_encrypt(duplicate, blen, pass, plen);
    sum = bluepoint2_hash64(duplicate, blen);

    free(duplicate);
    return(sum);
}

//# The encryption stack:

void    ENCRYPT(char *str, int slen, char *pass, int plen)
{
    int loop, loop2 = 0;  unsigned char  aa, bb, cc;
    
    //return;
    
    PASSLOOP(+)
    MIXIT2(+)   MIXIT2R(+)
    HECTOR(+)   FWLOOP(+)
    MIXIT2(+)   MIXIT2R(+)
    PASSLOOP(+) FWLOOP(+)
    HECTOR(+)   FWLOOP(+)
    MIXIT(+)    
    MIXITR(+)
    BWLOOP(+)   HECTOR(+)
}   

void    DECRYPT(char *str, int slen, char *pass, int plen)
{
    int loop, loop2 = 0; unsigned char aa, bb, cc;
    
    //return;
    HECTOR(-)   BWLOOP2(-)
    MIXITR(-)   
    MIXIT(-)
    FWLOOP2(-)  HECTOR(-)
    FWLOOP2(-)  PASSLOOP(-)
    MIXIT2R(-)  MIXIT2(-)
    FWLOOP2(-)  HECTOR(-)
    MIXIT2R(-)  MIXIT2(-)
    PASSLOOP(-)
}

//# -------------------------------------------------------------------------
//# The following routines are internal to this module:

void    do_encrypt(char *str, int slen, char *pass, int plen)

{
    if(verbose)
        {
        printf( "encrypt str='%s' len=%d pass='%s' plen=%d\n",
                 str, slen, pass, plen);
        }
      ENCRYPT(str, slen, pass, plen);
}

//# -------------------------------------------------------------------------
//# Internal to this module:

void    do_decrypt(char *str, int slen, char *pass, int plen)

{
    if(verbose)
        {
        printf( "decrypt(inp) str=%s len=%d pass=%s plen=%d\n",
                  str, slen, pass, plen);
        }
      DECRYPT(str, slen, pass, plen);
}

//# -------------------------------------------------------------------------
// use it for testing only as it has an xxx byte buffer limit
//# Use: mystr = bluepoint2_dumphex($str)

#ifdef DEF_DUMPHEX

static unsigned char buff[4096];

char    *bluepoint2_dumphex(const char *str, int len)

{
    buff[0] = 0;  int loop = 0, pos = 0;

    if(verbose)
        {
        printf("bluepoint2_dumphex str=%p len=%d ", str, len);
        }

    for (loop = 0; loop < len; loop++)
        {
        pos += sprintf(buff + pos, "-%02x", ( unsigned char)str[loop]);

        if(pos >= (sizeof(buff) - 8))
            {
            //# Show that string is incomplete
            buff[pos++] = ' ';
            buff[pos++] = '.';
            buff[pos++] = '.';
            buff[pos++] = '.';
            break;
            }
        }
    buff[pos] = '\0';
    return(buff);
}

//# -------------------------------------------------------------------------
// use it for testing only as it has a xx byte buffer limit
//# Use: mystr = bluepoint2_dump($str)

char    *bluepoint2_dump(const char *str, int len)

{
    int loop = 0, pos = 0;
    buff[0] = 0;  
    //memset(buff, sizeof(buff), 0);
    
    if(verbose)
        {
        printf("bluepoint2_dump str=%p len=%d ", str, len);
        }

    for (loop = 0; loop < len; loop++)
        {
        pos += sprintf(buff + pos, "%02x", ( unsigned char)str[loop]);

        if(pos >= (sizeof(buff) - 8))
            {
            //# Show that string is incomplete
            //printf("Overflow ...\n");
            buff[pos++] = ' ';
            buff[pos++] = '.';
            buff[pos++] = '.';
            buff[pos++] = '.';
            break;
            }
        }
    buff[pos] = '\0';
    return(buff);
}

//# -------------------------------------------------------------------------
// Use it for decoding the dump to cyphertext
//# Use: mystr = bluepoint2_undump($str, len)

char    *bluepoint2_undump(const char *str, int len)

{
    buff[0] = 0;  int loop = 0, pos = 0;
    unsigned int val = 0;

    if(verbose)
        {
        printf("bluepoint2_undump str=%p len=%d ", str, len);
        }
    memset(buff, 0, sizeof(buff));

    for (loop = 0; loop < len; loop+=2)
        {
        sscanf(str + loop, "%02x", &val);
        //printf("%02x ", val & 0xff);

        // Safety check for overflow
        if(pos >= (sizeof(buff) - 8))
            {
            break;
            }
        buff[pos++] = val & 0xff;
        }
    //printf("\n");

    return(buff);
}

#endif

//# -------------------------------------------------------------------------
// convert binary str to hex string
//# char    *bluepoint_tohex(char *str, int len, char *out, int *len)

char    *bluepoint2_tohex(char *str, int len, char *out, int *olen)

{
    int loop = 0, pos = 0;
    for (loop = 0; loop < len; loop++)
        {
        pos += sprintf(out + pos, "%02x", ( unsigned char) str[loop]);

        if(pos >= *olen - 4)
            break;
        }
    *olen = pos;
    return(out);
}

//# -------------------------------------------------------------------------
// convert hex string to binary str
//# char    *bluepoint_fromhex(char *str, int len, char *out, int *len)

char    *bluepoint2_fromhex(char *str, int len, char *out, int *olen)

{
    unsigned char *str2 = (unsigned char *)str;

    char chh[3]; chh[2] = 0;

    int loop = 0, pos = 0;
    for (loop = 0; loop < len; loop += 2)
        {
        long vv;

        chh[0] =  *(str + loop);
        chh[1] =  *(str + loop + 1);

        vv = strtol(chh, NULL, 16);

             if(pos > *olen - 3)
            break;

        out[pos++] =(char)vv;
        }

    // It aborted for just enough space to zero terminate
    out[pos] = 0;

    *olen = pos;
    return(out);
}









