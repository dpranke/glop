grammar  = (empty_line* decl)*:ds empty_line* end      -> ds

decl     = build | rule | var | subninja | include
         | pool | default

build    = "build" ws paths:os ws? ':' ws name:rule
            explicit_deps:eds implicit_deps:ids order_only_deps:ods eol
            (ws var)*:vs                               -> ['build', os, rule,
                                                           eds, ids, ods, vs]

rule     = "rule" ws name:n eol (ws var)*:vs           -> ['rule', n, vs]

var      = name:n ws? '=' ws? value:v eol              -> ['var', n, v]

value    = (~eol (('$' '\n' ' '+ -> '')|anything))*:vs -> ''.join(vs)

subninja = "subninja" ws path:p                        -> ['subninja', p]

include  = "include" ws path:p                         -> ['include', p]

pool     = "pool" ws name:n eol (ws var)*:vars         -> ['pool', n, vars]

default  = "default" ws paths:ps eol                   -> ['default', ps]

paths    = path:hd (ws path)*:tl                       -> [hd] + tl

path     = (('$' ' ')|(~(' '|':'|'='|'|'|eol) anything))+:p -> ''.join(p)

name     = letter:hd (letter|digit|'_')*:tl            -> ''.join([hd] + tl)

explicit_deps = ws? paths:ps                           -> ps
         |                                             -> []

implicit_deps = ws? '|' ws? paths:ps                   -> ps
         |                                             -> []

order_only_deps = ws? "||" ws? paths:ps                -> ps
         |                                             -> []

empty_line = ws? (comment | '\n')

eol      = ws? (comment | '\n' | end)

ws       = (' '|('$' '\n'))+

comment  = '#' (~'\n' anything)* ('\n'|end)
