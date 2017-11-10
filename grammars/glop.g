grammar     = (sp rule)*:vs sp end                     -> vs

sp          = ws*

ws          = '\u0020' | '\u0009' | eol | comment

eol         = '\u000D' '\u000A' | '\u000D' | '\u000A'

comment     = '//' (~eol anything)* 
            | '/*' (~'*/' anything)* '*/'

rule        = ident:i sp '=' sp choice:cs sp ','?      -> ['rule', i, cs]

ident       = id_start:hd id_continue*:tl              -> cat([hd] + tl)

id_start    = 'a'..'z' | 'A'..'Z' | '_'

id_continue = id_start | digit

choice      = seq:s (sp '|' sp seq)*:ss                -> ['choice', [s] + ss]

seq         = expr:e (ws sp expr)*:es                  -> ['seq', [e] + es]
            |                                          -> ['empty']

expr        = post_expr:e ':' ident:l                  -> ['label', e, l]
            | post_expr

post_expr   = prim_expr:e post_op:op                   -> ['post', e, op]
            | prim_expr

post_op     = '?' | '*' | '+'

prim_expr   = lit:i sp '..' sp lit:j                   -> ['range', i, j]
            | lit:l                                    -> l
            | ident:i ~(sp '=')                        -> ['apply', i]
            | '->' sp ll_expr:e                        -> ['action', e]
            | '~' prim_expr:e                          -> ['not', e]
            | '?(' sp ll_expr:e sp ')'                 -> ['pred', e]
            | '(' sp choice:e sp ')'                   -> ['paren', e]

lit         = squote sqchar*:cs squote                 -> ['lit', cat(cs)]
            | dquote dqchar*:cs dquote                 -> ['lit', cat(cs)]

sqchar      = bslash esc_char:c                        -> c
            | ~squote anything:c                       -> c

dqchar      = bslash esc_char:c                        -> c
            | ~dquote anything:c                       -> c

bslash      = '\x5C'

squote      = '\x27'

dquote      = '\x22'

esc_char    = 'b'                                      -> '\u0008'
            | 'f'                                      -> '\u000C'
            | 'n'                                      -> '\u000A'
            | 'r'                                      -> '\u000D'
            | 't'                                      -> '\u0009'
            | 'v'                                      -> '\u000B'
            | squote                                   -> '\u0027'
            | dquote                                   -> '\u0022'
            | bslash                                   -> '\u005C'
            | hex_esc:c                                -> c
            | unicode_esc:c                            -> c

hex_esc     = 'x' hex:h1 hex:h2                        -> xtou(h1 + h2)

unicode_esc = 'u' hex:a hex:b hex:c hex:d              -> xtou(a + b + c + d)
            | 'U' hex:a hex:b hex:c hex:d
                  hex:e hex:f hex:g hex:h              -> xtou(a + b + c + d +
                                                               e + f + g + h)

ll_exprs    = ll_expr:e (sp ',' sp ll_expr)*:es        -> [e] + es
            |                                          -> []

ll_expr     = ll_qual:e1 sp '+' sp ll_expr:e2          -> ['ll_plus', e1, e2]
            | ll_qual

ll_qual     = ll_prim:e ll_post_op+:ps                 -> ['ll_qual', e, ps]
            | ll_prim

ll_post_op  = '[' sp ll_expr:e sp ']'                  -> ['ll_getitem', e]
            | '(' sp ll_exprs:es sp ')'                -> ['ll_call', es]
            | '.' ident:i                              -> ['ll_getattr', i]

ll_prim     = ident:i                                  -> ['ll_var', i]
            | digits:ds                                -> ['ll_num', ds]
            | '0x' hexdigits:hs                        -> ['ll_num', '0x' + hs]
            | lit:l                                    -> ['ll_lit', l[1]]
            | '(' sp ll_expr:e sp ')'                  -> ['ll_paren', e]
            | '[' sp ll_exprs:es sp ']'                -> ['ll_arr', es]

digits      = digit+:ds                                -> cat(ds)

hexdigits   = hex+:hs                                  -> cat(hs)

hex         = digit | 'a'..'f' | 'A'..'F'

digit       = '0'..'9'
