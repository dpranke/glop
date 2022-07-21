grammar = expr '\n' end       -> _1

expr    = {num} '*' expr -> [_1, '*', _3]
        | {num} '+' expr -> [_1, '+', _3]
        | {num} '-' expr -> [_1, '-', _3]
        | {num}          -> _1

num     = ('0'..'9')+
