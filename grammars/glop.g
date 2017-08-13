grammar     = (sp rule)*:vs sp end                 -> vs

sp          = ws*

ws          = ' ' | '\t' | eol | comment

eol         = '\r' | '\n' | '\r\n'

comment     = '//' (~eol anything)* eol

rule        = ident:i sp '=' sp choice:cs sp ','?  -> ['rule', i, cs]

ident       = id_start:hd id_continue*:tl          -> ''.join([hd] + tl)

id_start    = letter | '_'

id_continue = letter | '_' | digit

choice      = seq:s (sp '|' sp seq)*:ss            -> ['choice', [s] + ss]

seq         = expr:e (ws sp expr)*:es              -> ['seq', [e] + es]
            |                                      -> ['empty']

expr        = post_expr:e ':' ident:l              -> ['label', e, l]
            | post_expr

post_expr   = prim_expr:e post_op:op               -> ['post', e, op]
            | prim_expr

prim_expr   = lit
            | ident:i ~(sp '=')                    -> ['apply', i]
            | '->' sp py_expr:e                    -> ['action', e]
            | '~' prim_expr:e                      -> ['not', e]
            | '?(' sp py_expr:e sp ')'             -> ['pred', e]
            | '(' sp choice:e sp ')'               -> ['paren', e]

lit         = squote (~squote sqchar)*:cs squote   -> ['lit', join('', cs)]
            | dquote (~dquote dqchar)*:cs dquote   -> ['lit', join('', cs)]

sqchar      = bslash squote                        -> '\x5C\x27'
            | anything

dqchar      = bslash dquote                        -> '\x5C\x22'
            | anything

bslash      = '\x5C'

squote      = '\x27'

dquote      = '\x22'

py_expr     = py_qual:e1 sp '+' sp py_expr:e2      -> ['py_plus', e1, e2]
            | py_qual

py_qual     = py_prim:e (py_post_op)+:ps           -> ['py_qual', e, ps]
            | py_prim

py_post_op  = '[' sp py_expr:e sp ']'              -> ['py_getitem', e]
            | '(' sp py_exprs:es sp ')'            -> ['py_call', es]
            | '.' ident:i                          -> ['py_getattr', i]

py_prim     = ident:i                              -> ['py_var', i]
            | digits:ds                            -> ['py_num', ds]
            | '0x' hexdigits:hs                    -> ['py_num', '0x' + hs]
            | lit:l                                -> ['py_lit', l[1]]
            | '(' sp py_expr:e sp ')'              -> ['py_paren', e]
            | '[' sp py_exprs:es sp ']'            -> ['py_arr', es]

digits      = digit+:ds                            -> join('', ds)

hexdigits   = hexdigit+:hs                         -> join('', hs)

hexdigit    = digit
            | 'a' | 'b' | 'c' | 'd' | 'e' | 'f'
            | 'A' | 'B' | 'C' | 'D' | 'E' | 'F'

py_exprs    = py_expr:e (sp ',' sp py_expr)*:es    -> [e] + es
            |                                      -> []

post_op     = ('?'|'*'|'+')
