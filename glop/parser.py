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
        self._seq([self._grammar__s0_, self._sp_, self._end_,
                   self._grammar__s3_])
        self._pop('grammar')

    def _grammar__s0_(self):
        self._bind(self._grammar__s0_l_, 'vs')

    def _grammar__s0_l_(self):
        self._star(self._grammar__s0_l_p_)

    def _grammar__s0_l_p_(self):
        self._seq([self._sp_, self._rule_])

    def _grammar__s3_(self):
        self._succeed(self._get('vs'))

    def _sp_(self):
        self._star(self._ws_)

    def _ws_(self):
        self._choose([self._ws__c0_, self._ws__c1_, self._eol_, self._comment_])

    def _ws__c0_(self):
        self._expect(' ', 1)

    def _ws__c1_(self):
        self._expect('\t', 1)

    def _eol_(self):
        self._choose([self._eol__c0_, self._eol__c1_, self._eol__c2_])

    def _eol__c0_(self):
        self._seq([lambda : self._expect('\r', 1),
                   lambda : self._expect('\n', 1)])

    def _eol__c1_(self):
        self._expect('\r', 1)

    def _eol__c2_(self):
        self._expect('\n', 1)

    def _comment_(self):
        self._choose([self._comment__c0_, self._comment__c1_])

    def _comment__c0_(self):
        self._seq([lambda : self._expect('//', 2), self._comment__c0__s1_])

    def _comment__c0__s1_(self):
        self._star(self._comment__c0__s1_p_)

    def _comment__c0__s1_p_(self):
        self._seq([self._comment__c0__s1_p__s0_, self._anything_])

    def _comment__c0__s1_p__s0_(self):
        self._not(self._eol_)

    def _comment__c1_(self):
        self._seq([lambda : self._expect('/*', 2), self._comment__c1__s1_,
                   lambda : self._expect('*/', 2)])

    def _comment__c1__s1_(self):
        self._star(self._comment__c1__s1_p_)

    def _comment__c1__s1_p_(self):
        self._seq([self._comment__c1__s1_p__s0_, self._anything_])

    def _comment__c1__s1_p__s0_(self):
        self._not(lambda : self._expect('*/', 2))

    def _rule_(self):
        self._push('rule')
        self._seq([self._rule__s0_, self._sp_, lambda : self._expect('=', 1),
                   self._sp_, self._rule__s4_, self._sp_, self._rule__s6_,
                   self._rule__s7_])
        self._pop('rule')

    def _rule__s0_(self):
        self._bind(self._ident_, 'i')

    def _rule__s4_(self):
        self._bind(self._choice_, 'cs')

    def _rule__s6_(self):
        self._opt(lambda : self._expect(',', 1))

    def _rule__s7_(self):
        self._succeed(['rule', self._get('i'), self._get('cs')])

    def _ident_(self):
        self._push('ident')
        self._seq([self._ident__s0_, self._ident__s1_, self._ident__s2_])
        self._pop('ident')

    def _ident__s0_(self):
        self._bind(self._id_start_, 'hd')

    def _ident__s1_(self):
        self._bind(self._ident__s1_l_, 'tl')

    def _ident__s1_l_(self):
        self._star(self._id_continue_)

    def _ident__s2_(self):
        self._succeed(self._join('', [self._get('hd')] + self._get('tl')))

    def _id_start_(self):
        self._choose([self._letter_, self._id_start__c1_])

    def _id_start__c1_(self):
        self._expect('_', 1)

    def _id_continue_(self):
        self._choose([self._id_start_, self._digit_])

    def _choice_(self):
        self._push('choice')
        self._seq([self._choice__s0_, self._choice__s1_, self._choice__s2_])
        self._pop('choice')

    def _choice__s0_(self):
        self._bind(self._seq_, 's')

    def _choice__s1_(self):
        self._bind(self._choice__s1_l_, 'ss')

    def _choice__s1_l_(self):
        self._star(self._choice__s1_l_p_)

    def _choice__s1_l_p_(self):
        self._seq([self._sp_, lambda : self._expect('|', 1), self._sp_,
                   self._seq_])

    def _choice__s2_(self):
        self._succeed(['choice', [self._get('s')] + self._get('ss')])

    def _seq_(self):
        self._choose([self._seq__c0_, self._seq__c1_])

    def _seq__c0_(self):
        self._push('seq__c0')
        self._seq([self._seq__c0__s0_, self._seq__c0__s1_, self._seq__c0__s2_])
        self._pop('seq__c0')

    def _seq__c0__s0_(self):
        self._bind(self._expr_, 'e')

    def _seq__c0__s1_(self):
        self._bind(self._seq__c0__s1_l_, 'es')

    def _seq__c0__s1_l_(self):
        self._star(self._seq__c0__s1_l_p_)

    def _seq__c0__s1_l_p_(self):
        self._seq([self._ws_, self._sp_, self._expr_])

    def _seq__c0__s2_(self):
        self._succeed(['seq', [self._get('e')] + self._get('es')])

    def _seq__c1_(self):
        self._succeed(['empty'])

    def _expr_(self):
        self._choose([self._expr__c0_, self._post_expr_])

    def _expr__c0_(self):
        self._push('expr__c0')
        self._seq([self._expr__c0__s0_, lambda : self._expect(':', 1),
                   self._expr__c0__s2_, self._expr__c0__s3_])
        self._pop('expr__c0')

    def _expr__c0__s0_(self):
        self._bind(self._post_expr_, 'e')

    def _expr__c0__s2_(self):
        self._bind(self._ident_, 'l')

    def _expr__c0__s3_(self):
        self._succeed(['label', self._get('e'), self._get('l')])

    def _post_expr_(self):
        self._choose([self._post_expr__c0_, self._prim_expr_])

    def _post_expr__c0_(self):
        self._push('post_expr__c0')
        self._seq([self._post_expr__c0__s0_, self._post_expr__c0__s1_,
                   self._post_expr__c0__s2_])
        self._pop('post_expr__c0')

    def _post_expr__c0__s0_(self):
        self._bind(self._prim_expr_, 'e')

    def _post_expr__c0__s1_(self):
        self._bind(self._post_op_, 'op')

    def _post_expr__c0__s2_(self):
        self._succeed(['post', self._get('e'), self._get('op')])

    def _post_op_(self):
        self._choose([self._post_op__c0_, self._post_op__c1_,
                      self._post_op__c2_])

    def _post_op__c0_(self):
        self._expect('?', 1)

    def _post_op__c1_(self):
        self._expect('*', 1)

    def _post_op__c2_(self):
        self._expect('+', 1)

    def _prim_expr_(self):
        self._choose([self._prim_expr__c0_, self._prim_expr__c1_,
                      self._prim_expr__c2_, self._prim_expr__c3_,
                      self._prim_expr__c4_, self._prim_expr__c5_,
                      self._prim_expr__c6_])

    def _prim_expr__c0_(self):
        self._push('prim_expr__c0')
        self._seq([self._prim_expr__c0__s0_, self._sp_,
                   lambda : self._expect('..', 2), self._sp_,
                   self._prim_expr__c0__s4_, self._prim_expr__c0__s5_])
        self._pop('prim_expr__c0')

    def _prim_expr__c0__s0_(self):
        self._bind(self._lit_, 'i')

    def _prim_expr__c0__s4_(self):
        self._bind(self._lit_, 'j')

    def _prim_expr__c0__s5_(self):
        self._succeed(['range', self._get('i'), self._get('j')])

    def _prim_expr__c1_(self):
        self._push('prim_expr__c1')
        self._seq([self._prim_expr__c1__s0_, self._prim_expr__c1__s1_])
        self._pop('prim_expr__c1')

    def _prim_expr__c1__s0_(self):
        self._bind(self._lit_, 'l')

    def _prim_expr__c1__s1_(self):
        self._succeed(self._get('l'))

    def _prim_expr__c2_(self):
        self._push('prim_expr__c2')
        self._seq([self._prim_expr__c2__s0_, self._prim_expr__c2__s1_,
                   self._prim_expr__c2__s2_])
        self._pop('prim_expr__c2')

    def _prim_expr__c2__s0_(self):
        self._bind(self._ident_, 'i')

    def _prim_expr__c2__s1_(self):
        self._not(self._prim_expr__c2__s1_n_)

    def _prim_expr__c2__s1_n_(self):
        self._prim_expr__c2__s1_n_g_()

    def _prim_expr__c2__s1_n_g_(self):
        self._choose([self._prim_expr__c2__s1_n_g__c0_])

    def _prim_expr__c2__s1_n_g__c0_(self):
        self._seq([self._sp_, lambda : self._expect('=', 1)])

    def _prim_expr__c2__s2_(self):
        self._succeed(['apply', self._get('i')])

    def _prim_expr__c3_(self):
        self._push('prim_expr__c3')
        self._seq([lambda : self._expect('->', 2), self._sp_,
                   self._prim_expr__c3__s2_, self._prim_expr__c3__s3_])
        self._pop('prim_expr__c3')

    def _prim_expr__c3__s2_(self):
        self._bind(self._ll_expr_, 'e')

    def _prim_expr__c3__s3_(self):
        self._succeed(['action', self._get('e')])

    def _prim_expr__c4_(self):
        self._push('prim_expr__c4')
        self._seq([lambda : self._expect('~', 1), self._prim_expr__c4__s1_,
                   self._prim_expr__c4__s2_])
        self._pop('prim_expr__c4')

    def _prim_expr__c4__s1_(self):
        self._bind(self._prim_expr_, 'e')

    def _prim_expr__c4__s2_(self):
        self._succeed(['not', self._get('e')])

    def _prim_expr__c5_(self):
        self._push('prim_expr__c5')
        self._seq([lambda : self._expect('?(', 2), self._sp_,
                   self._prim_expr__c5__s2_, self._sp_,
                   lambda : self._expect(')', 1), self._prim_expr__c5__s5_])
        self._pop('prim_expr__c5')

    def _prim_expr__c5__s2_(self):
        self._bind(self._ll_expr_, 'e')

    def _prim_expr__c5__s5_(self):
        self._succeed(['pred', self._get('e')])

    def _prim_expr__c6_(self):
        self._push('prim_expr__c6')
        self._seq([lambda : self._expect('(', 1), self._sp_,
                   self._prim_expr__c6__s2_, self._sp_,
                   lambda : self._expect(')', 1), self._prim_expr__c6__s5_])
        self._pop('prim_expr__c6')

    def _prim_expr__c6__s2_(self):
        self._bind(self._choice_, 'e')

    def _prim_expr__c6__s5_(self):
        self._succeed(['paren', self._get('e')])

    def _lit_(self):
        self._choose([self._lit__c0_, self._lit__c1_])

    def _lit__c0_(self):
        self._push('lit__c0')
        self._seq([self._squote_, self._lit__c0__s1_, self._squote_,
                   self._lit__c0__s3_])
        self._pop('lit__c0')

    def _lit__c0__s1_(self):
        self._bind(self._lit__c0__s1_l_, 'cs')

    def _lit__c0__s1_l_(self):
        self._star(self._sqchar_)

    def _lit__c0__s3_(self):
        self._succeed(['lit', self._join('', self._get('cs'))])

    def _lit__c1_(self):
        self._push('lit__c1')
        self._seq([self._dquote_, self._lit__c1__s1_, self._dquote_,
                   self._lit__c1__s3_])
        self._pop('lit__c1')

    def _lit__c1__s1_(self):
        self._bind(self._lit__c1__s1_l_, 'cs')

    def _lit__c1__s1_l_(self):
        self._star(self._dqchar_)

    def _lit__c1__s3_(self):
        self._succeed(['lit', self._join('', self._get('cs'))])

    def _sqchar_(self):
        self._choose([self._sqchar__c0_, self._sqchar__c1_])

    def _sqchar__c0_(self):
        self._push('sqchar__c0')
        self._seq([self._bslash_, self._sqchar__c0__s1_, self._sqchar__c0__s2_])
        self._pop('sqchar__c0')

    def _sqchar__c0__s1_(self):
        self._bind(self._esc_char_, 'c')

    def _sqchar__c0__s2_(self):
        self._succeed(self._get('c'))

    def _sqchar__c1_(self):
        self._push('sqchar__c1')
        self._seq([self._sqchar__c1__s0_, self._sqchar__c1__s1_,
                   self._sqchar__c1__s2_])
        self._pop('sqchar__c1')

    def _sqchar__c1__s0_(self):
        self._not(self._squote_)

    def _sqchar__c1__s1_(self):
        self._bind(self._anything_, 'c')

    def _sqchar__c1__s2_(self):
        self._succeed(self._get('c'))

    def _dqchar_(self):
        self._choose([self._dqchar__c0_, self._dqchar__c1_])

    def _dqchar__c0_(self):
        self._push('dqchar__c0')
        self._seq([self._bslash_, self._dqchar__c0__s1_, self._dqchar__c0__s2_])
        self._pop('dqchar__c0')

    def _dqchar__c0__s1_(self):
        self._bind(self._esc_char_, 'c')

    def _dqchar__c0__s2_(self):
        self._succeed(self._get('c'))

    def _dqchar__c1_(self):
        self._push('dqchar__c1')
        self._seq([self._dqchar__c1__s0_, self._dqchar__c1__s1_,
                   self._dqchar__c1__s2_])
        self._pop('dqchar__c1')

    def _dqchar__c1__s0_(self):
        self._not(self._dquote_)

    def _dqchar__c1__s1_(self):
        self._bind(self._anything_, 'c')

    def _dqchar__c1__s2_(self):
        self._succeed(self._get('c'))

    def _bslash_(self):
        self._expect('\\', 1)

    def _squote_(self):
        self._expect("'", 1)

    def _dquote_(self):
        self._expect('"', 1)

    def _esc_char_(self):
        self._choose([self._esc_char__c0_, self._esc_char__c1_,
                      self._esc_char__c2_, self._esc_char__c3_,
                      self._esc_char__c4_, self._esc_char__c5_,
                      self._esc_char__c6_, self._esc_char__c7_,
                      self._esc_char__c8_, self._esc_char__c9_,
                      self._esc_char__c10_])

    def _esc_char__c0_(self):
        self._seq([lambda : self._expect('b', 1), self._esc_char__c0__s1_])

    def _esc_char__c0__s1_(self):
        self._succeed('\b')

    def _esc_char__c1_(self):
        self._seq([lambda : self._expect('f', 1), self._esc_char__c1__s1_])

    def _esc_char__c10_(self):
        self._push('esc_char__c10')
        self._seq([self._esc_char__c10__s0_, self._esc_char__c10__s1_])
        self._pop('esc_char__c10')

    def _esc_char__c10__s0_(self):
        self._bind(self._unicode_esc_, 'c')

    def _esc_char__c10__s1_(self):
        self._succeed(self._get('c'))

    def _esc_char__c1__s1_(self):
        self._succeed('\f')

    def _esc_char__c2_(self):
        self._seq([lambda : self._expect('n', 1), self._esc_char__c2__s1_])

    def _esc_char__c2__s1_(self):
        self._succeed('\n')

    def _esc_char__c3_(self):
        self._seq([lambda : self._expect('r', 1), self._esc_char__c3__s1_])

    def _esc_char__c3__s1_(self):
        self._succeed('\r')

    def _esc_char__c4_(self):
        self._seq([lambda : self._expect('t', 1), self._esc_char__c4__s1_])

    def _esc_char__c4__s1_(self):
        self._succeed('\t')

    def _esc_char__c5_(self):
        self._seq([lambda : self._expect('v', 1), self._esc_char__c5__s1_])

    def _esc_char__c5__s1_(self):
        self._succeed('\v')

    def _esc_char__c6_(self):
        self._seq([self._squote_, self._esc_char__c6__s1_])

    def _esc_char__c6__s1_(self):
        self._succeed("'")

    def _esc_char__c7_(self):
        self._seq([self._dquote_, self._esc_char__c7__s1_])

    def _esc_char__c7__s1_(self):
        self._succeed('"')

    def _esc_char__c8_(self):
        self._seq([self._bslash_, self._esc_char__c8__s1_])

    def _esc_char__c8__s1_(self):
        self._succeed('\\')

    def _esc_char__c9_(self):
        self._push('esc_char__c9')
        self._seq([self._esc_char__c9__s0_, self._esc_char__c9__s1_])
        self._pop('esc_char__c9')

    def _esc_char__c9__s0_(self):
        self._bind(self._hex_esc_, 'c')

    def _esc_char__c9__s1_(self):
        self._succeed(self._get('c'))

    def _hex_esc_(self):
        self._push('hex_esc')
        self._seq([lambda : self._expect('x', 1), self._hex_esc__s1_,
                   self._hex_esc__s2_, self._hex_esc__s3_])
        self._pop('hex_esc')

    def _hex_esc__s1_(self):
        self._bind(self._hex_, 'h1')

    def _hex_esc__s2_(self):
        self._bind(self._hex_, 'h2')

    def _hex_esc__s3_(self):
        self._succeed(self._xtou(self._get('h1') + self._get('h2')))

    def _unicode_esc_(self):
        self._choose([self._unicode_esc__c0_, self._unicode_esc__c1_])

    def _unicode_esc__c0_(self):
        self._push('unicode_esc__c0')
        self._seq([lambda : self._expect('u', 1), self._unicode_esc__c0__s1_,
                   self._unicode_esc__c0__s2_, self._unicode_esc__c0__s3_,
                   self._unicode_esc__c0__s4_, self._unicode_esc__c0__s5_])
        self._pop('unicode_esc__c0')

    def _unicode_esc__c0__s1_(self):
        self._bind(self._hex_, 'a')

    def _unicode_esc__c0__s2_(self):
        self._bind(self._hex_, 'b')

    def _unicode_esc__c0__s3_(self):
        self._bind(self._hex_, 'c')

    def _unicode_esc__c0__s4_(self):
        self._bind(self._hex_, 'd')

    def _unicode_esc__c0__s5_(self):
        self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d')))

    def _unicode_esc__c1_(self):
        self._push('unicode_esc__c1')
        self._seq([lambda : self._expect('U', 1), self._unicode_esc__c1__s1_,
                   self._unicode_esc__c1__s2_, self._unicode_esc__c1__s3_,
                   self._unicode_esc__c1__s4_, self._unicode_esc__c1__s5_,
                   self._unicode_esc__c1__s6_, self._unicode_esc__c1__s7_,
                   self._unicode_esc__c1__s8_, self._unicode_esc__c1__s9_])
        self._pop('unicode_esc__c1')

    def _unicode_esc__c1__s1_(self):
        self._bind(self._hex_, 'a')

    def _unicode_esc__c1__s2_(self):
        self._bind(self._hex_, 'b')

    def _unicode_esc__c1__s3_(self):
        self._bind(self._hex_, 'c')

    def _unicode_esc__c1__s4_(self):
        self._bind(self._hex_, 'd')

    def _unicode_esc__c1__s5_(self):
        self._bind(self._hex_, 'e')

    def _unicode_esc__c1__s6_(self):
        self._bind(self._hex_, 'f')

    def _unicode_esc__c1__s7_(self):
        self._bind(self._hex_, 'g')

    def _unicode_esc__c1__s8_(self):
        self._bind(self._hex_, 'h')

    def _unicode_esc__c1__s9_(self):
        self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d') + self._get('e') + self._get('f') + self._get('g') + self._get('h')))

    def _ll_exprs_(self):
        self._choose([self._ll_exprs__c0_, self._ll_exprs__c1_])

    def _ll_exprs__c0_(self):
        self._push('ll_exprs__c0')
        self._seq([self._ll_exprs__c0__s0_, self._ll_exprs__c0__s1_,
                   self._ll_exprs__c0__s2_])
        self._pop('ll_exprs__c0')

    def _ll_exprs__c0__s0_(self):
        self._bind(self._ll_expr_, 'e')

    def _ll_exprs__c0__s1_(self):
        self._bind(self._ll_exprs__c0__s1_l_, 'es')

    def _ll_exprs__c0__s1_l_(self):
        self._star(self._ll_exprs__c0__s1_l_p_)

    def _ll_exprs__c0__s1_l_p_(self):
        self._seq([self._sp_, lambda : self._expect(',', 1), self._sp_,
                   self._ll_expr_])

    def _ll_exprs__c0__s2_(self):
        self._succeed([self._get('e')] + self._get('es'))

    def _ll_exprs__c1_(self):
        self._succeed([])

    def _ll_expr_(self):
        self._choose([self._ll_expr__c0_, self._ll_qual_])

    def _ll_expr__c0_(self):
        self._push('ll_expr__c0')
        self._seq([self._ll_expr__c0__s0_, self._sp_,
                   lambda : self._expect('+', 1), self._sp_,
                   self._ll_expr__c0__s4_, self._ll_expr__c0__s5_])
        self._pop('ll_expr__c0')

    def _ll_expr__c0__s0_(self):
        self._bind(self._ll_qual_, 'e1')

    def _ll_expr__c0__s4_(self):
        self._bind(self._ll_expr_, 'e2')

    def _ll_expr__c0__s5_(self):
        self._succeed(['ll_plus', self._get('e1'), self._get('e2')])

    def _ll_qual_(self):
        self._choose([self._ll_qual__c0_, self._ll_prim_])

    def _ll_qual__c0_(self):
        self._push('ll_qual__c0')
        self._seq([self._ll_qual__c0__s0_, self._ll_qual__c0__s1_,
                   self._ll_qual__c0__s2_])
        self._pop('ll_qual__c0')

    def _ll_qual__c0__s0_(self):
        self._bind(self._ll_prim_, 'e')

    def _ll_qual__c0__s1_(self):
        self._bind(self._ll_qual__c0__s1_l_, 'ps')

    def _ll_qual__c0__s1_l_(self):
        self._plus(self._ll_post_op_)

    def _ll_qual__c0__s2_(self):
        self._succeed(['ll_qual', self._get('e'), self._get('ps')])

    def _ll_post_op_(self):
        self._choose([self._ll_post_op__c0_, self._ll_post_op__c1_,
                      self._ll_post_op__c2_])

    def _ll_post_op__c0_(self):
        self._push('ll_post_op__c0')
        self._seq([lambda : self._expect('[', 1), self._sp_,
                   self._ll_post_op__c0__s2_, self._sp_,
                   lambda : self._expect(']', 1), self._ll_post_op__c0__s5_])
        self._pop('ll_post_op__c0')

    def _ll_post_op__c0__s2_(self):
        self._bind(self._ll_expr_, 'e')

    def _ll_post_op__c0__s5_(self):
        self._succeed(['ll_getitem', self._get('e')])

    def _ll_post_op__c1_(self):
        self._push('ll_post_op__c1')
        self._seq([lambda : self._expect('(', 1), self._sp_,
                   self._ll_post_op__c1__s2_, self._sp_,
                   lambda : self._expect(')', 1), self._ll_post_op__c1__s5_])
        self._pop('ll_post_op__c1')

    def _ll_post_op__c1__s2_(self):
        self._bind(self._ll_exprs_, 'es')

    def _ll_post_op__c1__s5_(self):
        self._succeed(['ll_call', self._get('es')])

    def _ll_post_op__c2_(self):
        self._push('ll_post_op__c2')
        self._seq([lambda : self._expect('.', 1), self._ll_post_op__c2__s1_,
                   self._ll_post_op__c2__s2_])
        self._pop('ll_post_op__c2')

    def _ll_post_op__c2__s1_(self):
        self._bind(self._ident_, 'i')

    def _ll_post_op__c2__s2_(self):
        self._succeed(['ll_getattr', self._get('i')])

    def _ll_prim_(self):
        self._choose([self._ll_prim__c0_, self._ll_prim__c1_,
                      self._ll_prim__c2_, self._ll_prim__c3_,
                      self._ll_prim__c4_, self._ll_prim__c5_])

    def _ll_prim__c0_(self):
        self._push('ll_prim__c0')
        self._seq([self._ll_prim__c0__s0_, self._ll_prim__c0__s1_])
        self._pop('ll_prim__c0')

    def _ll_prim__c0__s0_(self):
        self._bind(self._ident_, 'i')

    def _ll_prim__c0__s1_(self):
        self._succeed(['ll_var', self._get('i')])

    def _ll_prim__c1_(self):
        self._push('ll_prim__c1')
        self._seq([self._ll_prim__c1__s0_, self._ll_prim__c1__s1_])
        self._pop('ll_prim__c1')

    def _ll_prim__c1__s0_(self):
        self._bind(self._digits_, 'ds')

    def _ll_prim__c1__s1_(self):
        self._succeed(['ll_num', self._get('ds')])

    def _ll_prim__c2_(self):
        self._push('ll_prim__c2')
        self._seq([lambda : self._expect('0x', 2), self._ll_prim__c2__s1_,
                   self._ll_prim__c2__s2_])
        self._pop('ll_prim__c2')

    def _ll_prim__c2__s1_(self):
        self._bind(self._hexdigits_, 'hs')

    def _ll_prim__c2__s2_(self):
        self._succeed(['ll_num', '0x' + self._get('hs')])

    def _ll_prim__c3_(self):
        self._push('ll_prim__c3')
        self._seq([self._ll_prim__c3__s0_, self._ll_prim__c3__s1_])
        self._pop('ll_prim__c3')

    def _ll_prim__c3__s0_(self):
        self._bind(self._lit_, 'l')

    def _ll_prim__c3__s1_(self):
        self._succeed(['ll_lit', self._get('l')[1]])

    def _ll_prim__c4_(self):
        self._push('ll_prim__c4')
        self._seq([lambda : self._expect('(', 1), self._sp_,
                   self._ll_prim__c4__s2_, self._sp_,
                   lambda : self._expect(')', 1), self._ll_prim__c4__s5_])
        self._pop('ll_prim__c4')

    def _ll_prim__c4__s2_(self):
        self._bind(self._ll_expr_, 'e')

    def _ll_prim__c4__s5_(self):
        self._succeed(['ll_paren', self._get('e')])

    def _ll_prim__c5_(self):
        self._push('ll_prim__c5')
        self._seq([lambda : self._expect('[', 1), self._sp_,
                   self._ll_prim__c5__s2_, self._sp_,
                   lambda : self._expect(']', 1), self._ll_prim__c5__s5_])
        self._pop('ll_prim__c5')

    def _ll_prim__c5__s2_(self):
        self._bind(self._ll_exprs_, 'es')

    def _ll_prim__c5__s5_(self):
        self._succeed(['ll_arr', self._get('es')])

    def _digits_(self):
        self._push('digits')
        self._seq([self._digits__s0_, self._digits__s1_])
        self._pop('digits')

    def _digits__s0_(self):
        self._bind(self._digits__s0_l_, 'ds')

    def _digits__s0_l_(self):
        self._plus(self._digit_)

    def _digits__s1_(self):
        self._succeed(self._join('', self._get('ds')))

    def _hexdigits_(self):
        self._push('hexdigits')
        self._seq([self._hexdigits__s0_, self._hexdigits__s1_])
        self._pop('hexdigits')

    def _hexdigits__s0_(self):
        self._bind(self._hexdigits__s0_l_, 'hs')

    def _hexdigits__s0_l_(self):
        self._plus(self._hex_)

    def _hexdigits__s1_(self):
        self._succeed(self._join('', self._get('hs')))

    def _hex_(self):
        self._choose([self._digit_, self._hex__c1_, self._hex__c2_])

    def _hex__c1_(self):
        self._range('a', 'f')

    def _hex__c2_(self):
        self._range('A', 'F')

    def _hex_esc_(self):
        self._push('hex_esc')
        self._seq([lambda : self._expect('x', 1), self._hex_esc__s1_,
                   self._hex_esc__s2_, self._hex_esc__s3_])
        self._pop('hex_esc')

    def _hex_esc__s1_(self):
        self._bind(self._hex_, 'h1')

    def _hex_esc__s2_(self):
        self._bind(self._hex_, 'h2')

    def _hex_esc__s3_(self):
        self._succeed(self._xtou(self._get('h1') + self._get('h2')))

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

    def _expect(self, expr, l):
        p = self.pos
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self._succeed(expr, self.pos + l)
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
        return u'%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        for i in range(self.errpos):
            if self.msg[i] == u'\n':
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
