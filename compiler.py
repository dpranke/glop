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

import textwrap

from parser_base import ParserBase
from grammar_printer import GrammarPrinter


class Compiler(ParserBase):
    def __init__(self, grammar, msg, fname, classname):
        super(Compiler, self).__init__(msg, fname, grammar.start)
        self.grammar = grammar
        self.classname = classname
        self.printer = GrammarPrinter(grammar)

    def parse(self, rule=None, start=0):
        prefix = ('from parser_base import ParserBase\n'
                  '\n'
                  '\n'
                  'class %s(ParserBase):\n' % (self.classname))
        p = 4
        v = prefix
        lines = []
        for rule_name, node in self.grammar.rules.items():
            lines = []
            docstring = self.printer._proc(node)
            lines.append('')
            lines.append('def _%s_(self, p):' % rule_name)
            lines.append('    """" = %s""""' % docstring)
            v += self._fmt(4, lines) + self._proc(node, 8, {})
        return v, None

    def _fmt(self, p, lines):
        if lines:
            nlstr = '\n' + ' ' * p
            return ' ' * p + nlstr.join(lines) + '\n'
        return ''

    def _nyi(self, p, label):
        return self._fmt(p, ["v, p, err = (None, p, 'NYI - %s')" % label,
                             "if err:",
                             "    return None, p, err"])

    def _proc(self, node, p, scope):
        node_type = node[0]
        fn = getattr(self, '_' + node_type + '_', None)
        return fn(node, p, scope)

    def _choice_(self, node, p, scope):
        v = ''
        for choice in node[1]:
            v += ' ' * p + self._fmt(p, [self._proc(choice, p, scope)]) + '\n'
        return v

    def _seq_(self, node, p, scope):
        lines = []
        for s in node[1]:
            lines.append(self._proc(s, p, scope))
            lines.append('')
        return self._fmt(p, lines)

    def _label_(self, node, p, scope):
        return self._fmt(p, [self._proc(node[1], p, scope),
                             'if not err:',
                             '    v_%s = v' % node[2]])

    def _post_(self, node, p, scope):
        return self._nyi(p, 'post')

    def _apply_(self, node, p, scope):
        return self._fmt(p, ["v, p, err = self._%s_(p)" % node[1],
                             "if err:",
                             "    return None, p, err"])

    def _action_(self, node, p, scope):
        act = self._proc(node[1], p, scope)
        return self._fmt(p, ["return %s, p, None" % act])

    def _not_(self, node, p, scope):
        return self._nyi(p, 'not')

    def _pred_(self, node, p, scope):
        return self._nyi(p, 'pred')

    def _lit_(self, node, p, _scope):
        return self._fmt(p, ["v, p, err = self._expect('%s')" % node[1],
                             'if err:',
                             '    return None, p, err'])

    def _paren_(self, node, p, scope):
        return self._proc(node[1], p, scope)

    def _py_plus_(self, node, p, scope):
        return "%s + %s" % (self._proc(node[1], p, scope),
                            self._proc(node[2], p, scope))

    def _py_qual_(self, node, p, scope):
        return self._nyi(p, 'py_qual')

    def _py_lit_(self, node, p, scope):
        return "'%s'" % node[1]

    def _py_var_(self, node, p, scope):
        return 'v_%s' % node[1]

    def _py_num_(self, node, p, scope):
        return node[1]

    def _py_arr_(self, node, p, scope):
        return self._nyi(p, 'py_arr')
