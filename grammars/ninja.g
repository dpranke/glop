grammar    = (empty_line* decl)*:ds empty_line* end   -> ds

decl       = build | rule | var | subninja | include | pool | default

build      = 'build' ws paths:os imps:ios
             ws? ':' ws? name:n
             exps:es imps:is ords:ods eol vars:vs     -> ['build', os, ios,
                                                          n, es, is, ods, vs]

exps       = ws paths:ps                              -> ps
           |                                          -> []

imps       = ws? '|' ws? paths:ps                     -> ps
           |                                          -> []

ords       = ws? '||' ws? paths:ps                    -> ps
           |                                          -> []

rule       = 'rule' ws name:n eol (ws var)*:vs        -> ['rule', n, vs]

vars       = (ws var)*

var        = name:n ws? '=' ws? value:v eol           -> ['var', n, v]

value      = (~eol ((ws -> ' ') | anything))*:vs      -> cat(vs)

subninja   = 'subninja' ws path:p                     -> ['subninja', p]

include    = 'include' ws path:p                      -> ['include', p]

pool       = 'pool' ws name:n eol (ws var)*:vars      -> ['pool', n, vars]

default    = 'default' ws paths:ps eol                -> ['default', ps]

paths      = path:hd (ws path)*:tl                    -> [hd] + tl

path       = (esc |(~path_sep anything))+:ps          -> cat(ps)

esc        = '$ '                                     -> ' '
           | '$\n' ' '*                               -> ''
           | '$:'                                     -> ':'
           | '$' name:n                               -> '$' + n
           | '${' name:n '}'                          -> '${' + n + '}'
           | '$$'                                     -> '$'

name       = letter:hd (letter | digit | '_')*:tl     -> hd + cat(tl)

letter     = 'a'..'z' | 'A'..'Z'

digit      = '0'..'9'

path_sep   = ' ' | ':' | '|' | '\n'

empty_line = eol

eol        = ws? comment? '\n'

ws         = (' ' | '$\n')+

comment    = '#' (~'\n' anything)*
