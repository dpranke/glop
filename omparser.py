from parser import Parser


class OMParser(Parser):
    def _grammar_(self, p):
        """ = (sp rule)*:vs sp end                   -> vs """
        err = None
        vs = []
        p1 = p
        while not err:
            _, p, _ = self._sp_(p)
            v, p, err = self._rule_(p)
            if not err:
                vs.append(v)
                p1 = p
        _, p, _ = self._sp_(p1)
        _, p, err = self._end_(p)
        if err:
            return None, p, err
        return vs, p, None

    def _sp_(self, p):
        """ = (' ' | '\n' | '\t')* """
        err = None
        while not err:
            v, p, err = self._expect(p, ' ')
            if not err:
                continue

            v, p, err = self._expect(p, '\n')
            if not err:
                continue

            v, p, err = self._expect(p, '\t')
            if not err:
                continue
        return v, p, None

    def _rule_(self, p):
        """ = ident:i sp '=' sp choice:s sp ','     -> ['rule', i, c] """
        i, p, err = self._ident_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, '=')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            cs, p, err = self._choice_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, ',')
        if not err:
            return ['rule', i, cs], p, None
        return None, p, err

    def _ident_(self, p):
        """ = (letter|'_'):hd (letter|'_'|digit)*:tl -> ''.join([hd] + tl) """
        v, p, err = self._letter_(p)
        if err:
            v, p, err = self._expect(p, '_')

        if not err:
            hd = v
            tl = []
            while p < self.end and not err:
                v, p, err = self._letter_(p)
                if err:
                    v, p, err = self._digit_(p)
                    if err:
                        v, p, err = self._expect(p, '_')
                if not err:
                    tl.append(v)
            return ''.join([hd] + tl), p, None

        return None, p, "expecting a letter or '_'"

    def _choice_(self, p):
        """ = seq:c (sp '|' sp choice)+:cs     -> ['choice', [c] + cs]
            | seq """
        c, p, err = self._seq_(p)
        if err:
            return None, p, err

        p1 = p
        cs = []
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, '|')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            v, p, err = self._choice_(p)
            if not err:
                cs.append(v)
                while not err:
                    _, p, err = self._sp_(p)
                    if not err:
                        _, p, err = self._expect(p, '|')
                    if not err:
                        _, p, err = self._sp_(p)
                    if not err:
                        v, p, err = self._choice_(p)
                    if not err:
                        cs.append[v]
                return ['choice', [c] + cs], p, None

        return c, p1, None

    def _seq_(self, p):
        """ = expr:e (sp expr)+:es                 -> ['seq', [e] + es]
            | expr:e                               -> e
        """
        e, p, err = self._expr_(p)
        if err:
            return None, p, err

        p1 = p
        es = []
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            v, p, err = self._expr_(p)
        if not err:
            es.append(v)
            while not err:
                _, p, err = self._sp_(p)
                if not err:
                    v, p, err = self._expr_(p)
                if not err:
                    es.append(v)
            return ['seq', [e] + es], p, None

        return e, p1, None

    def _expr_(self, p):
        """ = post_expr:e ':' ident:i                -> ['label', e, i]
            | post_expr
        """
        e, p, err = self._post_expr_(p)
        if err:
            return None, p, err
        p1 = p
        if not err:
            _, p, err = self._expect(p, ':')
        if not err:
            i, p, err = self._ident_(p)
        if not err:
            return ['label', e, i], p, None

        return e, p1, None

    def _post_expr_(self, p):
        """ = prim_expr:e post_op:op                 -> ['post', e, op]
            | prim_expr
        """
        e, p, err = self._prim_expr_(p)
        if err:
            return None, p, err
        p1 = p
        if not err:
            op, p, err = self._post_op_(p)
        if not err:
            return ['post', e, op], p, None

        return e, p1, None

    def _prim_expr_(self, p):
        """ = literal
            | ident:i                                -> ['apply', i]
            | '->' sp py_expr:e                      -> ['action', e]
            | '~' prim_expr:e                        -> ['not', pe]
            | '?(' sp py_expr:e sp ')'               -> ['pred', e]
            | '(' sp choice_expr:e sp ')'            -> e
        """
        start = p
        v, p, err = self._literal_(p)
        if not err:
            return v, p, err

        i, p, err = self._ident_(start)
        if not err:
            return ['apply', i], p, None

        _, p, err = self._expect(start, '->')
        if not err:
            _, p, err = self._sp_(p)
            if not err:
                e, p, err = self._py_expr_(p)
            if not err:
                return ['action', e], p, None

        _, p, err = self._expect(start, '~')
        if not err:
            v, pe, err = self._prim_expr_(p)
        if not err:
            return ['not', pe]

        _, p, err = self._expect(start, '?(')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            e, p, err = self._py_expr_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, ')')
        if not err:
            return ['pred', e], p, None

        _, p, err = self._expect(start, '(')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            e, p, err = self._choice_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(start, ')')
        if not err:
            return e, p, None

        return None, start, "one of a literal, an ident, '~', '?(', or '('"

    def _literal_(self, p):
        """ = quote (~quote anything)+:cs quote      -> ''.join(cs) """
        cs = []
        v, p, err = self._quote_(p)
        if not err:
            _, p, err = self._quote_(p)
            if err:
                v, p, err = self._anything_(p)
                if not err:
                    cs.append(v)
            while p < self.end and not err:
                _, p, err = self._quote_(p)
                if not err:
                    return ['lit', ''.join(cs)], p, None
                v, p, err = self._anything_(p)
                if not err:
                    cs.append(v)
        return None, p, err

    def _quote_(self, p):
        """ = '\'' """
        return self._expect(p, '\'')

    def _py_expr_(self, p):
        """ = py_qual:e1 sp '+' py_expr:e2            -> ['plus', e1, e2]
            | py_qual
        """
        e1, p, err = self._py_qual_(p)
        p1 = p
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, '+')
        if not err:
            e2, p, err = self._py_expr_(p)
        if not err:
            return ['plus', e1, e2], p, None

        return e1, p1, None

    def _py_qual_(self, p):
        """ = py_prim:e [py_post_op]+:ps             -> ['py_qual', e, ps]
            | py_prim
        """
        e, p, err = self._py_prim_(p)
        if err:
            return None, p, err
        p1 = p
        if not err:
            ps = []
            v, p, err = self._py_post_op_(p)
            while not err:
                ps.append(v)
                v, p, err = self._py_post_op_(p)
            if ps:
                return ['py_qual', e, ps], p, None

        return e, p1, None

    def _py_post_op_(self, p):
        """ = '[' sp py_expr:e sp ']'                -> ['getitem', e]
            | '(' sp py_exprs:es sp ')'              -> ['call', es]
            | '(' sp ')'                             -> ['call', []]
            | '.' ident:i                            -> ['getattr', i]
        """
        start = p
        _, p, err = self._expect(start, '[')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            e, p, err = self._py_expr_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, ']')
        if not err:
            return ['getitem', e], p, None

        _, p, err = self._expect(start, '(')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            es, p, err = self._py_exprs_(p)
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, ')')
        if not err:
            return ['call', es], p, None

        _, p, err = self._expect(start, '(')
        if not err:
            _, p, err = self._sp_(p)
        if not err:
            _, p, err = self._expect(p, ')')
        if not err:
            return ['call', []], p, None

        _, p, err = self._expect(start, '.')
        if not err:
            i, p, err = self._ident_(p)
        if not err:
            return ['getattr', i], p, None

        return None, start, "one of a subscript, a call, or a field deref"

    def _py_prim_(self, p):
        """ = ident
            | literal
            | quote quote                            -> ''
            | digit+:ds                              -> int(''.join(ds))
            | '(' sp py_expr:e sp ')'                -> e
        """
        start = p
        v, p, err = self._ident_(start)
        if not err:
            return v, p, None

        v, p, err = self._literal_(start)
        if not err:
            return v, p, None

        v, p, err = self._quote_(start)
        if not err:
            v, p, err = self._quote_(start)
        if not err:
            return '', p, None

        v, p, err = self._digit_(start)
        if not err:
            ds = []
            while not err:
                ds.append(v)
                v, p, err = self._digit_(p)
            return int(''.join(ds)), p, None

        _, p, err = self._expect(start, '(')
        if not err:
            e, p, err = self._py_expr_(p)
        if not err:
            _, p, err = self._expect(p, ')')
        if not err:
            return e, p, None

        return None, start, ('one of an ident, a literal, an empty string, '
                             'a number, or a parenthesized py_expr ')

    def _py_exprs_(self, p):
        """ = py_expr:e sp ',' sp py_exprs:es     -> [e] + es
            | py_expr:e                           -> [e]
        """
        err = None
        e, p, err = self._py_expr_(p)
        p1 = p

        if not err:
            _, p, err = self._expect(p, ',')
        if not err:
            es, p, err = self._py_exprs_(p)
        if not err:
            return [e] + es, p, None

        return [e], p1, None

    def _post_op_(self, p):
        """ = '?' | '*' | '+' """
        v, p, err = self._expect(p, '?')
        if not err:
            return v, p, None

        v, p, err = self._expect(p, '*')
        if not err:
            return v, p, None

        v, p, err = self._expect(p, '+')
        if not err:
            return v, p, None

        return None, p, "one of '?', '*', '+'"
