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
        lines = ['from parser_base import ParserBase',
                 '',
                 '',
                 'class %s(ParserBase):' % (self.classname),
                 ]
        start += 4
        for rule_name, node in self.grammar.rules.items():
            lines.append('')
            lines.append('%sdef _%s_(self, p):' % (' ' * start, rule_name))
            docstring = self.printer._proc(node)
            lines.append('%s    """" = %s""""' % (' ' * start, docstring))
            lines.extend(self._proc(node, start + 4, {}))

        return '\n'.join(lines) + '\n', None

    def _proc(self, node, p, scope):
        node_type = node[0]
        fn = getattr(self, '_' + node_type + '_', None)
        return fn(node, p, scope)

    def _choice_(self, node, p, scope):
        lines = []
        for c in node[1]:
            lines.extend(self._proc(c, p, scope))
        return ['%s%s' % (' ' * p, l) for l in lines]

    def _seq_(self, node, p, scope):
        lines = []
        for s in node[1]:
            lines.extend([
                'v, p, err = %s' % self._proc(s, p, scope),
                'if err:',
                '    return None, p, err',
                ])
        lines.extend(['return v, p, None'])
        return lines

    def _label_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - label')"]

    def _post_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - post')"]

    def _apply_(self, node, p, scope):
        return "self._%s_(p)" % node[1]

    def _action_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - action')"]

    def _not_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - not')"]

    def _pred_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - pred')"]

    def _lit_(self, node, p, _scope):
        return "self._expect(p, '%s')" % node[1]

    def _paren_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - paren')"]

    def _py_plus_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - py_plus')"]

    def _py_qual_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - py_qual')"]

    def _py_lit_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - py_lit')"]

    def _py_var_(self, node, p, scope):
        return ["(None, p, 'NotImplemented - py_var')"]

    def _py_num_(self, node, p, _scope):
        return ["(None, p, 'NotImplemented - py_num')"]
