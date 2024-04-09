#!/usr/bin/env python

# Global keyword configuration for pyedpro.

# ------------------------------------------------------------------------
# Add keywords to taste. Note, that we are cheating here, as the
# coloring sub system does not  parse the file, marely does a string
# compare. For example ' len(' is  unlikely to appear in any  context
# but in it's intended  place. Note that '=len(xx)' is not highlited but
# '= len(xx)' is. Add  strings that match your coding style or your
# language. It is feasible to have a set of keywords that cover
# multiple languages. (like # (hash) for bash, perl, python ...)
#
# Also note that coloring too much distracts from readability, so
# configure this conservatively.

# Keywords for Python coloring (this is in effect for .sh .c ... etc):

keywords =  ("def ", "import ", "from ", "for ", "while ", " len(",
            "return ", "range(", "if ", "if(", "elif ", "not ", " abs(",
            " any(", " all(", " min(", " max(",  " map(", " print(",
            " open(", " in ", " break ", "[]", "()", "{}", " pass",
            "pass ", " pass ", "True", " False", "True;", "False;",
            "true", "false", "global ", "else:", "continue", "None",
             "<tr ", "<tr>",  "</tr>", "<td ", "<td>", "</td>" )

# Keywords for class related enrties:
clwords =  ("class ", " self.", "try:", "except", "except:", "finally",
                "table ", "/table",)

# Keywords for summary extraction: (left side window)
pykeywords = ("class ", "def ", "TODO ")
basekeywords = ("(sub )|(SUB )")
Skeywords = "(^[_a-zA-Z].*:)|(\.bss)|(\.text)|(\.macro)"
pykeywords2 = "(class )|(def )|(TODO )|(__main__)"
pykeywords3 = "(_mac_)"
sumkeywords = "class ", "def ", "TODO "
htmlkeywords = "(\{ .* \})"

ckeywords =  "^[_a-zA-Z].*\(.*\)"
localkwords = "(int .*)|(char .*)|(for)|(while)|(if)|(return)"
localpywords = "(for )|(while )|(return )|(import )|(def )"

# Keywords for auto correct. This corrects strings as we type.
# Auto correct is case sensitive.
# As a 'C' programmer I kept typing "else" in python ... this feature
# corrects it to "else: "  (the trailing colon for python)
# It is contra indicatory to support bad habits, but for
# productivity .... all is forgiven.
#   Especially if one's next assignment is back to 'C'
#
# Make sure to_str is longer than from_str (if shorter ... why correct?)
# Ctrl-m to toggle autocorrect (default: off)

# Syntax: from_str, to_str ....

auto_corr_table = \
                [   ( "else",   "else: "                    ),
                    ( "whi",    "while "                    ),
                    ( "Tr",     "True "                     ),
                    ( "Fa",     "False "                    ),
                    ( "bre",    "break"                     ),
                    ( "short",   "sh "                      ),

            # One can do unconventional things here:

            ( "Fn",     "def funcname():  "                 ),
            ( "If",     "if val: action else:  action2 "    ),

            # No control chars, text only
            #( "Bad",     "if val: \n "    ),
        ]


# These files are colored by default (add extension if needed)

color_files = (".py", ".c", ".cpp", ".sh", ".pl", ".h", ".hpp",
                    ".js", ".php", ".f", ".y", ".pc", ".asm",
                        ".inc", ".asm", ".bas", ".s", ".html", ".ino")

# These files are considered 'c' like (for basic syntax highlites)

c_like_exts = ( ".js",  ".c",  ".h",  ".php", ".ino", ".sh")


# EOF
