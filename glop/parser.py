# pylint: disable=line-too-long

import sys


if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr
    range = xrange
    str = unicode


class Parser(object):
    def __init__(self, msg, fname):
        self.msg = str(msg)
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0
        self._scopes = []

    def parse(self):
        self._grammar_()
        if self.failed:
            return None, self._err_str(), self.errpos
        return self.val, None, self.pos

    def _grammar_(self):
        self._push('grammar')
        self._seq([lambda: self._bind(self._grammar__s0_l_, 'vs'), self._sp_,
                   self._end_, lambda: self._succeed(self._get('vs'))])
        self._pop('grammar')

    def _grammar__s0_l_(self):
        self._star(lambda: self._seq([self._sp_, self._rule_]))

    def _sp_(self):
        self._star(self._ws_)

    def _ws_(self):
        self._choose([self._ws__c0_, self._ws__c1_, self._eol_, self._comment_])

    def _ws__c0_(self):
        self._ch(' ')

    def _ws__c1_(self):
        self._ch('\t')

    def _eol_(self):
        self._choose([self._eol__c0_, self._eol__c1_, self._eol__c2_])

    def _eol__c0_(self):
        self._seq([lambda: self._ch('\r'), lambda: self._ch('\n')])

    def _eol__c1_(self):
        self._ch('\r')

    def _eol__c2_(self):
        self._ch('\n')

    def _comment_(self):
        self._choose([self._comment__c0_, self._comment__c1_])

    def _comment__c0_(self):
        self._seq([lambda: self._str('//', 2),
                   lambda: self._star(self._comment__c0__s1_p_)])

    def _comment__c0__s1_p_(self):
        self._seq([lambda: self._not(self._eol_), self._anything_])

    def _comment__c1_(self):
        self._seq([lambda: self._str('/*', 2), self._comment__c1__s1_,
                   lambda: self._str('*/', 2)])

    def _comment__c1__s1_(self):
        self._star(lambda: self._seq([self._comment__c1__s1_p__s0_, self._anything_]))

    def _comment__c1__s1_p__s0_(self):
        self._not(lambda: self._str('*/', 2))

    def _rule_(self):
        self._push('rule')
        self._seq([lambda: self._bind(self._ident_, 'i'), self._sp_,
                   lambda: self._ch('='), self._sp_,
                   lambda: self._bind(self._choice_, 'cs'), self._sp_,
                   self._rule__s6_,
                   lambda: self._succeed(['rule', self._get('i'), self._get('cs')])])
        self._pop('rule')

    def _rule__s6_(self):
        self._opt(lambda: self._ch(','))

    def _ident_(self):
        self._push('ident')
        self._seq([lambda: self._bind(self._id_start_, 'hd'), self._ident__s1_,
                   lambda: self._succeed(self._join('', [self._get('hd')] + self._get('tl')))])
        self._pop('ident')

    def _ident__s1_(self):
        self._bind(lambda: self._star(self._id_continue_), 'tl')

    def _id_start_(self):
        self._choose([self._letter_, self._id_start__c1_])

    def _id_start__c1_(self):
        self._ch('_')

    def _id_continue_(self):
        self._choose([self._id_start_, self._digit_])

    def _choice_(self):
        self._push('choice')
        self._seq([lambda: self._bind(self._seq_, 's'), self._choice__s1_,
                   lambda: self._succeed(['choice', [self._get('s')] + self._get('ss')])])
        self._pop('choice')

    def _choice__s1_(self):
        self._bind(lambda: self._star(self._choice__s1_l_p_), 'ss')

    def _choice__s1_l_p_(self):
        self._seq([self._sp_, lambda: self._ch('|'), self._sp_, self._seq_])

    def _seq_(self):
        self._choose([self._seq__c0_, self._seq__c1_])

    def _seq__c0_(self):
        self._push('seq__c0')
        self._seq([lambda: self._bind(self._expr_, 'e'),
                   lambda: self._bind(self._seq__c0__s1_l_, 'es'),
                   lambda: self._succeed(['seq', [self._get('e')] + self._get('es')])])
        self._pop('seq__c0')

    def _seq__c0__s1_l_(self):
        self._star(lambda: self._seq([self._ws_, self._sp_, self._expr_]))

    def _seq__c1_(self):
        self._succeed(['empty'])

    def _expr_(self):
        self._choose([self._expr__c0_, self._post_expr_])

    def _expr__c0_(self):
        self._push('expr__c0')
        self._seq([lambda: self._bind(self._post_expr_, 'e'),
                   lambda: self._ch(':'), lambda: self._bind(self._ident_, 'l'),
                   lambda: self._succeed(['label', self._get('e'), self._get('l')])])
        self._pop('expr__c0')

    def _post_expr_(self):
        self._choose([self._post_expr__c0_, self._prim_expr_])

    def _post_expr__c0_(self):
        self._push('post_expr__c0')
        self._seq([lambda: self._bind(self._prim_expr_, 'e'),
                   lambda: self._bind(self._post_op_, 'op'),
                   lambda: self._succeed(['post', self._get('e'), self._get('op')])])
        self._pop('post_expr__c0')

    def _post_op_(self):
        self._choose([self._post_op__c0_, self._post_op__c1_,
                      self._post_op__c2_])

    def _post_op__c0_(self):
        self._ch('?')

    def _post_op__c1_(self):
        self._ch('*')

    def _post_op__c2_(self):
        self._ch('+')

    def _prim_expr_(self):
        self._choose([self._prim_expr__c0_, self._prim_expr__c1_,
                      self._prim_expr__c2_, self._prim_expr__c3_,
                      self._prim_expr__c4_, self._prim_expr__c5_,
                      self._prim_expr__c6_])

    def _prim_expr__c0_(self):
        self._push('prim_expr__c0')
        self._seq([lambda: self._bind(self._lit_, 'i'), self._sp_,
                   lambda: self._str('..', 2), self._sp_,
                   lambda: self._bind(self._lit_, 'j'),
                   lambda: self._succeed(['range', self._get('i'), self._get('j')])])
        self._pop('prim_expr__c0')

    def _prim_expr__c1_(self):
        self._push('prim_expr__c1')
        self._seq([lambda: self._bind(self._lit_, 'l'),
                   lambda: self._succeed(self._get('l'))])
        self._pop('prim_expr__c1')

    def _prim_expr__c2_(self):
        self._push('prim_expr__c2')
        self._seq([lambda: self._bind(self._ident_, 'i'),
                   lambda: self._not(self._prim_expr__c2__s1_n_),
                   lambda: self._succeed(['apply', self._get('i')])])
        self._pop('prim_expr__c2')

    def _prim_expr__c2__s1_n_(self):
        (lambda: self._choose([self._prim_expr__c2__s1_n_g__c0_]))()

    def _prim_expr__c2__s1_n_g__c0_(self):
        self._seq([self._sp_, lambda: self._ch('=')])

    def _prim_expr__c3_(self):
        self._push('prim_expr__c3')
        self._seq([lambda: self._str('->', 2), self._sp_,
                   lambda: self._bind(self._ll_expr_, 'e'),
                   lambda: self._succeed(['action', self._get('e')])])
        self._pop('prim_expr__c3')

    def _prim_expr__c4_(self):
        self._push('prim_expr__c4')
        self._seq([lambda: self._ch('~'),
                   lambda: self._bind(self._prim_expr_, 'e'),
                   lambda: self._succeed(['not', self._get('e')])])
        self._pop('prim_expr__c4')

    def _prim_expr__c5_(self):
        self._push('prim_expr__c5')
        self._seq([lambda: self._str('?(', 2), self._sp_,
                   lambda: self._bind(self._ll_expr_, 'e'), self._sp_,
                   lambda: self._ch(')'),
                   lambda: self._succeed(['pred', self._get('e')])])
        self._pop('prim_expr__c5')

    def _prim_expr__c6_(self):
        self._push('prim_expr__c6')
        self._seq([lambda: self._ch('('), self._sp_,
                   lambda: self._bind(self._choice_, 'e'), self._sp_,
                   lambda: self._ch(')'),
                   lambda: self._succeed(['paren', self._get('e')])])
        self._pop('prim_expr__c6')

    def _lit_(self):
        self._choose([self._lit__c0_, self._lit__c1_])

    def _lit__c0_(self):
        self._push('lit__c0')
        self._seq([self._squote_, self._lit__c0__s1_, self._squote_,
                   lambda: self._succeed(['lit', self._join('', self._get('cs'))])])
        self._pop('lit__c0')

    def _lit__c0__s1_(self):
        self._bind(lambda: self._star(self._sqchar_), 'cs')

    def _lit__c1_(self):
        self._push('lit__c1')
        self._seq([self._dquote_, self._lit__c1__s1_, self._dquote_,
                   lambda: self._succeed(['lit', self._join('', self._get('cs'))])])
        self._pop('lit__c1')

    def _lit__c1__s1_(self):
        self._bind(lambda: self._star(self._dqchar_), 'cs')

    def _sqchar_(self):
        self._choose([self._sqchar__c0_, self._sqchar__c1_])

    def _sqchar__c0_(self):
        self._push('sqchar__c0')
        self._seq([self._bslash_, lambda: self._bind(self._esc_char_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('sqchar__c0')

    def _sqchar__c1_(self):
        self._push('sqchar__c1')
        self._seq([lambda: self._not(self._squote_),
                   lambda: self._bind(self._anything_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('sqchar__c1')

    def _dqchar_(self):
        self._choose([self._dqchar__c0_, self._dqchar__c1_])

    def _dqchar__c0_(self):
        self._push('dqchar__c0')
        self._seq([self._bslash_, lambda: self._bind(self._esc_char_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('dqchar__c0')

    def _dqchar__c1_(self):
        self._push('dqchar__c1')
        self._seq([lambda: self._not(self._dquote_),
                   lambda: self._bind(self._anything_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('dqchar__c1')

    def _bslash_(self):
        self._ch('\\')

    def _squote_(self):
        self._ch("'")

    def _dquote_(self):
        self._ch('"')

    def _esc_char_(self):
        self._choose([self._esc_char__c0_, self._esc_char__c1_,
                      self._esc_char__c2_, self._esc_char__c3_,
                      self._esc_char__c4_, self._esc_char__c5_,
                      self._esc_char__c6_, self._esc_char__c7_,
                      self._esc_char__c8_, self._esc_char__c9_,
                      self._esc_char__c10_])

    def _esc_char__c0_(self):
        self._seq([lambda: self._ch('b'), lambda: self._succeed('\b')])

    def _esc_char__c1_(self):
        self._seq([lambda: self._ch('f'), lambda: self._succeed('\f')])

    def _esc_char__c10_(self):
        self._push('esc_char__c10')
        self._seq([lambda: self._bind(self._unicode_esc_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('esc_char__c10')

    def _esc_char__c2_(self):
        self._seq([lambda: self._ch('n'), lambda: self._succeed('\n')])

    def _esc_char__c3_(self):
        self._seq([lambda: self._ch('r'), lambda: self._succeed('\r')])

    def _esc_char__c4_(self):
        self._seq([lambda: self._ch('t'), lambda: self._succeed('\t')])

    def _esc_char__c5_(self):
        self._seq([lambda: self._ch('v'), lambda: self._succeed('\v')])

    def _esc_char__c6_(self):
        self._seq([self._squote_, lambda: self._succeed("'")])

    def _esc_char__c7_(self):
        self._seq([self._dquote_, lambda: self._succeed('"')])

    def _esc_char__c8_(self):
        self._seq([self._bslash_, lambda: self._succeed('\\')])

    def _esc_char__c9_(self):
        self._push('esc_char__c9')
        self._seq([lambda: self._bind(self._hex_esc_, 'c'),
                   lambda: self._succeed(self._get('c'))])
        self._pop('esc_char__c9')

    def _hex_esc_(self):
        self._push('hex_esc')
        self._seq([lambda: self._ch('x'), lambda: self._bind(self._hex_, 'h1'),
                   lambda: self._bind(self._hex_, 'h2'),
                   lambda: self._succeed(self._xtou(self._get('h1') + self._get('h2')))])
        self._pop('hex_esc')

    def _unicode_esc_(self):
        self._choose([self._unicode_esc__c0_, self._unicode_esc__c1_])

    def _unicode_esc__c0_(self):
        self._push('unicode_esc__c0')
        self._seq([lambda: self._ch('u'), lambda: self._bind(self._hex_, 'a'),
                   lambda: self._bind(self._hex_, 'b'),
                   lambda: self._bind(self._hex_, 'c'),
                   lambda: self._bind(self._hex_, 'd'),
                   lambda: self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d')))])
        self._pop('unicode_esc__c0')

    def _unicode_esc__c1_(self):
        self._push('unicode_esc__c1')
        self._seq([lambda: self._ch('U'), lambda: self._bind(self._hex_, 'a'),
                   lambda: self._bind(self._hex_, 'b'),
                   lambda: self._bind(self._hex_, 'c'),
                   lambda: self._bind(self._hex_, 'd'),
                   lambda: self._bind(self._hex_, 'e'),
                   lambda: self._bind(self._hex_, 'f'),
                   lambda: self._bind(self._hex_, 'g'),
                   lambda: self._bind(self._hex_, 'h'),
                   lambda: self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d') + self._get('e') + self._get('f') + self._get('g') + self._get('h')))])
        self._pop('unicode_esc__c1')

    def _ll_exprs_(self):
        self._choose([self._ll_exprs__c0_, self._ll_exprs__c1_])

    def _ll_exprs__c0_(self):
        self._push('ll_exprs__c0')
        self._seq([lambda: self._bind(self._ll_expr_, 'e'),
                   self._ll_exprs__c0__s1_,
                   lambda: self._succeed([self._get('e')] + self._get('es'))])
        self._pop('ll_exprs__c0')

    def _ll_exprs__c0__s1_(self):
        self._bind(lambda: self._star(self._ll_exprs__c0__s1_l_p_), 'es')

    def _ll_exprs__c0__s1_l_p_(self):
        self._seq([self._sp_, lambda: self._ch(','), self._sp_, self._ll_expr_])

    def _ll_exprs__c1_(self):
        self._succeed([])

    def _ll_expr_(self):
        self._choose([self._ll_expr__c0_, self._ll_qual_])

    def _ll_expr__c0_(self):
        self._push('ll_expr__c0')
        self._seq([lambda: self._bind(self._ll_qual_, 'e1'), self._sp_,
                   lambda: self._ch('+'), self._sp_,
                   lambda: self._bind(self._ll_expr_, 'e2'),
                   lambda: self._succeed(['ll_plus', self._get('e1'), self._get('e2')])])
        self._pop('ll_expr__c0')

    def _ll_qual_(self):
        self._choose([self._ll_qual__c0_, self._ll_prim_])

    def _ll_qual__c0_(self):
        self._push('ll_qual__c0')
        self._seq([lambda: self._bind(self._ll_prim_, 'e'),
                   self._ll_qual__c0__s1_,
                   lambda: self._succeed(['ll_qual', self._get('e'), self._get('ps')])])
        self._pop('ll_qual__c0')

    def _ll_qual__c0__s1_(self):
        self._bind(lambda: self._plus(self._ll_post_op_), 'ps')

    def _ll_post_op_(self):
        self._choose([self._ll_post_op__c0_, self._ll_post_op__c1_,
                      self._ll_post_op__c2_])

    def _ll_post_op__c0_(self):
        self._push('ll_post_op__c0')
        self._seq([lambda: self._ch('['), self._sp_,
                   lambda: self._bind(self._ll_expr_, 'e'), self._sp_,
                   lambda: self._ch(']'),
                   lambda: self._succeed(['ll_getitem', self._get('e')])])
        self._pop('ll_post_op__c0')

    def _ll_post_op__c1_(self):
        self._push('ll_post_op__c1')
        self._seq([lambda: self._ch('('), self._sp_,
                   lambda: self._bind(self._ll_exprs_, 'es'), self._sp_,
                   lambda: self._ch(')'),
                   lambda: self._succeed(['ll_call', self._get('es')])])
        self._pop('ll_post_op__c1')

    def _ll_post_op__c2_(self):
        self._push('ll_post_op__c2')
        self._seq([lambda: self._ch('.'), lambda: self._bind(self._ident_, 'i'),
                   lambda: self._succeed(['ll_getattr', self._get('i')])])
        self._pop('ll_post_op__c2')

    def _ll_prim_(self):
        self._choose([self._ll_prim__c0_, self._ll_prim__c1_,
                      self._ll_prim__c2_, self._ll_prim__c3_,
                      self._ll_prim__c4_, self._ll_prim__c5_])

    def _ll_prim__c0_(self):
        self._push('ll_prim__c0')
        self._seq([lambda: self._bind(self._ident_, 'i'),
                   lambda: self._succeed(['ll_var', self._get('i')])])
        self._pop('ll_prim__c0')

    def _ll_prim__c1_(self):
        self._push('ll_prim__c1')
        self._seq([lambda: self._bind(self._digits_, 'ds'),
                   lambda: self._succeed(['ll_num', self._get('ds')])])
        self._pop('ll_prim__c1')

    def _ll_prim__c2_(self):
        self._push('ll_prim__c2')
        self._seq([lambda: self._str('0x', 2),
                   lambda: self._bind(self._hexdigits_, 'hs'),
                   lambda: self._succeed(['ll_num', '0x' + self._get('hs')])])
        self._pop('ll_prim__c2')

    def _ll_prim__c3_(self):
        self._push('ll_prim__c3')
        self._seq([lambda: self._bind(self._lit_, 'l'),
                   lambda: self._succeed(['ll_lit', self._get('l')[1]])])
        self._pop('ll_prim__c3')

    def _ll_prim__c4_(self):
        self._push('ll_prim__c4')
        self._seq([lambda: self._ch('('), self._sp_,
                   lambda: self._bind(self._ll_expr_, 'e'), self._sp_,
                   lambda: self._ch(')'),
                   lambda: self._succeed(['ll_paren', self._get('e')])])
        self._pop('ll_prim__c4')

    def _ll_prim__c5_(self):
        self._push('ll_prim__c5')
        self._seq([lambda: self._ch('['), self._sp_,
                   lambda: self._bind(self._ll_exprs_, 'es'), self._sp_,
                   lambda: self._ch(']'),
                   lambda: self._succeed(['ll_arr', self._get('es')])])
        self._pop('ll_prim__c5')

    def _digits_(self):
        self._push('digits')
        self._seq([self._digits__s0_,
                   lambda: self._succeed(self._join('', self._get('ds')))])
        self._pop('digits')

    def _digits__s0_(self):
        self._bind(lambda: self._plus(self._digit_), 'ds')

    def _hexdigits_(self):
        self._push('hexdigits')
        self._seq([self._hexdigits__s0_,
                   lambda: self._succeed(self._join('', self._get('hs')))])
        self._pop('hexdigits')

    def _hexdigits__s0_(self):
        self._bind(lambda: self._plus(self._hex_), 'hs')

    def _hex_(self):
        self._choose([self._digit_, self._hex__c1_, self._hex__c2_])

    def _hex__c1_(self):
        self._range('a', 'f')

    def _hex__c2_(self):
        self._range('A', 'F')

    def _hex_esc_(self):
        self._push('hex_esc')
        self._seq([lambda: self._ch('x'), lambda: self._bind(self._hex_, 'h1'),
                   lambda: self._bind(self._hex_, 'h2'),
                   lambda: self._succeed(self._xtou(self._get('h1') + self._get('h2')))])
        self._pop('hex_esc')

    def _digit_(self):
        self._range('0', '9')

    def _anything_(self):
        if self.pos < self.end:
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()

    def _end_(self):
        if self.pos == self.end:
            self._succeed(None)
        else:
            self._fail()

    def _letter_(self):
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()

    def _join(self, s, vs):
        return s.join(vs)

    def _xtou(self, s):
        return chr(int(s, base=16))

    def _ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._succeed(ch, self.pos + 1)
        else:
            self._fail()

    def _str(self, s, l):
        p = self.pos
        if (p + l <= self.end) and self.msg[p:p + l] == s:
            self._succeed(s, self.pos + l)
        else:
            self._fail()

    def _range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._succeed(self.msg[p], self.pos + 1)
        else:
            self._fail()

    def _push(self, name):
        self._scopes.append((name, {}))

    def _pop(self, name):
        actual_name, _ = self._scopes.pop()
        assert name == actual_name

    def _get(self, var):
        return self._scopes[-1][1][var]

    def _set(self, var, val):
        self._scopes[-1][1][var] = val

    def _err_str(self):
        lineno, colno = self._err_offsets()
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = '"%s"' % self.msg[self.errpos]
        return '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        for i in range(self.errpos):
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        return lineno, colno

    def _succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos

    def _fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _rewind(self, newpos):
        self._succeed(None, newpos)

    def _bind(self, rule, var):
        rule()
        if not self.failed:
            self._set(var, self.val)

    def _not(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._succeed(None, p)
        else:
            self._rewind(p)
            self._fail()

    def _opt(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._succeed([], p)
        else:
            self._succeed([self.val])

    def _plus(self, rule):
        vs = []
        rule()
        vs.append(self.val)
        if self.failed:
            return
        self._star(rule, vs)

    def _star(self, rule, vs=None):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._rewind(p)
                break
            else:
                vs.append(self.val)
        self._succeed(vs)

    def _seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _choose(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._rewind(p)
        rules[-1]()
