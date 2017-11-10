grammar     = (sp rule)*:vs sp end                -> vs

sp          = ws*

ws          = '\x20' | '\x09' | eol | comment

eol         = '\x0D' '\x0A' | '\x0D' | '\x0A'

comment     = '//' (~eol anything)* 
            | '/*' (~'*/' anything)* '*/'

rule        = ident:i sp '=' sp choice:cs sp ','? -> ['rule', i, cs]

ident       = id_start:hd id_continue*:tl         -> cat([hd] + tl)

id_start    = 'a'..'z' | 'A'..'Z' | '_'

id_continue = id_start | digit

choice      = seq:s (sp '|' sp seq)*:ss           -> ['choice', [s] + ss]

seq         = expr:e (ws sp expr)*:es             -> ['seq', [e] + es]
            |                                     -> ['empty']

expr        = post_expr:e ':' ident:l             -> ['label', e, l]
            | post_expr

post_expr   = prim_expr:e post_op:op              -> ['post', e, op]
            | prim_expr

post_op     = '?' | '*' | '+'

prim_expr   = lit:i sp '..' sp lit:j              -> ['range', i, j]
            | lit:l                               -> l
            | ident:i ~(sp '=')                   -> ['apply', i]
            | '->' sp ll_expr:e                   -> ['action', e]
            | '~' prim_expr:e                     -> ['not', e]
            | '?(' sp ll_expr:e sp ')'            -> ['pred', e]
            | '(' sp choice:e sp ')'              -> ['paren', e]

lit         = squote sqchar*:cs squote            -> ['lit', cat(cs)]
            | dquote dqchar*:cs dquote            -> ['lit', cat(cs)]

sqchar      = bslash esc_char:c                   -> c
            | ~squote anything:c                  -> c

dqchar      = bslash esc_char:c                   -> c
            | ~dquote anything:c                  -> c

bslash      = '\x5C'

squote      = '\x27'

dquote      = '\x22'

esc_char    = 'b'                                 -> '\x08'
            | 'f'                                 -> '\x0C'
            | 'n'                                 -> '\x0A'
            | 'r'                                 -> '\x0D'
            | 't'                                 -> '\x09'
            | 'v'                                 -> '\x0B'
            | squote                              -> '\x27'
            | dquote                              -> '\x22'
            | bslash                              -> '\x5C'
            | hex_esc:c                           -> c
            | unicode_esc:c                       -> c

hex_esc     = 'x' hex:h1 hex:h2                   -> xtou(h1 + h2)

unicode_esc = 'u' hex:h1 hex:h2 hex:h3 hex:h4     -> xtou(h1 + h2 + h3 + h4)
            | 'U' hex:h1 hex:h2 hex:h3 hex:h4
                  hex:h5 hex:h6 hex:h7 hex:h8     -> xtou(h1 + h2 + h3 + h4 +
                                                          h5 + h6 + h7 + h8)

ll_exprs    = ll_expr:e (sp ',' sp ll_expr)*:es   -> [e] + es
            |                                     -> []

ll_expr     = ll_qual:e1 sp '+' sp ll_expr:e2     -> ['ll_plus', e1, e2]
            | ll_qual

ll_qual     = ll_prim:e ll_post_op+:ps            -> ['ll_qual', e, ps]
            | ll_prim

ll_post_op  = '[' sp ll_expr:e sp ']'             -> ['ll_getitem', e]
            | '(' sp ll_exprs:es sp ')'           -> ['ll_call', es]
            | '.' ident:i                         -> ['ll_getattr', i]

ll_prim     = ident:i                             -> ['ll_var', i]
            | digits:ds                           -> ['ll_num', ds]
            | '0x' hexdigits:hs                   -> ['ll_num', '0x' + hs]
            | lit:l                               -> ['ll_lit', l[1]]
            | '(' sp ll_expr:e sp ')'             -> ['ll_paren', e]
            | '[' sp ll_exprs:es sp ']'           -> ['ll_arr', es]

digits      = digit+:ds                           -> cat(ds)

hexdigits   = hex+:hs                             -> cat(hs)

hex         = digit | 'a'..'f' | 'A'..'F'

digit       = '0'..'9'
