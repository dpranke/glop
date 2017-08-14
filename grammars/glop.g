grammar     = (sp rule)*:vs sp end                -> vs

sp          = ws*

ws          = ' '
            | '\t'
            | eol
            | comment

eol         = '\r'
            | '\n'
            | '\r\n'

comment     = '//' (~eol anything)* eol

rule        = ident:i sp '=' sp choice:cs sp ','? -> ['rule', i, cs]

ident       = id_start:hd id_continue*:tl         -> ''.join([hd] + tl)

id_start    = letter
            | '_'

id_continue = letter
            | '_'
            | digit

choice      = seq:s (sp '|' sp seq)*:ss           -> ['choice', [s] + ss]

seq         = expr:e (ws sp expr)*:es             -> ['seq', [e] + es]
            |                                     -> ['empty']

expr        = post_expr:e ':' ident:l             -> ['label', e, l]
            | post_expr

post_expr   = prim_expr:e post_op:op              -> ['post', e, op]
            | prim_expr

post_op     = '?'
            | '*'
            | '+'

prim_expr   = lit
            | ident:i ~(sp '=')                   -> ['apply', i]
            | '->' sp ll_expr:e                   -> ['action', e]
            | '~' prim_expr:e                     -> ['not', e]
            | '?(' sp py_expr:e sp ')'            -> ['pred', e]
            | '(' sp choice:e sp ')'              -> ['paren', e]

lit         = squote (~squote sqchar)*:cs squote  -> ['lit', join('', cs)]
            | dquote (~dquote dqchar)*:cs dquote  -> ['lit', join('', cs)]

sqchar      = bslash squote                       -> '\x5C\x27'
            | bslash bslash                       -> '\x5C\x5C'
            | anything

dqchar      = bslash dquote                       -> '\x5C\x22'
            | bslash bslash                       -> '\x5C\x5C'
            | anything

bslash      = '\x5C'

squote      = '\x27'

dquote      = '\x22'

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

digits      = digit+:ds                           -> join('', ds)

hexdigits   = hexdigit+:hs                        -> join('', hs)

hexdigit    = digit
            | 'a'
            | 'b'
            | 'c'
            | 'd'
            | 'e'
            | 'f'
            | 'A'
            | 'B'
            | 'C'
            | 'D'
            | 'E'
            | 'F'
