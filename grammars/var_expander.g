grammar = chunk*:cs end         -> ''.join(cs),
chunk   = ~'$' anything:c       -> c
        | '$' (' '|':'|'$'):c   -> c
        | '$' '{' varname:v '}' -> scope[v]
        | '$' varname:v         -> scope[v],
varname = (letter|'_')+:ls      -> ''.join(ls),
