# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from parser_base import ParserBase


class Interpreter(ParserBase):
    def __init__(self, grammar, msg, fname):
        super(Interpreter, self).__init__(msg, fname, grammar.start)
        self.grammar = grammar

    def parse(self, rule=None, start=0):
        rule = rule or self.starting_rule
        v, _, err = self._proc(self.grammar.rules[rule], start, {})
        return v, err

    def _proc(self, node, p, scope):
        node_type = node[0]
        fn = getattr(self, '_' + node_type + '_', None)
        return fn(node, p, scope)

    def _choice_(self, node, p, scope):
        start = p
        _, choices = node
        for choice in choices:
            v, p, err = self._proc(choice, start, scope)
            if not err:
                return v, p, None
        return None, p, "no choice matched"

    def _seq_(self, node, p, scope):
        _, exprs = node
        scope = {}
        for expr in exprs:
            v, p, err = self._proc(expr, p, scope)
            if err:
                return None, p, err
        return v, p, None

    def _label_(self, node, p, scope):
        _, expr, label = node
        v, p, _ = self._proc(expr, p, scope)
        scope[label] = v
        return v, p, None

    def _post_(self, node, p, scope):
        _, expr, op = node
        if op == '*':
            vs = []
            err = None
            while not err:
                v, p, err = self._proc(expr, p, scope)
                if not err:
                    vs.append(v)
            return vs, p, None
        if op == '+':
            v, p, err = self._proc(expr, p, scope)
            if err:
                return None, p, err
            vs = []
            while not err:
                v, p, err = self._proc(expr, p, scope)
                if not err:
                    vs.append(v)
            return vs, p, None
        if op == '?':
            v, p, err = self._proc(expr, p, scope)
            if not err:
                return v, p, None
            return None, p, None

    def _apply_(self, node, p, scope):
        _, rule_name = node
        if rule_name in self.builtins:
            fn = getattr(self, '_' + rule_name + '_')
            v, p, err = fn(p)
            if not err:
                return v, p, None
            return None, p, err

        return self._proc(self.grammar.rules[rule_name], p, scope)

    def _action_(self, node, p, scope):
        _, py_expr = node
        return self._proc(py_expr, p, scope)

    def _not_(self, node, p, scope):
        _, expr = node
        start = p
        _, p, err = self._proc(expr, p, scope)
        if err:
            return None, start, None
        return None, start, 'not matched'

    def _pred_(self, node, p, scope):
        _, expr = node
        v, p, _ = self._proc(expr, p, scope)
        if v:
            return v, p, None
        return None, p, 'pred returned False'

    def _lit_(self, node, p, _scope):
        _, lit = node
        return self._expect(p, lit)

    def _paren_(self, node, p, scope):
        return self._proc(node[1], p, scope)

    def _py_plus_(self, node, p, scope):
        _, e1, e2 = node
        v1, p, _ = self._proc(e1, p, scope)
        v2, p, _ = self._proc(e2, p, scope)
        return v1 + v2, p, None

    def _py_qual_(self, node, p, scope):
        _, e, ops = node
        v, p, _ = self._proc(e, p, scope)
        for op in ops:
            if op[0] == 'py_getitem':
                idx, p, _ = self._proc(op[1], p, scope)
                v = v[idx]
            if op[0] == 'py_call':
                args = []
                for expr in op[1]:
                    a, p, _ = self._proc(expr, p, scope)
                    args.append(a)
                v = v(*args)
            if op[0] == 'py_getattr':
                v = getattr(v, op[1])
        return v, p, None

    def _py_lit_(self, node, p, scope):
        _, v = node
        return v, p, scope

    def _py_var_(self, node, p, scope):
        _, v = node
        return scope[v], p, None

    def _py_num_(self, node, p, _scope):
        _, v = node
        return int(v), p, None

    def _py_arr_(self, node, p, scope):
        _, v = node
        return [self._proc(e, p, scope) for e in v], p, None
