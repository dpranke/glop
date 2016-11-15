grammar    = (sp rule)*:vs sp end                   -> vs,

ws         = (' ' | '\t' | eol | comment),

eol        = ('\r' | '\n' | '\r\n'),

comment    = '//' (~eol anything)* eol,

sp         = ws*,

rule       = ident:i sp '=' sp choice:cs sp ','     -> ['rule', i, cs],

ident      = (letter|'_'):hd (letter|'_'|digit)*:tl -> ''.join([hd] + tl),

choice     = seq:s (sp '|' sp seq)*:ss              -> ['choice', [s] + ss],

seq        = expr:e (ws sp expr)*:es                -> ['seq', [e] + es]
           |                                        -> ['empty'],

expr       = post_expr:e ':' ident:l                -> ['label', e, l]
           | post_expr,

post_expr  = prim_expr:e post_op:op                 -> ['post', e, op]
           | prim_expr,

prim_expr  = lit
           | ident:i                                -> ['apply', i]
           | '->' sp py_expr:e                      -> ['action', e]
           | '~' prim_expr:e                        -> ['not', e]
           | '?(' sp py_expr:e sp ')'               -> ['pred', e]
           | '(' sp choice:e sp ')'                 -> ['paren', e],

// Only single-quoted strings are supported.

lit        = quote (~quote qchar)*:cs quote         -> ['lit', join('', cs)],

qchar      = '\\\''                                 -> '\''
           | '\\\\'                                 -> '\\'
           | anything,

quote      = '\'',

py_expr    = py_qual:e1 sp '+' sp py_expr:e2        -> ['py_plus', e1, e2]
           | py_qual,

py_qual    = py_prim:e (py_post_op)+:ps             -> ['py_qual', e, ps]
           | py_prim,

py_post_op = '[' sp py_expr:e sp ']'                -> ['py_getitem', e]
           | '(' sp py_exprs:es sp ')'              -> ['py_call', es]
           | '.' ident:i                            -> ['py_getattr', i],

py_prim    = ident:i                                -> ['py_var', i]
           | digit+:ds                              -> ['py_num',
                                                        atoi(join('', ds))]
           | lit:l                                  -> ['py_lit', l[1]]
           | '(' sp py_expr:e sp ')'                -> ['py_paren', e]
           | '[' sp py_exprs:es sp ']'              -> ['py_arr', es],

py_exprs   = py_expr:e (sp ',' sp py_expr)*:es      -> [e] + es
           |                                        -> [],

post_op    = ('?'|'*'|'+'),
