# pylint: disable=line-too-long

import sys


if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    str = unicode
    chr = unichr


class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar'):
        self.msg = str(msg)
        self.end = len(msg)
        self.fname = fname
        self.starting_rule = starting_rule
        self.val = None
        self.err = None
        self.pos = 0
        self.errpos = 0
        self.errset = set()
        self.scopes = []

    def parse(self):
        rule_fn = getattr(self, '_' + self.starting_rule + '_', None)
        if not rule_fn:
            return None, 'unknown rule "%s"' % self.starting_rule
        rule_fn()
        if self.err:
            return None, self._err_str()
        return self.val, None

    def _push(self, name):
        self.scopes.append((name, {}))

    def _pop(self, name):
        actual_name, _ = self.scopes.pop()
        assert name == actual_name

    def _get(self, var):
        return self.scopes[-1][1][var]

    def _set(self, var, val):
        self.scopes[-1][1][var] = val

    def _err_str(self):
        lineno, colno, _ = self._err_offsets()
        prefix = u'%s:%d' % (self.fname, lineno)
        if self.errpos == self.end:
            thing = "<end of input>"
        else:
            thing = self.msg[self.errpos]
        return u'%s Unexpected "%s" at column %d' % (
                prefix, thing, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        i = 0
        begpos = 0
        while i < self.errpos:
            if self.msg[i] == u'\n':
                lineno += 1
                colno = 1
                begpos = i
            else:
                colno += 1
            i += 1
        return lineno, colno, begpos

    def _esc(self, val):
        return str(val)

    def _expect(self, expr):
        p = self.pos
        l = len(expr)
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self.pos += l
            self.val = expr
            self.err = False
        else:
            self.val = None
            self.err = True
            if self.pos >= self.errpos:
                if self.pos > self.errpos:
                    self.errset = set()
                self.errset.add(self._esc(expr))
                self.errpos = self.pos
        return

    def _grammar_(self):
        self._push('grammar')
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                self._rule_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('vs', self.val)
        if self.err:
            self._pop('grammar')
            return
        self._sp_()
        self._end_()
        if self.err:
            self._pop('grammar')
            return
        self.val = self._get('vs')
        self.err = None
        self._pop('grammar')

    def _sp_(self):
        vs = []
        while not self.err:
            p = self.pos
            self._ws_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None

    def _ws_(self):
        p = self.pos
        def choice_0():
            self._expect(u' ')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'\t')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._eol_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._comment_()
        choice_3()

    def _eol_(self):
        p = self.pos
        def choice_0():
            self._expect(u'\r')
            if self.err:
                return
            self._expect(u'\n')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'\r')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'\n')
        choice_2()

    def _comment_(self):
        p = self.pos
        def choice_0():
            self._expect(u'//')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._eol_()
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._anything_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'/*')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._expect(u'*/')
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._anything_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            self._expect(u'*/')
        choice_1()

    def _rule_(self):
        self._push('rule')
        self._ident_()
        if not self.err:
            self._set('i', self.val)
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        self._expect(u'=')
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        self._choice_()
        if not self.err:
            self._set('cs', self.val)
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        p = self.pos
        self._expect(u',')
        if self.err:
            self.val = []
            self.err = None
            self.pos = p
        else:
            self.val = [self.val]
        self.val = [u'rule', self._get('i'), self._get('cs')]
        self.err = None
        self._pop('rule')

    def _ident_(self):
        self._push('ident')
        self._id_start_()
        if not self.err:
            self._set('hd', self.val)
        if self.err:
            self._pop('ident')
            return
        vs = []
        while not self.err:
            p = self.pos
            self._id_continue_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('tl', self.val)
        if self.err:
            self._pop('ident')
            return
        self.val = self._join(u'', [self._get('hd')] + self._get('tl'))
        self.err = None
        self._pop('ident')

    def _id_start_(self):
        p = self.pos
        def choice_0():
            self._letter_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'_')
        choice_1()

    def _id_continue_(self):
        p = self.pos
        def choice_0():
            self._id_start_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._digit_()
        choice_1()

    def _choice_(self):
        self._push('choice')
        self._seq_()
        if not self.err:
            self._set('s', self.val)
        if self.err:
            self._pop('choice')
            return
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                self._expect(u'|')
                if self.err:
                    return
                self._sp_()
                self._seq_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('ss', self.val)
        if self.err:
            self._pop('choice')
            return
        self.val = [u'choice', [self._get('s')] + self._get('ss')]
        self.err = None
        self._pop('choice')

    def _seq_(self):
        p = self.pos
        def choice_0():
            self._push('seq_0')
            self._expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('seq_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._ws_()
                    if self.err:
                        return
                    self._sp_()
                    self._expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('seq_0')
                return
            self.val = [u'seq', [self._get('e')] + self._get('es')]
            self.err = None
            self._pop('seq_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = [u'empty']
            self.err = None
        choice_1()

    def _expr_(self):
        p = self.pos
        def choice_0():
            self._push('expr_0')
            self._post_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('expr_0')
                return
            self._expect(u':')
            if self.err:
                self._pop('expr_0')
                return
            self._ident_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('expr_0')
                return
            self.val = [u'label', self._get('e'), self._get('l')]
            self.err = None
            self._pop('expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._post_expr_()
        choice_1()

    def _post_expr_(self):
        p = self.pos
        def choice_0():
            self._push('post_expr_0')
            self._prim_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('post_expr_0')
                return
            self._post_op_()
            if not self.err:
                self._set('op', self.val)
            if self.err:
                self._pop('post_expr_0')
                return
            self.val = [u'post', self._get('e'), self._get('op')]
            self.err = None
            self._pop('post_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._prim_expr_()
        choice_1()

    def _post_op_(self):
        p = self.pos
        def choice_0():
            self._expect(u'?')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'*')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'+')
        choice_2()

    def _prim_expr_(self):
        p = self.pos
        def choice_0():
            self._push('prim_expr_0')
            self._lit_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('prim_expr_0')
                return
            self._sp_()
            self._expect(u'..')
            if self.err:
                self._pop('prim_expr_0')
                return
            self._sp_()
            self._lit_()
            if not self.err:
                self._set('j', self.val)
            if self.err:
                self._pop('prim_expr_0')
                return
            self.val = [u'range', self._get('i'), self._get('j')]
            self.err = None
            self._pop('prim_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('prim_expr_1')
            self._lit_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('prim_expr_1')
                return
            self.val = self._get('l')
            self.err = None
            self._pop('prim_expr_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('prim_expr_2')
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('prim_expr_2')
                return
            p = self.pos
            def group():
                self._sp_()
                self._expect(u'=')
            group()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('prim_expr_2')
                return
            self.err = None
            if self.err:
                self._pop('prim_expr_2')
                return
            self.val = [u'apply', self._get('i')]
            self.err = None
            self._pop('prim_expr_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('prim_expr_3')
            self._expect(u'->')
            if self.err:
                self._pop('prim_expr_3')
                return
            self._sp_()
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_3')
                return
            self.val = [u'action', self._get('e')]
            self.err = None
            self._pop('prim_expr_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('prim_expr_4')
            self._expect(u'~')
            if self.err:
                self._pop('prim_expr_4')
                return
            self._prim_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_4')
                return
            self.val = [u'not', self._get('e')]
            self.err = None
            self._pop('prim_expr_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('prim_expr_5')
            self._expect(u'?(')
            if self.err:
                self._pop('prim_expr_5')
                return
            self._sp_()
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_5')
                return
            self._sp_()
            self._expect(u')')
            if self.err:
                self._pop('prim_expr_5')
                return
            self.val = [u'pred', self._get('e')]
            self.err = None
            self._pop('prim_expr_5')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._push('prim_expr_6')
            self._expect(u'(')
            if self.err:
                self._pop('prim_expr_6')
                return
            self._sp_()
            self._choice_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_6')
                return
            self._sp_()
            self._expect(u')')
            if self.err:
                self._pop('prim_expr_6')
                return
            self.val = [u'paren', self._get('e')]
            self.err = None
            self._pop('prim_expr_6')
        choice_6()

    def _lit_(self):
        p = self.pos
        def choice_0():
            self._push('lit_0')
            self._squote_()
            if self.err:
                self._pop('lit_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                self._sqchar_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('lit_0')
                return
            self._squote_()
            if self.err:
                self._pop('lit_0')
                return
            self.val = [u'lit', self._join(u'', self._get('cs'))]
            self.err = None
            self._pop('lit_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('lit_1')
            self._dquote_()
            if self.err:
                self._pop('lit_1')
                return
            vs = []
            while not self.err:
                p = self.pos
                self._dqchar_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('lit_1')
                return
            self._dquote_()
            if self.err:
                self._pop('lit_1')
                return
            self.val = [u'lit', self._join(u'', self._get('cs'))]
            self.err = None
            self._pop('lit_1')
        choice_1()

    def _sqchar_(self):
        p = self.pos
        def choice_0():
            self._push('sqchar_0')
            self._bslash_()
            if self.err:
                self._pop('sqchar_0')
                return
            self._esc_char_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('sqchar_0')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('sqchar_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('sqchar_1')
            p = self.pos
            self._squote_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('sqchar_1')
                return
            self.err = None
            if self.err:
                self._pop('sqchar_1')
                return
            self._anything_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('sqchar_1')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('sqchar_1')
        choice_1()

    def _dqchar_(self):
        p = self.pos
        def choice_0():
            self._push('dqchar_0')
            self._bslash_()
            if self.err:
                self._pop('dqchar_0')
                return
            self._esc_char_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('dqchar_0')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('dqchar_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('dqchar_1')
            p = self.pos
            self._dquote_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('dqchar_1')
                return
            self.err = None
            if self.err:
                self._pop('dqchar_1')
                return
            self._anything_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('dqchar_1')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('dqchar_1')
        choice_1()

    def _bslash_(self):
        self._expect(u'\\')

    def _squote_(self):
        self._expect(u"'")

    def _dquote_(self):
        self._expect(u'"')

    def _esc_char_(self):
        p = self.pos
        def choice_0():
            self._expect(u'b')
            if self.err:
                return
            self.val = u'\x08'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'f')
            if self.err:
                return
            self.val = u'\x0c'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'n')
            if self.err:
                return
            self.val = u'\n'
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect(u'r')
            if self.err:
                return
            self.val = u'\r'
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect(u't')
            if self.err:
                return
            self.val = u'\t'
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect(u'v')
            if self.err:
                return
            self.val = u'\x0b'
            self.err = None
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._squote_()
            if self.err:
                return
            self.val = u"'"
            self.err = None
        choice_6()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_7():
            self._dquote_()
            if self.err:
                return
            self.val = u'"'
            self.err = None
        choice_7()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_8():
            self._bslash_()
            if self.err:
                return
            self.val = u'\\'
            self.err = None
        choice_8()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_9():
            self._push('esc_char_9')
            self._hex_esc_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('esc_char_9')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('esc_char_9')
        choice_9()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_10():
            self._push('esc_char_10')
            self._unicode_esc_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('esc_char_10')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('esc_char_10')
        choice_10()

    def _hex_esc_(self):
        self._push('hex_esc')
        self._expect(u'x')
        if self.err:
            self._pop('hex_esc')
            return
        self._hex_()
        if not self.err:
            self._set('h1', self.val)
        if self.err:
            self._pop('hex_esc')
            return
        self._hex_()
        if not self.err:
            self._set('h2', self.val)
        if self.err:
            self._pop('hex_esc')
            return
        self.val = self._xtou(self._get('h1') + self._get('h2'))
        self.err = None
        self._pop('hex_esc')

    def _unicode_esc_(self):
        p = self.pos
        def choice_0():
            self._push('unicode_esc_0')
            self._expect(u'u')
            if self.err:
                self._pop('unicode_esc_0')
                return
            self._hex_()
            if not self.err:
                self._set('a', self.val)
            if self.err:
                self._pop('unicode_esc_0')
                return
            self._hex_()
            if not self.err:
                self._set('b', self.val)
            if self.err:
                self._pop('unicode_esc_0')
                return
            self._hex_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('unicode_esc_0')
                return
            self._hex_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('unicode_esc_0')
                return
            self.val = self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d'))
            self.err = None
            self._pop('unicode_esc_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('unicode_esc_1')
            self._expect(u'U')
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('a', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('b', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('f', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('g', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self._hex_()
            if not self.err:
                self._set('h', self.val)
            if self.err:
                self._pop('unicode_esc_1')
                return
            self.val = self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d') + self._get('e') + self._get('f') + self._get('g') + self._get('h'))
            self.err = None
            self._pop('unicode_esc_1')
        choice_1()

    def _ll_exprs_(self):
        p = self.pos
        def choice_0():
            self._push('ll_exprs_0')
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_exprs_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._sp_()
                    self._expect(u',')
                    if self.err:
                        return
                    self._sp_()
                    self._ll_expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_exprs_0')
                return
            self.val = [self._get('e')] + self._get('es')
            self.err = None
            self._pop('ll_exprs_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = []
            self.err = None
        choice_1()

    def _ll_expr_(self):
        p = self.pos
        def choice_0():
            self._push('ll_expr_0')
            self._ll_qual_()
            if not self.err:
                self._set('e1', self.val)
            if self.err:
                self._pop('ll_expr_0')
                return
            self._sp_()
            self._expect(u'+')
            if self.err:
                self._pop('ll_expr_0')
                return
            self._sp_()
            self._ll_expr_()
            if not self.err:
                self._set('e2', self.val)
            if self.err:
                self._pop('ll_expr_0')
                return
            self.val = [u'll_plus', self._get('e1'), self._get('e2')]
            self.err = None
            self._pop('ll_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._ll_qual_()
        choice_1()

    def _ll_qual_(self):
        p = self.pos
        def choice_0():
            self._push('ll_qual_0')
            self._ll_prim_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_qual_0')
                return
            vs = []
            self._ll_post_op_()
            if self.err:
                self._pop('ll_qual_0')
                return
            vs.append(self.val)
            while not self.err:
                p = self.pos
                self._ll_post_op_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('ps', self.val)
            if self.err:
                self._pop('ll_qual_0')
                return
            self.val = [u'll_qual', self._get('e'), self._get('ps')]
            self.err = None
            self._pop('ll_qual_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._ll_prim_()
        choice_1()

    def _ll_post_op_(self):
        p = self.pos
        def choice_0():
            self._push('ll_post_op_0')
            self._expect(u'[')
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._sp_()
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._sp_()
            self._expect(u']')
            if self.err:
                self._pop('ll_post_op_0')
                return
            self.val = [u'll_getitem', self._get('e')]
            self.err = None
            self._pop('ll_post_op_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('ll_post_op_1')
            self._expect(u'(')
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._sp_()
            self._ll_exprs_()
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._sp_()
            self._expect(u')')
            if self.err:
                self._pop('ll_post_op_1')
                return
            self.val = [u'll_call', self._get('es')]
            self.err = None
            self._pop('ll_post_op_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('ll_post_op_2')
            self._expect(u'.')
            if self.err:
                self._pop('ll_post_op_2')
                return
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('ll_post_op_2')
                return
            self.val = [u'll_getattr', self._get('i')]
            self.err = None
            self._pop('ll_post_op_2')
        choice_2()

    def _ll_prim_(self):
        p = self.pos
        def choice_0():
            self._push('ll_prim_0')
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('ll_prim_0')
                return
            self.val = [u'll_var', self._get('i')]
            self.err = None
            self._pop('ll_prim_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('ll_prim_1')
            self._digits_()
            if not self.err:
                self._set('ds', self.val)
            if self.err:
                self._pop('ll_prim_1')
                return
            self.val = [u'll_num', self._get('ds')]
            self.err = None
            self._pop('ll_prim_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('ll_prim_2')
            self._expect(u'0x')
            if self.err:
                self._pop('ll_prim_2')
                return
            self._hexdigits_()
            if not self.err:
                self._set('hs', self.val)
            if self.err:
                self._pop('ll_prim_2')
                return
            self.val = [u'll_num', u'0x' + self._get('hs')]
            self.err = None
            self._pop('ll_prim_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('ll_prim_3')
            self._lit_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('ll_prim_3')
                return
            self.val = [u'll_lit', self._get('l')[1]]
            self.err = None
            self._pop('ll_prim_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('ll_prim_4')
            self._expect(u'(')
            if self.err:
                self._pop('ll_prim_4')
                return
            self._sp_()
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_prim_4')
                return
            self._sp_()
            self._expect(u')')
            if self.err:
                self._pop('ll_prim_4')
                return
            self.val = [u'll_paren', self._get('e')]
            self.err = None
            self._pop('ll_prim_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('ll_prim_5')
            self._expect(u'[')
            if self.err:
                self._pop('ll_prim_5')
                return
            self._sp_()
            self._ll_exprs_()
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_prim_5')
                return
            self._sp_()
            self._expect(u']')
            if self.err:
                self._pop('ll_prim_5')
                return
            self.val = [u'll_arr', self._get('es')]
            self.err = None
            self._pop('ll_prim_5')
        choice_5()

    def _digits_(self):
        self._push('digits')
        vs = []
        self._digit_()
        if self.err:
            self._pop('digits')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._digit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('ds', self.val)
        if self.err:
            self._pop('digits')
            return
        self.val = self._join(u'', self._get('ds'))
        self.err = None
        self._pop('digits')

    def _hexdigits_(self):
        self._push('hexdigits')
        vs = []
        self._hex_()
        if self.err:
            self._pop('hexdigits')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._hex_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('hs', self.val)
        if self.err:
            self._pop('hexdigits')
            return
        self.val = self._join(u'', self._get('hs'))
        self.err = None
        self._pop('hexdigits')

    def _hex_(self):
        p = self.pos
        def choice_0():
            self._digit_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            i = u'a'
            j = u'f'
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[self.pos]
                self.err = False
                self.pos += 1
            return
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            i = u'A'
            j = u'F'
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[self.pos]
                self.err = False
                self.pos += 1
            return
        choice_2()

    def _digit_(self):
        i = u'0'
        j = u'9'
        if (self.pos == self.end or
            ord(self.msg[self.pos]) < ord(i) or
            ord(self.msg[self.pos]) > ord(j)):
            self.val = None
            self.err = True
            if self.pos >= self.errpos:
                if self.pos > self.errpos:
                    self.errset = set()
                self.errset.add('something between %s and %s' % (i, j))
                self.errpos = self.pos
        else:
            self.val = self.msg[self.pos]
            self.err = False
            self.pos += 1
        return

    def _anything_(self):
        if self.pos < self.end:
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = u'anything'

    def _end_(self):
        if self.pos == self.end:
            self.val = None
            self.err = None
        else:
            self.val = None
            self.err = u'the end'
        return

    def _letter_(self):
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = u'a letter'
        return

    def _join(self, s, vs):
        return s.join(vs)

    def _xtou(self, s):
        return chr(int(s, base=16))
