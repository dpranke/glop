grammar = expr '\n' end  -> _1

expr    = expr '*' {num} -> [_1, '*', _3]
        | expr '+' {num} -> [_1, '+', _3]
        | expr '-' {num} -> [_1, '-', _3]
        | {num}          -> _1

num     = ('0'..'9')+
