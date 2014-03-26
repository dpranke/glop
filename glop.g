grammar    = (sp rule)*:vs sp end                   -> vs ,

sp         = (' ' | '\n' | '\t' )* ,

rule       = ident:i sp '=' sp choice:cs sp ','     -> ['rule', i, cs] ,

ident      = (letter|'_'):hd (letter|'_'|digit)*:tl -> ''.join([hd] + tl) ,

choice     = seq:s sp ('|' sp seq)+:ss              -> ['choice', [s] + [ss]]
           | seq ,

seq        = expr:e (sp expr)+:es                   -> ['seq', [e] + [es]]
           | expr
           |                                        -> ['empty'] ,

expr       = post_expr:e ':' ident:i                -> ['label', e, l]
           | post_expr ,

post_expr  = prim_expr:e post_op                    -> ['post', e, op]
           | prim_expr ,

prim_expr  = lit
           | ident:i                                -> ['apply', i]
           | '->' sp py_expr:e                      -> ['action', e]
           | '~' prim_expr:e                        -> ['not', e]
           | '?(' py_expr:e ')'                     -> ['pred', e]
           | '(' sp choice_expr:e sp ')'            -> e ,

lit        = quote (~quote (('\\\'' -> '\'') | anything))+:cs quote
                                                    -> ['lit', ''.join(cs)] ,

quote      = '\'' ,

py_expr    = py_qual:e1 sp '+' py_expr:e            -> ['py_plus', e1, e2]
           | py_qual ,

py_qual    = py_prim:e (py_post_op)+:ps             -> ['py_qual', e, ps]
           | py_prim ,

py_post_op = '[' sp py_expr:e sp ']'                -> ['py_getitem', e]
           | '(' sp py_exprs:es sp ')'              -> ['py_call', es]
           | '.' ident:i                            -> ['py_getattr', i] ,

py_prim    = ident:i                                -> ['py_var', i]
           | digit+:ds                              -> ['py_num',
                                                        int(''.join(ds))]
           | literal:l                              -> ['py_lit', l[1]]
           | '(' sp py_expr:e sp ')'                -> e
           | '[' sp py_exprs:es sp ']'              -> ['py_arr', [es]] ,

py_exprs   = py_expr:e ( sp ',' sp py_expr)*:es     -> [e] + es
           |                                        -> [] ,

post_op    = '?' | '*' | '+' ,
