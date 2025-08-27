%{

FN   [\~_a-zA-Z]
FNN  [\~_a-zA-Z0-9]

%%

\\\n                 {
                     if(config.testpreflex)
                         { printf("[BS EOL] '%s", yytext); fflush(stdout); }
                     // Ignore
                     }

 //test lexer

%}

// test