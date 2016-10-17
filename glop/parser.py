class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar', starting_pos=0):
        self.msg = msg
        self.fname = fname
        self.starting_rule = starting_rule
        self.starting_pos = starting_pos
        self.end = len(msg)
        self.val = None
        self.err = None
        self.maxerr = None
        self.pos = self.starting_pos
        self.maxpos = self.starting_pos
        self.builtins = ('anything', 'digit', 'letter', 'end')

    def parse(self, rule=None, start=0):
        rule = rule or self.starting_rule
        self.pos = start
        self.apply_rule(rule)
        if self.err:
            lineno, colno = self._line_and_colno()
            return None, "%s:%d:%d expecting %s" % (
                self.fname, lineno, colno, self.maxerr)
        return self.val, None

    def apply_rule(self, rule):
        rule_fn = getattr(self, '_' + rule + '_', None)
        if not rule_fn:
            self.err = 'unknown rule "%s"' % rule
        rule_fn()

    def _line_and_colno(self):
        lineno = 1
        colno = 1
        i = 0
        while i < self.maxpos:
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
            i += 1
        return lineno, colno

    def _expect(self, expr):
        p = self.pos
        l = len(expr)
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self.pos += l
            self.val = expr
            self.err = None
        else:
            self.val = None
            self.err = "'%s'" % expr
            if self.pos > self.maxpos:
                self.maxpos, self.maxerr = self.pos, self.err
        return

    def _atoi(self, s):
        return int(s)

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
            def group():
                self._sp_()
                if self.err:
                    return
                self._rule_()
            group()
            if not self.err:
                vs.append(self.val)
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

    def _ws_(self):
        def group():
            p = self.pos
            def choice_0():
                self._expect(' ')
            choice_0()
            if not self.err:
                return

            self.pos = p
            def choice_1():
                self._expect('\n')
            choice_1()
            if not self.err:
                return

            self.pos = p
            def choice_2():
                self._expect('\t')
            choice_2()
        group()

    def _sp_(self):
        vs = []
        while not self.err:
            self._ws_()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None

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
        self._expect(',')
        if self.err:
            return
        self.val = ['rule', v_i, v_cs]
        self.err = None

    def _ident_(self):
        def group():
            p = self.pos
            def choice_0():
                self._letter_()
            choice_0()
            if not self.err:
                return

            self.pos = p
            def choice_1():
                self._expect('_')
            choice_1()
        group()
        if not self.err:
            v_hd = self.val
        if self.err:
            return
        vs = []
        while not self.err:
            def group():
                p = self.pos
                def choice_0():
                    self._letter_()
                choice_0()
                if not self.err:
                    return

                self.pos = p
                def choice_1():
                    self._expect('_')
                choice_1()
                if not self.err:
                    return

                self.pos = p
                def choice_2():
                    self._digit_()
                choice_2()
            group()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None
        if not self.err:
            v_tl = self.val
        if self.err:
            return
        self.val = ''.join([v_hd] + v_tl)
        self.err = None

    def _choice_(self):
        self._seq_()
        if not self.err:
            v_s = self.val
        if self.err:
            return
        vs = []
        while not self.err:
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

        self.pos = p
        def choice_1():
            self._ident_()
            if not self.err:
                v_i = self.val
            if self.err:
                return
            self.val = ['apply', v_i]
            self.err = None
        choice_1()
        if not self.err:
            return

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
        self._quote_()
        if self.err:
            return
        vs = []
        while not self.err:
            def group():
                p = self.pos
                self._quote_()
                self.pos = p
                if not self.err:
                     self.err = "not"
                     self.val = None
                     return
                self.err = None
                if self.err:
                    return
                self._qchar_()
            group()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None
        if not self.err:
            v_cs = self.val
        if self.err:
            return
        self._quote_()
        if self.err:
            return
        self.val = ['lit', self._join('', v_cs)]
        self.err = None

    def _qchar_(self):
        p = self.pos
        def choice_0():
            self._expect('\\\'')
            if self.err:
                return
            self.val = '\''
            self.err = None
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._anything_()
        choice_1()

    def _quote_(self):
        self._expect('\'')

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
                def group():
                    self._py_post_op_()
                group()
                if not self.err:
                    vs.append(self.val)
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

        self.pos = p
        def choice_1():
            vs = []
            self._digit_()
            if self.err:
                return
            vs.append(self.val)
            while not self.err:
                self._digit_()
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if not self.err:
                v_ds = self.val
            if self.err:
                return
            self.val = ['py_num', self._atoi(self._join('', v_ds))]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._lit_()
            if not self.err:
                v_l = self.val
            if self.err:
                return
            self.val = ['py_lit', v_l[1]]
            self.err = None
        choice_2()
        if not self.err:
            return

        self.pos = p
        def choice_3():
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
        choice_3()
        if not self.err:
            return

        self.pos = p
        def choice_4():
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
        choice_4()

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

            self.pos = p
            def choice_1():
                self._expect('*')
            choice_1()
            if not self.err:
                return

            self.pos = p
            def choice_2():
                self._expect('+')
            choice_2()
        group()
