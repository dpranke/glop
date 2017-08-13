# pylint: disable=line-too-long

class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar', starting_pos=0):
        self.msg = msg
        self.fname = fname
        self.starting_rule = starting_rule
        self.starting_pos = starting_pos
        self.end = len(msg)
        self.val = None
        self.err = None
        self.pos = self.starting_pos
        self.errpos = self.starting_pos
        self.errset = set()
        self.builtins = ('anything', 'digit', 'end', 'letter')

    def parse(self, rule=None, start=0):
        rule = rule or self.starting_rule
        self.pos = start or self.starting_pos
        self.apply_rule(rule)
        if self.err:
            return None, self._err_str()
        return self.val, None

    def apply_rule(self, rule):
        rule_fn = getattr(self, '_' + rule + '_', None)
        if not rule_fn:
            self.err = 'unknown rule "%s"' % rule
            return None, True
        rule_fn()

    def _err_str(self):
        lineno, colno, _ = self._err_offsets()
        if isinstance(self.err, basestring):
            return '%s:%d %s' % (self.fname, lineno, self.err)
        exps = sorted(self.errset)
        if len(exps) > 2:
            expstr = "either %s, or '%s'" % (
                ', '.join("'%s'" % exp for exp in exps[:-1]), exps[-1])
        elif len(exps) == 2:
            expstr = "either '%s' or '%s'" % (exps[0], exps[1])
        elif len(exps) == 1:
            expstr = "a '%s'" % exps[0]
        else:
            expstr = '<EOF>'
        prefix = '%s:%d' % (self.fname, lineno)
        return "%s Expecting %s at column %d" % (prefix, expstr, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        i = 0
        begpos = 0
        while i < self.errpos:
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
                begpos = i
            else:
                colno += 1
            i += 1
        return lineno, colno, begpos

    def _py_escape(self, expr):
        return expr.replace('\r', '\\r').replace('\n', '\\n').replace(
            '\t', '\\t')

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
                self.errset.add(self._py_escape(expr))
                self.errpos = self.pos
        return

    def _atoi(self, s):
        if s.startswith('0x'):
            return int(s, base=16)
        return int(s)

    def _itoa(self, n):
        return str(n)

    def _join(self, s, vs):
        return s.join(vs)

    def _anything_(self):
        if self.pos < self.end:
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "anything"

    def _end_(self):
        self._anything_()
        if self.err:
            self.val = None
            self.err = None
        else:
            self.val = None
            self.err = "the end"
        return

    def _letter_(self):
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a letter"
        return

    def _digit_(self):
        if self.pos < self.end and self.msg[self.pos].isdigit():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a digit"
        return

    def _grammar_(self):
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._rule_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            v_vs = self.val
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        self._end_()
        if self.err:
            return
        self.val = v_vs
        self.err = None

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
            self._expect(' ')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\t')
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
            self._expect('\r')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\n')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('\r\n')
        choice_2()

    def _comment_(self):
        self._expect('//')
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
        if self.err:
            return
        self._eol_()

    def _rule_(self):
        self._ident_()
        if not self.err:
            v_i = self.val
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        self._expect('=')
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        self._choice_()
        if not self.err:
            v_cs = self.val
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        p = self.pos
        self._expect(',')
        if self.err:
            self.val = []
            self.err = None
            self.pos = p
        else:
            self.val = [self.val]
        if self.err:
            return
        self.val = ['rule', v_i, v_cs]
        self.err = None

    def _ident_(self):
        self._id_start_()
        if not self.err:
            v_hd = self.val
        if self.err:
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
            v_tl = self.val
        if self.err:
            return
        self.val = ''.join([v_hd] + v_tl)
        self.err = None

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
            self._expect('_')
        choice_1()

    def _id_continue_(self):
        p = self.pos
        def choice_0():
            self._letter_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('_')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._digit_()
        choice_2()

    def _choice_(self):
        self._seq_()
        if not self.err:
            v_s = self.val
        if self.err:
            return
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._expect('|')
                if self.err:
                    return
                self._sp_()
                if self.err:
                    return
                self._seq_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            v_ss = self.val
        if self.err:
            return
        self.val = ['choice', [v_s] + v_ss]
        self.err = None

    def _seq_(self):
        p = self.pos
        def choice_0():
            self._expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._ws_()
                    if self.err:
                        return
                    self._sp_()
                    if self.err:
                        return
                    self._expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                v_es = self.val
            if self.err:
                return
            self.val = ['seq', [v_e] + v_es]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = ['empty']
            self.err = None
        choice_1()

    def _expr_(self):
        p = self.pos
        def choice_0():
            self._post_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._expect(':')
            if self.err:
                return
            self._ident_()
            if not self.err:
                v_l = self.val
            if self.err:
                return
            self.val = ['label', v_e, v_l]
            self.err = None
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
            self._prim_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._post_op_()
            if not self.err:
                v_op = self.val
            if self.err:
                return
            self.val = ['post', v_e, v_op]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._prim_expr_()
        choice_1()

    def _prim_expr_(self):
        p = self.pos
        def choice_0():
            self._lit_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._ident_()
            if not self.err:
                v_i = self.val
            if self.err:
                return
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._expect('=')
            group()
            self.pos = p
            if not self.err:
                 self.err = "not"
                 self.val = None
                 return
            self.err = None
            if self.err:
                return
            self.val = ['apply', v_i]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('->')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self.val = ['action', v_e]
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect('~')
            if self.err:
                return
            self._prim_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self.val = ['not', v_e]
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect('?(')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(')')
            if self.err:
                return
            self.val = ['pred', v_e]
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect('(')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._choice_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(')')
            if self.err:
                return
            self.val = ['paren', v_e]
            self.err = None
        choice_5()

    def _lit_(self):
        p = self.pos
        def choice_0():
            self._squote_()
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._squote_()
                    self.pos = p
                    if not self.err:
                         self.err = "not"
                         self.val = None
                         return
                    self.err = None
                    if self.err:
                        return
                    self._sqchar_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                v_cs = self.val
            if self.err:
                return
            self._squote_()
            if self.err:
                return
            self.val = ['lit', self._join('', v_cs)]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._dquote_()
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._dquote_()
                    self.pos = p
                    if not self.err:
                         self.err = "not"
                         self.val = None
                         return
                    self.err = None
                    if self.err:
                        return
                    self._dqchar_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                v_cs = self.val
            if self.err:
                return
            self._dquote_()
            if self.err:
                return
            self.val = ['lit', self._join('', v_cs)]
            self.err = None
        choice_1()

    def _sqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._squote_()
            if self.err:
                return
            self.val = '\x5C\x27'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._anything_()
        choice_1()

    def _dqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._dquote_()
            if self.err:
                return
            self.val = '\x5C\x22'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._anything_()
        choice_1()

    def _bslash_(self):
        self._expect('\x5C')

    def _squote_(self):
        self._expect('\x27')

    def _dquote_(self):
        self._expect('\x22')

    def _py_expr_(self):
        p = self.pos
        def choice_0():
            self._py_qual_()
            if not self.err:
                v_e1 = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect('+')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_expr_()
            if not self.err:
                v_e2 = self.val
            if self.err:
                return
            self.val = ['py_plus', v_e1, v_e2]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._py_qual_()
        choice_1()

    def _py_qual_(self):
        p = self.pos
        def choice_0():
            self._py_prim_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            vs = []
            def group():
                self._py_post_op_()
            group()
            if self.err:
                return
            vs.append(self.val)
            while not self.err:
                p = self.pos
                def group():
                    self._py_post_op_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                v_ps = self.val
            if self.err:
                return
            self.val = ['py_qual', v_e, v_ps]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._py_prim_()
        choice_1()

    def _py_post_op_(self):
        p = self.pos
        def choice_0():
            self._expect('[')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(']')
            if self.err:
                return
            self.val = ['py_getitem', v_e]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('(')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_exprs_()
            if not self.err:
                v_es = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(')')
            if self.err:
                return
            self.val = ['py_call', v_es]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('.')
            if self.err:
                return
            self._ident_()
            if not self.err:
                v_i = self.val
            if self.err:
                return
            self.val = ['py_getattr', v_i]
            self.err = None
        choice_2()

    def _py_prim_(self):
        p = self.pos
        def choice_0():
            self._ident_()
            if not self.err:
                v_i = self.val
            if self.err:
                return
            self.val = ['py_var', v_i]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._digits_()
            if not self.err:
                v_ds = self.val
            if self.err:
                return
            self.val = ['py_num', v_ds]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('0x')
            if self.err:
                return
            self._hexdigits_()
            if not self.err:
                v_hs = self.val
            if self.err:
                return
            self.val = ['py_num', '0x' + v_hs]
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._lit_()
            if not self.err:
                v_l = self.val
            if self.err:
                return
            self.val = ['py_lit', v_l[1]]
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect('(')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(')')
            if self.err:
                return
            self.val = ['py_paren', v_e]
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect('[')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._py_exprs_()
            if not self.err:
                v_es = self.val
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(']')
            if self.err:
                return
            self.val = ['py_arr', v_es]
            self.err = None
        choice_5()

    def _digits_(self):
        vs = []
        self._digit_()
        if self.err:
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
            v_ds = self.val
        if self.err:
            return
        self.val = self._join('', v_ds)
        self.err = None

    def _hexdigits_(self):
        vs = []
        self._hexdigit_()
        if self.err:
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._hexdigit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            v_hs = self.val
        if self.err:
            return
        self.val = self._join('', v_hs)
        self.err = None

    def _hexdigit_(self):
        p = self.pos
        def choice_0():
            self._digit_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('a')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('b')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect('c')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect('d')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect('e')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._expect('f')
        choice_6()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_7():
            self._expect('A')
        choice_7()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_8():
            self._expect('B')
        choice_8()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_9():
            self._expect('C')
        choice_9()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_10():
            self._expect('D')
        choice_10()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_11():
            self._expect('E')
        choice_11()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_12():
            self._expect('F')
        choice_12()

    def _py_exprs_(self):
        p = self.pos
        def choice_0():
            self._py_expr_()
            if not self.err:
                v_e = self.val
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._sp_()
                    if self.err:
                        return
                    self._expect(',')
                    if self.err:
                        return
                    self._sp_()
                    if self.err:
                        return
                    self._py_expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                v_es = self.val
            if self.err:
                return
            self.val = [v_e] + v_es
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = []
            self.err = None
        choice_1()

    def _post_op_(self):
        def group():
            p = self.pos
            def choice_0():
                self._expect('?')
            choice_0()
            if not self.err:
                return

            self.err = False
            self.pos = p
            def choice_1():
                self._expect('*')
            choice_1()
            if not self.err:
                return

            self.err = False
            self.pos = p
            def choice_2():
                self._expect('+')
            choice_2()
        group()
