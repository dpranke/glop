from compiled_parser_base import CompiledParserBase


class CompiledGrammarParser(CompiledParserBase):

    def _grammar_(self):
        """ (sp rule)*:vs sp end -> vs """
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
        """ (' '|'\n'|'\t') """
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
        """ ws* """
        vs = []
        while not self.err:
            self._ws_()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None

    def _rule_(self):
        """ ident:i sp '=' sp choice:cs sp ',' -> ['rule', i, cs] """
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
        """ (letter|'_'):hd (letter|'_'|digit)*:tl -> ''.join([hd] + tl) """
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
        """ seq:s (sp '|' sp seq)*:ss -> ['choice', [s] + ss] """
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
        """ expr:e (ws sp expr)*:es -> ['seq', [e] + es]|-> ['empty'] """
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
        """ post_expr:e ':' ident:l -> ['label', e, l]|post_expr """
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
        """ prim_expr:e post_op:op -> ['post', e, op]|prim_expr """
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
        """ lit|ident:i -> ['apply', i]|'->' sp py_expr:e -> ['action', e]|'~' prim_expr:e -> ['not', e]|'?(' sp py_expr:e sp ')' -> ['pred', e]|'(' sp choice:e sp ')' -> ['paren', e] """
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
        """ quote (~quote qchar)*:cs quote -> ['lit', ''.join(cs)] """
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
        self.val = ['lit', ''.join(v_cs)]
        self.err = None

    def _qchar_(self):
        """ '\\\'' -> '\''|anything """
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
        """ '\'' """
        self._expect('\'')

    def _py_expr_(self):
        """ py_qual:e1 sp '+' sp py_expr:e2 -> ['py_plus', e1, e2]|py_qual """
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
        """ py_prim:e (py_post_op)+:ps -> ['py_qual', e, ps]|py_prim """
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
        """ '[' sp py_expr:e sp ']' -> ['py_getitem', e]|'(' sp py_exprs:es sp ')' -> ['py_call', es]|'.' ident:i -> ['py_getattr', i] """
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
        """ ident:i -> ['py_var', i]|digit+:ds -> ['py_num', ''.join(ds)]|lit:l -> ['py_lit', l[1]]|'(' sp py_expr:e sp ')' -> ['py_paren', e]|'[' sp py_exprs:es sp ']' -> ['py_arr', [es]] """
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
            self.val = ['py_num', ''.join(v_ds)]
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
            self.val = ['py_arr', [v_es]]
            self.err = None
        choice_4()

    def _py_exprs_(self):
        """ py_expr:e (sp ',' sp py_expr)*:es -> [e] + es|-> [] """
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
        """ ('?'|'*'|'+') """
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
