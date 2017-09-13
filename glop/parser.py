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
        self.err = False
        self.errpos = 0
        self._scopes = []

    def parse(self):
        self._grammar_()
        if self._failed():
            return None, self._err_str(), self.errpos
        return self.val, None, self.pos

    def _grammar_(self):
        self._choose([self._grammar__c0_])

    def _grammar__c0_(self):
        self._push('grammar__c0')
        self._seq([self._grammar__c0__s0_, self._sp_, self._end_,
                   self._grammar__c0__s3_])
        self._pop('grammar__c0')

    def _grammar__c0__s0_(self):
        self._bind(self._grammar__c0__s0_l_, u'vs')

    def _grammar__c0__s0_l_(self):
        self._star(self._grammar__c0__s0_l_p_)

    def _grammar__c0__s0_l_p_(self):
        self._grammar__c0__s0_l_p_g_()

    def _grammar__c0__s0_l_p_g_(self):
        self._choose([self._grammar__c0__s0_l_p_g__c0_])

    def _grammar__c0__s0_l_p_g__c0_(self):
        self._seq([self._sp_, self._rule_])

    def _grammar__c0__s3_(self):
        self._succeed(self._get('vs'), self.pos)

    def _sp_(self):
        self._choose([self._sp__c0_])

    def _sp__c0_(self):
        self._seq([self._sp__c0__s0_])

    def _sp__c0__s0_(self):
        self._star(self._ws_)

    def _ws_(self):
        self._choose([self._ws__c0_, self._ws__c1_, self._ws__c2_,
                      self._ws__c3_])

    def _ws__c0_(self):
        self._seq([lambda : self._expect(u' ', 1)])

    def _ws__c1_(self):
        self._seq([lambda : self._expect(u'\t', 1)])

    def _ws__c2_(self):
        self._seq([self._eol_])

    def _ws__c3_(self):
        self._seq([self._comment_])

    def _eol_(self):
        self._choose([self._eol__c0_, self._eol__c1_, self._eol__c2_])

    def _eol__c0_(self):
        self._seq([lambda : self._expect(u'\r', 1),
                   lambda : self._expect(u'\n', 1)])

    def _eol__c1_(self):
        self._seq([lambda : self._expect(u'\r', 1)])

    def _eol__c2_(self):
        self._seq([lambda : self._expect(u'\n', 1)])

    def _comment_(self):
        self._choose([self._comment__c0_, self._comment__c1_])

    def _comment__c0_(self):
        self._seq([lambda : self._expect(u'//', 2), self._comment__c0__s1_])

    def _comment__c0__s1_(self):
        self._star(self._comment__c0__s1_p_)

    def _comment__c0__s1_p_(self):
        self._comment__c0__s1_p_g_()

    def _comment__c0__s1_p_g_(self):
        self._choose([self._comment__c0__s1_p_g__c0_])

    def _comment__c0__s1_p_g__c0_(self):
        self._seq([self._comment__c0__s1_p_g__c0__s0_, self._anything_])

    def _comment__c0__s1_p_g__c0__s0_(self):
        self._not(self._eol_)

    def _comment__c1_(self):
        self._seq([lambda : self._expect(u'/*', 2), self._comment__c1__s1_,
                   lambda : self._expect(u'*/', 2)])

    def _comment__c1__s1_(self):
        self._star(self._comment__c1__s1_p_)

    def _comment__c1__s1_p_(self):
        self._comment__c1__s1_p_g_()

    def _comment__c1__s1_p_g_(self):
        self._choose([self._comment__c1__s1_p_g__c0_])

    def _comment__c1__s1_p_g__c0_(self):
        self._seq([self._comment__c1__s1_p_g__c0__s0_, self._anything_])

    def _comment__c1__s1_p_g__c0__s0_(self):
        self._not(lambda : self._expect(u'*/', 2))

    def _rule_(self):
        self._choose([self._rule__c0_])

    def _rule__c0_(self):
        self._push('rule__c0')
        self._seq([self._rule__c0__s0_, self._sp_,
                   lambda : self._expect(u'=', 1), self._sp_,
                   self._rule__c0__s4_, self._sp_, self._rule__c0__s6_,
                   self._rule__c0__s7_])
        self._pop('rule__c0')

    def _rule__c0__s0_(self):
        self._bind(self._ident_, u'i')

    def _rule__c0__s4_(self):
        self._bind(self._choice_, u'cs')

    def _rule__c0__s6_(self):
        self._opt(lambda : self._expect(u',', 1))

    def _rule__c0__s7_(self):
        self._succeed([u'rule', self._get('i'), self._get('cs')], self.pos)

    def _ident_(self):
        self._choose([self._ident__c0_])

    def _ident__c0_(self):
        self._push('ident__c0')
        self._seq([self._ident__c0__s0_, self._ident__c0__s1_,
                   self._ident__c0__s2_])
        self._pop('ident__c0')

    def _ident__c0__s0_(self):
        self._bind(self._id_start_, u'hd')

    def _ident__c0__s1_(self):
        self._bind(self._ident__c0__s1_l_, u'tl')

    def _ident__c0__s1_l_(self):
        self._star(self._id_continue_)

    def _ident__c0__s2_(self):
        self._succeed(self._join(u'', [self._get('hd')] + self._get('tl')), self.pos)

    def _id_start_(self):
        self._choose([self._id_start__c0_, self._id_start__c1_])

    def _id_start__c0_(self):
        self._seq([self._letter_])

    def _id_start__c1_(self):
        self._seq([lambda : self._expect(u'_', 1)])

    def _id_continue_(self):
        self._choose([self._id_continue__c0_, self._id_continue__c1_])

    def _id_continue__c0_(self):
        self._seq([self._id_start_])

    def _id_continue__c1_(self):
        self._seq([self._digit_])

    def _choice_(self):
        self._choose([self._choice__c0_])

    def _choice__c0_(self):
        self._push('choice__c0')
        self._seq([self._choice__c0__s0_, self._choice__c0__s1_,
                   self._choice__c0__s2_])
        self._pop('choice__c0')

    def _choice__c0__s0_(self):
        self._bind(self._seq_, u's')

    def _choice__c0__s1_(self):
        self._bind(self._choice__c0__s1_l_, u'ss')

    def _choice__c0__s1_l_(self):
        self._star(self._choice__c0__s1_l_p_)

    def _choice__c0__s1_l_p_(self):
        self._choice__c0__s1_l_p_g_()

    def _choice__c0__s1_l_p_g_(self):
        self._choose([self._choice__c0__s1_l_p_g__c0_])

    def _choice__c0__s1_l_p_g__c0_(self):
        self._seq([self._sp_, lambda : self._expect(u'|', 1), self._sp_,
                   self._seq_])

    def _choice__c0__s2_(self):
        self._succeed([u'choice', [self._get('s')] + self._get('ss')], self.pos)

    def _seq_(self):
        self._choose([self._seq__c0_, self._seq__c1_])

    def _seq__c0_(self):
        self._push('seq__c0')
        self._seq([self._seq__c0__s0_, self._seq__c0__s1_, self._seq__c0__s2_])
        self._pop('seq__c0')

    def _seq__c0__s0_(self):
        self._bind(self._expr_, u'e')

    def _seq__c0__s1_(self):
        self._bind(self._seq__c0__s1_l_, u'es')

    def _seq__c0__s1_l_(self):
        self._star(self._seq__c0__s1_l_p_)

    def _seq__c0__s1_l_p_(self):
        self._seq__c0__s1_l_p_g_()

    def _seq__c0__s1_l_p_g_(self):
        self._choose([self._seq__c0__s1_l_p_g__c0_])

    def _seq__c0__s1_l_p_g__c0_(self):
        self._seq([self._ws_, self._sp_, self._expr_])

    def _seq__c0__s2_(self):
        self._succeed([u'seq', [self._get('e')] + self._get('es')], self.pos)

    def _seq__c1_(self):
        self._seq([self._seq__c1__s0_])

    def _seq__c1__s0_(self):
        self._succeed([u'empty'], self.pos)

    def _expr_(self):
        self._choose([self._expr__c0_, self._expr__c1_])

    def _expr__c0_(self):
        self._push('expr__c0')
        self._seq([self._expr__c0__s0_, lambda : self._expect(u':', 1),
                   self._expr__c0__s2_, self._expr__c0__s3_])
        self._pop('expr__c0')

    def _expr__c0__s0_(self):
        self._bind(self._post_expr_, u'e')

    def _expr__c0__s2_(self):
        self._bind(self._ident_, u'l')

    def _expr__c0__s3_(self):
        self._succeed([u'label', self._get('e'), self._get('l')], self.pos)

    def _expr__c1_(self):
        self._seq([self._post_expr_])

    def _post_expr_(self):
        self._choose([self._post_expr__c0_, self._post_expr__c1_])

    def _post_expr__c0_(self):
        self._push('post_expr__c0')
        self._seq([self._post_expr__c0__s0_, self._post_expr__c0__s1_,
                   self._post_expr__c0__s2_])
        self._pop('post_expr__c0')

    def _post_expr__c0__s0_(self):
        self._bind(self._prim_expr_, u'e')

    def _post_expr__c0__s1_(self):
        self._bind(self._post_op_, u'op')

    def _post_expr__c0__s2_(self):
        self._succeed([u'post', self._get('e'), self._get('op')], self.pos)

    def _post_expr__c1_(self):
        self._seq([self._prim_expr_])

    def _post_op_(self):
        self._choose([self._post_op__c0_, self._post_op__c1_,
                      self._post_op__c2_])

    def _post_op__c0_(self):
        self._seq([lambda : self._expect(u'?', 1)])

    def _post_op__c1_(self):
        self._seq([lambda : self._expect(u'*', 1)])

    def _post_op__c2_(self):
        self._seq([lambda : self._expect(u'+', 1)])

    def _prim_expr_(self):
        self._choose([self._prim_expr__c0_, self._prim_expr__c1_,
                      self._prim_expr__c2_, self._prim_expr__c3_,
                      self._prim_expr__c4_, self._prim_expr__c5_,
                      self._prim_expr__c6_])

    def _prim_expr__c0_(self):
        self._push('prim_expr__c0')
        self._seq([self._prim_expr__c0__s0_, self._sp_,
                   lambda : self._expect(u'..', 2), self._sp_,
                   self._prim_expr__c0__s4_, self._prim_expr__c0__s5_])
        self._pop('prim_expr__c0')

    def _prim_expr__c0__s0_(self):
        self._bind(self._lit_, u'i')

    def _prim_expr__c0__s4_(self):
        self._bind(self._lit_, u'j')

    def _prim_expr__c0__s5_(self):
        self._succeed([u'range', self._get('i'), self._get('j')], self.pos)

    def _prim_expr__c1_(self):
        self._push('prim_expr__c1')
        self._seq([self._prim_expr__c1__s0_, self._prim_expr__c1__s1_])
        self._pop('prim_expr__c1')

    def _prim_expr__c1__s0_(self):
        self._bind(self._lit_, u'l')

    def _prim_expr__c1__s1_(self):
        self._succeed(self._get('l'), self.pos)

    def _prim_expr__c2_(self):
        self._push('prim_expr__c2')
        self._seq([self._prim_expr__c2__s0_, self._prim_expr__c2__s1_,
                   self._prim_expr__c2__s2_])
        self._pop('prim_expr__c2')

    def _prim_expr__c2__s0_(self):
        self._bind(self._ident_, u'i')

    def _prim_expr__c2__s1_(self):
        self._not(self._prim_expr__c2__s1_n_)

    def _prim_expr__c2__s1_n_(self):
        self._prim_expr__c2__s1_n_g_()

    def _prim_expr__c2__s1_n_g_(self):
        self._choose([self._prim_expr__c2__s1_n_g__c0_])

    def _prim_expr__c2__s1_n_g__c0_(self):
        self._seq([self._sp_, lambda : self._expect(u'=', 1)])

    def _prim_expr__c2__s2_(self):
        self._succeed([u'apply', self._get('i')], self.pos)

    def _prim_expr__c3_(self):
        self._push('prim_expr__c3')
        self._seq([lambda : self._expect(u'->', 2), self._sp_,
                   self._prim_expr__c3__s2_, self._prim_expr__c3__s3_])
        self._pop('prim_expr__c3')

    def _prim_expr__c3__s2_(self):
        self._bind(self._ll_expr_, u'e')

    def _prim_expr__c3__s3_(self):
        self._succeed([u'action', self._get('e')], self.pos)

    def _prim_expr__c4_(self):
        self._push('prim_expr__c4')
        self._seq([lambda : self._expect(u'~', 1), self._prim_expr__c4__s1_,
                   self._prim_expr__c4__s2_])
        self._pop('prim_expr__c4')

    def _prim_expr__c4__s1_(self):
        self._bind(self._prim_expr_, u'e')

    def _prim_expr__c4__s2_(self):
        self._succeed([u'not', self._get('e')], self.pos)

    def _prim_expr__c5_(self):
        self._push('prim_expr__c5')
        self._seq([lambda : self._expect(u'?(', 2), self._sp_,
                   self._prim_expr__c5__s2_, self._sp_,
                   lambda : self._expect(u')', 1), self._prim_expr__c5__s5_])
        self._pop('prim_expr__c5')

    def _prim_expr__c5__s2_(self):
        self._bind(self._ll_expr_, u'e')

    def _prim_expr__c5__s5_(self):
        self._succeed([u'pred', self._get('e')], self.pos)

    def _prim_expr__c6_(self):
        self._push('prim_expr__c6')
        self._seq([lambda : self._expect(u'(', 1), self._sp_,
                   self._prim_expr__c6__s2_, self._sp_,
                   lambda : self._expect(u')', 1), self._prim_expr__c6__s5_])
        self._pop('prim_expr__c6')

    def _prim_expr__c6__s2_(self):
        self._bind(self._choice_, u'e')

    def _prim_expr__c6__s5_(self):
        self._succeed([u'paren', self._get('e')], self.pos)

    def _lit_(self):
        self._choose([self._lit__c0_, self._lit__c1_])

    def _lit__c0_(self):
        self._push('lit__c0')
        self._seq([self._squote_, self._lit__c0__s1_, self._squote_,
                   self._lit__c0__s3_])
        self._pop('lit__c0')

    def _lit__c0__s1_(self):
        self._bind(self._lit__c0__s1_l_, u'cs')

    def _lit__c0__s1_l_(self):
        self._star(self._sqchar_)

    def _lit__c0__s3_(self):
        self._succeed([u'lit', self._join(u'', self._get('cs'))], self.pos)

    def _lit__c1_(self):
        self._push('lit__c1')
        self._seq([self._dquote_, self._lit__c1__s1_, self._dquote_,
                   self._lit__c1__s3_])
        self._pop('lit__c1')

    def _lit__c1__s1_(self):
        self._bind(self._lit__c1__s1_l_, u'cs')

    def _lit__c1__s1_l_(self):
        self._star(self._dqchar_)

    def _lit__c1__s3_(self):
        self._succeed([u'lit', self._join(u'', self._get('cs'))], self.pos)

    def _sqchar_(self):
        self._choose([self._sqchar__c0_, self._sqchar__c1_])

    def _sqchar__c0_(self):
        self._push('sqchar__c0')
        self._seq([self._bslash_, self._sqchar__c0__s1_, self._sqchar__c0__s2_])
        self._pop('sqchar__c0')

    def _sqchar__c0__s1_(self):
        self._bind(self._esc_char_, u'c')

    def _sqchar__c0__s2_(self):
        self._succeed(self._get('c'), self.pos)

    def _sqchar__c1_(self):
        self._push('sqchar__c1')
        self._seq([self._sqchar__c1__s0_, self._sqchar__c1__s1_,
                   self._sqchar__c1__s2_])
        self._pop('sqchar__c1')

    def _sqchar__c1__s0_(self):
        self._not(self._squote_)

    def _sqchar__c1__s1_(self):
        self._bind(self._anything_, u'c')

    def _sqchar__c1__s2_(self):
        self._succeed(self._get('c'), self.pos)

    def _dqchar_(self):
        self._choose([self._dqchar__c0_, self._dqchar__c1_])

    def _dqchar__c0_(self):
        self._push('dqchar__c0')
        self._seq([self._bslash_, self._dqchar__c0__s1_, self._dqchar__c0__s2_])
        self._pop('dqchar__c0')

    def _dqchar__c0__s1_(self):
        self._bind(self._esc_char_, u'c')

    def _dqchar__c0__s2_(self):
        self._succeed(self._get('c'), self.pos)

    def _dqchar__c1_(self):
        self._push('dqchar__c1')
        self._seq([self._dqchar__c1__s0_, self._dqchar__c1__s1_,
                   self._dqchar__c1__s2_])
        self._pop('dqchar__c1')

    def _dqchar__c1__s0_(self):
        self._not(self._dquote_)

    def _dqchar__c1__s1_(self):
        self._bind(self._anything_, u'c')

    def _dqchar__c1__s2_(self):
        self._succeed(self._get('c'), self.pos)

    def _bslash_(self):
        self._choose([self._bslash__c0_])

    def _bslash__c0_(self):
        self._seq([lambda : self._expect(u'\\', 1)])

    def _squote_(self):
        self._choose([self._squote__c0_])

    def _squote__c0_(self):
        self._seq([lambda : self._expect(u"'", 1)])

    def _dquote_(self):
        self._choose([self._dquote__c0_])

    def _dquote__c0_(self):
        self._seq([lambda : self._expect(u'"', 1)])

    def _esc_char_(self):
        self._choose([self._esc_char__c0_, self._esc_char__c1_,
                      self._esc_char__c2_, self._esc_char__c3_,
                      self._esc_char__c4_, self._esc_char__c5_,
                      self._esc_char__c6_, self._esc_char__c7_,
                      self._esc_char__c8_, self._esc_char__c9_,
                      self._esc_char__c10_])

    def _esc_char__c0_(self):
        self._seq([lambda : self._expect(u'b', 1), self._esc_char__c0__s1_])

    def _esc_char__c0__s1_(self):
        self._succeed(u'\x08', self.pos)

    def _esc_char__c1_(self):
        self._seq([lambda : self._expect(u'f', 1), self._esc_char__c1__s1_])

    def _esc_char__c10_(self):
        self._push('esc_char__c10')
        self._seq([self._esc_char__c10__s0_, self._esc_char__c10__s1_])
        self._pop('esc_char__c10')

    def _esc_char__c10__s0_(self):
        self._bind(self._unicode_esc_, u'c')

    def _esc_char__c10__s1_(self):
        self._succeed(self._get('c'), self.pos)

    def _esc_char__c1__s1_(self):
        self._succeed(u'\x0c', self.pos)

    def _esc_char__c2_(self):
        self._seq([lambda : self._expect(u'n', 1), self._esc_char__c2__s1_])

    def _esc_char__c2__s1_(self):
        self._succeed(u'\n', self.pos)

    def _esc_char__c3_(self):
        self._seq([lambda : self._expect(u'r', 1), self._esc_char__c3__s1_])

    def _esc_char__c3__s1_(self):
        self._succeed(u'\r', self.pos)

    def _esc_char__c4_(self):
        self._seq([lambda : self._expect(u't', 1), self._esc_char__c4__s1_])

    def _esc_char__c4__s1_(self):
        self._succeed(u'\t', self.pos)

    def _esc_char__c5_(self):
        self._seq([lambda : self._expect(u'v', 1), self._esc_char__c5__s1_])

    def _esc_char__c5__s1_(self):
        self._succeed(u'\x0b', self.pos)

    def _esc_char__c6_(self):
        self._seq([self._squote_, self._esc_char__c6__s1_])

    def _esc_char__c6__s1_(self):
        self._succeed(u"'", self.pos)

    def _esc_char__c7_(self):
        self._seq([self._dquote_, self._esc_char__c7__s1_])

    def _esc_char__c7__s1_(self):
        self._succeed(u'"', self.pos)

    def _esc_char__c8_(self):
        self._seq([self._bslash_, self._esc_char__c8__s1_])

    def _esc_char__c8__s1_(self):
        self._succeed(u'\\', self.pos)

    def _esc_char__c9_(self):
        self._push('esc_char__c9')
        self._seq([self._esc_char__c9__s0_, self._esc_char__c9__s1_])
        self._pop('esc_char__c9')

    def _esc_char__c9__s0_(self):
        self._bind(self._hex_esc_, u'c')

    def _esc_char__c9__s1_(self):
        self._succeed(self._get('c'), self.pos)

    def _hex_esc_(self):
        self._choose([self._hex_esc__c0_])

    def _hex_esc__c0_(self):
        self._push('hex_esc__c0')
        self._seq([lambda : self._expect(u'x', 1), self._hex_esc__c0__s1_,
                   self._hex_esc__c0__s2_, self._hex_esc__c0__s3_])
        self._pop('hex_esc__c0')

    def _hex_esc__c0__s1_(self):
        self._bind(self._hex_, u'h1')

    def _hex_esc__c0__s2_(self):
        self._bind(self._hex_, u'h2')

    def _hex_esc__c0__s3_(self):
        self._succeed(self._xtou(self._get('h1') + self._get('h2')), self.pos)

    def _unicode_esc_(self):
        self._choose([self._unicode_esc__c0_, self._unicode_esc__c1_])

    def _unicode_esc__c0_(self):
        self._push('unicode_esc__c0')
        self._seq([lambda : self._expect(u'u', 1), self._unicode_esc__c0__s1_,
                   self._unicode_esc__c0__s2_, self._unicode_esc__c0__s3_,
                   self._unicode_esc__c0__s4_, self._unicode_esc__c0__s5_])
        self._pop('unicode_esc__c0')

    def _unicode_esc__c0__s1_(self):
        self._bind(self._hex_, u'a')

    def _unicode_esc__c0__s2_(self):
        self._bind(self._hex_, u'b')

    def _unicode_esc__c0__s3_(self):
        self._bind(self._hex_, u'c')

    def _unicode_esc__c0__s4_(self):
        self._bind(self._hex_, u'd')

    def _unicode_esc__c0__s5_(self):
        self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d')), self.pos)

    def _unicode_esc__c1_(self):
        self._push('unicode_esc__c1')
        self._seq([lambda : self._expect(u'U', 1), self._unicode_esc__c1__s1_,
                   self._unicode_esc__c1__s2_, self._unicode_esc__c1__s3_,
                   self._unicode_esc__c1__s4_, self._unicode_esc__c1__s5_,
                   self._unicode_esc__c1__s6_, self._unicode_esc__c1__s7_,
                   self._unicode_esc__c1__s8_, self._unicode_esc__c1__s9_])
        self._pop('unicode_esc__c1')

    def _unicode_esc__c1__s1_(self):
        self._bind(self._hex_, u'a')

    def _unicode_esc__c1__s2_(self):
        self._bind(self._hex_, u'b')

    def _unicode_esc__c1__s3_(self):
        self._bind(self._hex_, u'c')

    def _unicode_esc__c1__s4_(self):
        self._bind(self._hex_, u'd')

    def _unicode_esc__c1__s5_(self):
        self._bind(self._hex_, u'e')

    def _unicode_esc__c1__s6_(self):
        self._bind(self._hex_, u'f')

    def _unicode_esc__c1__s7_(self):
        self._bind(self._hex_, u'g')

    def _unicode_esc__c1__s8_(self):
        self._bind(self._hex_, u'h')

    def _unicode_esc__c1__s9_(self):
        self._succeed(self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d') + self._get('e') + self._get('f') + self._get('g') + self._get('h')), self.pos)

    def _ll_exprs_(self):
        self._choose([self._ll_exprs__c0_, self._ll_exprs__c1_])

    def _ll_exprs__c0_(self):
        self._push('ll_exprs__c0')
        self._seq([self._ll_exprs__c0__s0_, self._ll_exprs__c0__s1_,
                   self._ll_exprs__c0__s2_])
        self._pop('ll_exprs__c0')

    def _ll_exprs__c0__s0_(self):
        self._bind(self._ll_expr_, u'e')

    def _ll_exprs__c0__s1_(self):
        self._bind(self._ll_exprs__c0__s1_l_, u'es')

    def _ll_exprs__c0__s1_l_(self):
        self._star(self._ll_exprs__c0__s1_l_p_)

    def _ll_exprs__c0__s1_l_p_(self):
        self._ll_exprs__c0__s1_l_p_g_()

    def _ll_exprs__c0__s1_l_p_g_(self):
        self._choose([self._ll_exprs__c0__s1_l_p_g__c0_])

    def _ll_exprs__c0__s1_l_p_g__c0_(self):
        self._seq([self._sp_, lambda : self._expect(u',', 1), self._sp_,
                   self._ll_expr_])

    def _ll_exprs__c0__s2_(self):
        self._succeed([self._get('e')] + self._get('es'), self.pos)

    def _ll_exprs__c1_(self):
        self._seq([self._ll_exprs__c1__s0_])

    def _ll_exprs__c1__s0_(self):
        self._succeed([], self.pos)

    def _ll_expr_(self):
        self._choose([self._ll_expr__c0_, self._ll_expr__c1_])

    def _ll_expr__c0_(self):
        self._push('ll_expr__c0')
        self._seq([self._ll_expr__c0__s0_, self._sp_,
                   lambda : self._expect(u'+', 1), self._sp_,
                   self._ll_expr__c0__s4_, self._ll_expr__c0__s5_])
        self._pop('ll_expr__c0')

    def _ll_expr__c0__s0_(self):
        self._bind(self._ll_qual_, u'e1')

    def _ll_expr__c0__s4_(self):
        self._bind(self._ll_expr_, u'e2')

    def _ll_expr__c0__s5_(self):
        self._succeed([u'll_plus', self._get('e1'), self._get('e2')], self.pos)

    def _ll_expr__c1_(self):
        self._seq([self._ll_qual_])

    def _ll_qual_(self):
        self._choose([self._ll_qual__c0_, self._ll_qual__c1_])

    def _ll_qual__c0_(self):
        self._push('ll_qual__c0')
        self._seq([self._ll_qual__c0__s0_, self._ll_qual__c0__s1_,
                   self._ll_qual__c0__s2_])
        self._pop('ll_qual__c0')

    def _ll_qual__c0__s0_(self):
        self._bind(self._ll_prim_, u'e')

    def _ll_qual__c0__s1_(self):
        self._bind(self._ll_qual__c0__s1_l_, u'ps')

    def _ll_qual__c0__s1_l_(self):
        self._plus(self._ll_post_op_)

    def _ll_qual__c0__s2_(self):
        self._succeed([u'll_qual', self._get('e'), self._get('ps')], self.pos)

    def _ll_qual__c1_(self):
        self._seq([self._ll_prim_])

    def _ll_post_op_(self):
        self._choose([self._ll_post_op__c0_, self._ll_post_op__c1_,
                      self._ll_post_op__c2_])

    def _ll_post_op__c0_(self):
        self._push('ll_post_op__c0')
        self._seq([lambda : self._expect(u'[', 1), self._sp_,
                   self._ll_post_op__c0__s2_, self._sp_,
                   lambda : self._expect(u']', 1), self._ll_post_op__c0__s5_])
        self._pop('ll_post_op__c0')

    def _ll_post_op__c0__s2_(self):
        self._bind(self._ll_expr_, u'e')

    def _ll_post_op__c0__s5_(self):
        self._succeed([u'll_getitem', self._get('e')], self.pos)

    def _ll_post_op__c1_(self):
        self._push('ll_post_op__c1')
        self._seq([lambda : self._expect(u'(', 1), self._sp_,
                   self._ll_post_op__c1__s2_, self._sp_,
                   lambda : self._expect(u')', 1), self._ll_post_op__c1__s5_])
        self._pop('ll_post_op__c1')

    def _ll_post_op__c1__s2_(self):
        self._bind(self._ll_exprs_, u'es')

    def _ll_post_op__c1__s5_(self):
        self._succeed([u'll_call', self._get('es')], self.pos)

    def _ll_post_op__c2_(self):
        self._push('ll_post_op__c2')
        self._seq([lambda : self._expect(u'.', 1), self._ll_post_op__c2__s1_,
                   self._ll_post_op__c2__s2_])
        self._pop('ll_post_op__c2')

    def _ll_post_op__c2__s1_(self):
        self._bind(self._ident_, u'i')

    def _ll_post_op__c2__s2_(self):
        self._succeed([u'll_getattr', self._get('i')], self.pos)

    def _ll_prim_(self):
        self._choose([self._ll_prim__c0_, self._ll_prim__c1_,
                      self._ll_prim__c2_, self._ll_prim__c3_,
                      self._ll_prim__c4_, self._ll_prim__c5_])

    def _ll_prim__c0_(self):
        self._push('ll_prim__c0')
        self._seq([self._ll_prim__c0__s0_, self._ll_prim__c0__s1_])
        self._pop('ll_prim__c0')

    def _ll_prim__c0__s0_(self):
        self._bind(self._ident_, u'i')

    def _ll_prim__c0__s1_(self):
        self._succeed([u'll_var', self._get('i')], self.pos)

    def _ll_prim__c1_(self):
        self._push('ll_prim__c1')
        self._seq([self._ll_prim__c1__s0_, self._ll_prim__c1__s1_])
        self._pop('ll_prim__c1')

    def _ll_prim__c1__s0_(self):
        self._bind(self._digits_, u'ds')

    def _ll_prim__c1__s1_(self):
        self._succeed([u'll_num', self._get('ds')], self.pos)

    def _ll_prim__c2_(self):
        self._push('ll_prim__c2')
        self._seq([lambda : self._expect(u'0x', 2), self._ll_prim__c2__s1_,
                   self._ll_prim__c2__s2_])
        self._pop('ll_prim__c2')

    def _ll_prim__c2__s1_(self):
        self._bind(self._hexdigits_, u'hs')

    def _ll_prim__c2__s2_(self):
        self._succeed([u'll_num', u'0x' + self._get('hs')], self.pos)

    def _ll_prim__c3_(self):
        self._push('ll_prim__c3')
        self._seq([self._ll_prim__c3__s0_, self._ll_prim__c3__s1_])
        self._pop('ll_prim__c3')

    def _ll_prim__c3__s0_(self):
        self._bind(self._lit_, u'l')

    def _ll_prim__c3__s1_(self):
        self._succeed([u'll_lit', self._get('l')[1]], self.pos)

    def _ll_prim__c4_(self):
        self._push('ll_prim__c4')
        self._seq([lambda : self._expect(u'(', 1), self._sp_,
                   self._ll_prim__c4__s2_, self._sp_,
                   lambda : self._expect(u')', 1), self._ll_prim__c4__s5_])
        self._pop('ll_prim__c4')

    def _ll_prim__c4__s2_(self):
        self._bind(self._ll_expr_, u'e')

    def _ll_prim__c4__s5_(self):
        self._succeed([u'll_paren', self._get('e')], self.pos)

    def _ll_prim__c5_(self):
        self._push('ll_prim__c5')
        self._seq([lambda : self._expect(u'[', 1), self._sp_,
                   self._ll_prim__c5__s2_, self._sp_,
                   lambda : self._expect(u']', 1), self._ll_prim__c5__s5_])
        self._pop('ll_prim__c5')

    def _ll_prim__c5__s2_(self):
        self._bind(self._ll_exprs_, u'es')

    def _ll_prim__c5__s5_(self):
        self._succeed([u'll_arr', self._get('es')], self.pos)

    def _digits_(self):
        self._choose([self._digits__c0_])

    def _digits__c0_(self):
        self._push('digits__c0')
        self._seq([self._digits__c0__s0_, self._digits__c0__s1_])
        self._pop('digits__c0')

    def _digits__c0__s0_(self):
        self._bind(self._digits__c0__s0_l_, u'ds')

    def _digits__c0__s0_l_(self):
        self._plus(self._digit_)

    def _digits__c0__s1_(self):
        self._succeed(self._join(u'', self._get('ds')), self.pos)

    def _hexdigits_(self):
        self._choose([self._hexdigits__c0_])

    def _hexdigits__c0_(self):
        self._push('hexdigits__c0')
        self._seq([self._hexdigits__c0__s0_, self._hexdigits__c0__s1_])
        self._pop('hexdigits__c0')

    def _hexdigits__c0__s0_(self):
        self._bind(self._hexdigits__c0__s0_l_, u'hs')

    def _hexdigits__c0__s0_l_(self):
        self._plus(self._hex_)

    def _hexdigits__c0__s1_(self):
        self._succeed(self._join(u'', self._get('hs')), self.pos)

    def _hex_(self):
        self._choose([self._hex__c0_, self._hex__c1_, self._hex__c2_])

    def _hex__c0_(self):
        self._seq([self._digit_])

    def _hex__c1_(self):
        self._seq([self._hex__c1__s0_])

    def _hex__c1__s0_(self):
        self._range(u'a', u'f')

    def _hex__c2_(self):
        self._seq([self._hex__c2__s0_])

    def _hex__c2__s0_(self):
        self._range(u'A', u'F')

    def _hex_esc_(self):
        self._choose([self._hex_esc__c0_])

    def _hex_esc__c0_(self):
        self._push('hex_esc__c0')
        self._seq([lambda : self._expect(u'x', 1), self._hex_esc__c0__s1_,
                   self._hex_esc__c0__s2_, self._hex_esc__c0__s3_])
        self._pop('hex_esc__c0')

    def _hex_esc__c0__s1_(self):
        self._bind(self._hex_, u'h1')

    def _hex_esc__c0__s2_(self):
        self._bind(self._hex_, u'h2')

    def _hex_esc__c0__s3_(self):
        self._succeed(self._xtou(self._get('h1') + self._get('h2')), self.pos)

    def _digit_(self):
        self._choose([self._digit__c0_])

    def _digit__c0_(self):
        self._seq([self._digit__c0__s0_])

    def _digit__c0__s0_(self):
        self._range(u'0', u'9')

    def _anything_(self):
        if self.pos < self.end:
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()

    def _end_(self):
        if self.pos == self.end:
            self._succeed(None, self.pos)
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

    def _succeed(self, v, newpos):
        self.val = v
        self.err = False
        self.pos = newpos

    def _fail(self):
        self.val = None
        self.err = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _failed(self):
        return self.err

    def _rewind(self, newpos):
        self.val = None
        self.err = False
        self.pos = newpos

    def _bind(self, rule, var):
        rule()
        if not self._failed():
            self._set(var, self.val)

    def _not(self, rule):
        p = self.pos
        rule()
        if self._failed():
            self._succeed(None, p)
        else:
            self._rewind(p)
            self._fail()

    def _opt(self, rule):
        p = self.pos
        rule()
        if self._failed():
            self._succeed([], p)
        else:
            self._succeed([self.val], self.pos)

    def _plus(self, rule):
        vs = []
        rule()
        vs.append(self.val)
        if self._failed():
            return
        self._star(rule, vs)

    def _star(self, rule, vs=None):
        vs = vs or []
        while not self._failed():
            p = self.pos
            rule()
            if self._failed():
                self._rewind(p)
                break
            else:
                vs.append(self.val)
        self._succeed(vs, self.pos)

    def _seq(self, rules):
        for rule in rules:
            rule()
            if self._failed():
                return

    def _choose(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self._failed():
                return
            self._rewind(p)
        rules[-1]()
