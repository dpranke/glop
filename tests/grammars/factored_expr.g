grammar = expr '\n' end -> _1

expr    = expr '+' term -> [_1, '+', _3]
        | expr '-' term -> [_1, '-', _3]
        | term          -> _1

term    = term '*' factor -> [ _1, '*', _3 ]
        | term '/' factor -> [ _1, '/', _3 ]
        | factor          -> _1

factor  = '(' expr ')'    -> _2
        | atom            -> _1

atom    = {('0'..'9')+}   -> _1
        | {('a'..'z'|'A'..'Z')+}  -> _1
