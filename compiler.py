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

from grammar_printer import GrammarPrinter


class Compiler(object):
    def __init__(self, grammar, classname):
        self.grammar = grammar
        self.classname = classname
        self.printer = GrammarPrinter(grammar)
        self.val = None
        self.err = None
        self.indent = 0
        self.shiftwidth = 4
        self.istr = ' ' * self.shiftwidth

    def walk(self):
        self.val = []
        self._ext('from new_parser_base import NewParserBase',
                  '',
                  '',
                  'class %s(NewParserBase):' % (self.classname))

        for rule_name, node in self.grammar.rules.items():
            docstring = self.printer._proc(node)
            self._indent()
            self._ext('',
                      'def _%s_(self):' % rule_name)
            self._indent()
            self._ext('""" %s """' % docstring)
            self._proc(node)
            self._dedent()
            self._dedent()

        if self.err:
            return None, self.err
        return '\n'.join(self.val) + '\n', None

    def _nyi(self, label):
        self._ext("# nyi - %s" % label)

    def _indent(self):
        self.indent += 1

    def _dedent(self):
        self.indent -= 1

    def _ext(self, *lines):
        for l in lines:
            self.val.append('%s%s' % (' ' * self.indent * self.shiftwidth, l))

    def _proc(self, node):
        node_type = node[0]
        fn = getattr(self, '_' + node_type + '_', None)
        if not fn:
            import pdb; pdb.set_trace()
        return fn(node)

    def _choice_(self, node):
        if len(node[1]) == 1:
            self._proc(node[1][0])
            return

        for i, choice in enumerate(node[1]):
            self._ext('def choice_%d():' % i)
            self._indent()
            self._proc(choice)
            self._dedent()
            self._ext('choice_%d()' % i)
            if i < len(node[1]) - 1:
                self._ext('if not self.err:',
                          self.istr + 'return',
                          '')

    def _seq_(self, node):
        for i, s in enumerate(node[1]):
            self._proc(s)
            if i < len(node[1]) - 1:
                self._ext('if self.err:',
                          self.istr + 'return')

    def _label_(self, node):
        self._proc(node[1])
        self._ext('if not self.err:',
                  self.istr + 'v_%s = self.val' % node[2])

    def _post_(self, _node):
        return self._nyi('post')

    def _apply_(self, node):
        self._ext('self._%s_()' % node[1])

    def _action_(self, node):
        self._ext('self.val = %s' % self._proc(node[1]),
                  'self.err = None')

    def _not_(self, node):
        self._proc(node[1])
        self._ext('if not self.err:',
                  self.istr + ' self.err = "not"',
                  self.istr + ' self.val = None',
                  self.istr + ' return')

    def _pred_(self, _node):
        return self._nyi('pred')

    def _lit_(self, node):
        self._ext('self._expect("%s")' % node[1])

    def _paren_(self, node):
        return self._proc(node[1])

    def _py_plus_(self, node):
        return "%s + %s" % (self._proc(node[1]), self._proc(node[2]))

    def _py_qual_(self, _node):
        return 'None # NYI - py_qual'

    def _py_lit_(self, node):
        return "'%s'" % node[1]

    def _py_var_(self, node):
        return 'v_%s' % node[1]

    def _py_num_(self, node):
        return node[1]

    def _py_arr_(self, _node):
        return 'None # NYI - py_arr'
