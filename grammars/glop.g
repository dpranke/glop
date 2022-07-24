grammar     = (sp rule)* sp end                     -> ['rules', _1]

sp          = ws*

ws          = '\x20' | '\x09' | eol | comment

eol         = '\x0D\x0A' | '\x0D' | '\x0A'

comment     = '//' (~eol anything)*
            | '/*' (~'*/' anything)* '*/'

rule        = ident sp '=' sp choice sp ','?        -> ['rule', _1, _5]

ident       = {id_start id_continue*}

id_start    = 'a'..'z' | 'A'..'Z' | '_'

id_continue = id_start | digit

choice      = seq (sp '|' sp seq)*                  -> ['choice', [_1] + _2]

seq         = expr (ws sp expr)*                    -> ['seq', [_1] + _2]
            |                                       -> ['empty']

expr        = post_expr ':' ident                   -> ['label', _1, _3]
            | post_expr

post_expr   = prim_expr post_op                     -> [_2, _1]
            | prim_expr                             -> _1

post_op     = '?'                                   -> 'opt'
            | '*'                                   -> 'star'
            | '+'                                   -> 'plus'

prim_expr   = lit sp '..' sp lit                    -> ['range', _1, _5]
            | lit                                   -> _1
            | ident ~(sp '=')                       -> ['apply', _1]
            | '(' sp choice sp ')'                  -> ['paren', _3]
            | '~' prim_expr                         -> ['not', _2]
            | '->' sp ll_expr                       -> ['action', _3]
            | '{}'                                  -> ['pos']
            | '{' sp choice sp '}'                  -> ['capture', _3]
            | '={' sp ll_expr sp '}'                -> ['eq', _3]
            | '?{' sp ll_expr sp '}'                -> ['pred', _3]

lit         = squote sqchar* squote                 -> ['lit', cat(_2)]
            | dquote dqchar* dquote                 -> ['lit', cat(_2)]

sqchar      = bslash esc_char                       -> _2
            | ~squote anything                      -> _2

dqchar      = bslash esc_char                       -> _2
            | ~dquote anything                      -> _2

bslash      = '\x5C'

squote      = '\x27'

dquote      = '\x22'

esc_char    = 'b'                                   -> '\x08'
            | 'd'                                   -> '\\d'
            | 'f'                                   -> '\x0C'
            | 'n'                                   -> '\x0A'
            | 'r'                                   -> '\x0D'
            | 's'                                   -> '\\s'
            | 't'                                   -> '\x09'
            | 'v'                                   -> '\x0B'
            | 'w'                                   -> '\\w'
            | squote                                -> '\x27'
            | dquote                                -> '\x22'
            | bslash                                -> '\x5C'
            | hex_esc                               -> _1
            | unicode_esc                           -> _1
            | 'p{' unicode_cat '}'                  -> '\\p{' + _2 + '}'

hex_esc     = 'x' {hex hex}                         -> xtou(_2)

unicode_esc = 'u' {hex hex hex hex}                 -> xtou(_2)
            | 'U' {hex hex hex hex hex hex hex hex} -> xtou(_2)

unicode_cat = 'L' | 'Ll' | 'Lu' | 'Lt' |
              'Nd'

ll_exprs    = ll_expr (sp ',' sp ll_expr)*          -> [_1] + _2
            |                                       -> []

ll_expr     = ll_qual sp '+' sp ll_expr             -> ['ll_plus', _1, _5]
            | ll_qual

ll_qual     = ll_prim ll_post_op+                   -> ['ll_qual', _1, _2]
            | ll_prim

ll_post_op  = '[' sp ll_expr sp ']'                 -> ['ll_getitem', _3]
            | '(' sp ll_exprs sp ')'                -> ['ll_call', _3]

ll_prim     = ident                                 -> ['ll_var', _1]
            | '0x' hex+                             -> ['ll_hex', cat(_2)]
            | digit+                                -> ['ll_dec', cat(_1)]
            | lit                                   -> ['ll_str', _1[1]]
            | '(' sp ll_expr sp ')'                 -> ['ll_paren', _3]
            | '[' sp ll_exprs sp ']'                -> ['ll_arr', _3]

hex         = digit | 'a'..'f' | 'A'..'F'

digit       = '0'..'9'
