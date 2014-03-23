from parser import Parser


class GrammarInterp(Parser):
    def __init__(self, grammar, msg, fname):
        super(GrammarInterp, self).__init__(msg, fname, grammar.start)
        self.grammar = grammar

    def parse(self, rule=None, start=0):
        rule = rule or self.starting_rule
        return self._proc(rule, start, {})

    def _proc(self, node, p, scope):
        node_type = node[0]
        fn = getattr(self, '_' + node_type + '_', None)
        if fn:
            return fn(node, p, scope)
        return None, pos, 'unexpected node type "%s"' % node_type

    def _choice_(self, node, p, scope):
        start = p
        _, choices = node
        for choice in choices:
            v, p, err = self._proc(choice, start, scope)
            if not err:
                return v, p, None
        return None, False

    def _seq_(self, node, p, scope):
        _, exprs = node
        scope = {}
        for expr in exprs:
            v, p, err = self._proc(expr, p, scope)
            if not err:
                return v, p, err

    def _label_(self, node, p, scope):
        _, expr, label = node
        v, p, err = self._proc(expr, p, scope)
        if err:
            return None, p, err
        scope[label] = v
        return v, p, None

    def _post_(self, node, p, scope):
        _, expr, op = node
        if op == '*':
            vs = []
            while not err:
                v, p, err = self._proc(expr, p, scope)
                if not err:
                    vs.append(v)
            return vs, p, None
        if op == '+':
            v, p, err = self._proc(expr, p, scope)
            if err:
                return None, p, err
            while not err:
                v, p, err = self._proc(expr, p, scope)
                if not err:
                    vs.append(v)
            return vs, p, None
        if op == '?':
            start = p
            v, p, err = self._proc(expr, p, scope)
            if not err:
                return v, p, None
            return None, p, None

    def _apply_(self, node, p, scope):
        return self._proc(self.grammar[node[1]], p, scope)

    def _action_(self, node, p, scope):
        _, py_expr = node
        return self._proc(py_expr, p, scope)

    def _not_(self, node, p, scope):
        _, expr = node
        start = p
        v, p, err = self._proc(expr, p, scope)
        if err:
            return None, start, None
        return None, start, 'not matched'

    def _pred_(self, node, p, scope):
        _, expr = node
        v, p, err = self._proc(expr, p, scope)
        if v:
            return v, p, None
        return None, p, 'pred returned False'

    def _lit_(self, node, p, scope):
        _, lit = node
        return self._expect(p, lit)

    def _py_plus_(self, node, p, scope):
        _, e1, e2 = node
        v1 = self._proc(e1, p, scope)
        v2 = self._proc(e2, p, scope)
        return v1 + v2, p, None

    def _py_qual_(self, node, p, scope):
        _, e, ops = node
        v = self._proc(e, p, scope)
        for op in ops:
            if op[0] == 'py_getitem':
                idx = self._proc(op[1], p, scope)
                v = v[idx]
            if op[0] == 'py_call':
                args = []
                for expr in op[1]:
                    args.append(self._proc(expr, p, scope))
                v = v(*args)
            if op[0] == 'py_getattr':
                fld = self._proc(op[1], p, scope)
                v = getattr(v, fld)
        return v, p, None

    def _py_prim_(self, node, p, scope):
        _, sub_node = node
        if node[0] == 'py_var':
            return scope[node[1]], p, None
        if node[0] == 'py_num':
            return node[1]
        if node[0] == 'literal':
            return node[1]
