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
    def __init__(self, grammar, classname, package, inline_base):
        self.grammar = grammar
        self.classname = classname
        self.package = package
        self.inline_base = inline_base
        self.printer = GrammarPrinter(grammar)
        self.val = None
        self.err = None
        self.indent = 0
        self.shiftwidth = 4
        self.istr = ' ' * self.shiftwidth

    def walk(self):
        self.val = []
        if self.inline_base:
          self._ext(self.inline_base)
        else:
            if self.package:
                from_cls = "%s.compiled_parser_base" % (self.package)
            else:
                from_cls = "compiled_parser_base"
            self._ext('from %s import CompiledParserBase' % from_cls)

        self._ext('',
                  '',
                  'class %s(CompiledParserBase):' % self.classname)

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
        return '\n'.join(v.rstrip() for v in self.val) + '\n', None

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

        self._ext('p = self.pos')
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
                self._ext('self.pos = p')

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

    def _post_(self, node):
        if node[2] == '?':
            self._proc(node[1])
            self._ext('self.err = None')
            return

        self._ext('vs = []')
        if node[2] == '+':
            self._proc(node[1])
            self._ext('if self.err:',
                      self.istr + 'return')
            self._ext('vs.append(self.val)')

        self._ext("while not self.err:")
        self._indent()
        self._proc(node[1])
        self._ext('if not self.err:',
                  self.istr + 'vs.append(self.val)')
        self._dedent()
        self._ext('self.val = vs',
                  'self.err = None')

    def _apply_(self, node):
        self._ext('self._%s_()' % node[1])

    def _action_(self, node):
        self._ext('self.val = %s' % self._proc(node[1]),
                  'self.err = None')

    def _not_(self, node):
        self._ext('p = self.pos')
        self._proc(node[1])
        self._ext('self.pos = p')
        self._ext('if not self.err:',
                  self.istr + ' self.err = "not"',
                  self.istr + ' self.val = None',
                  self.istr + ' return',
                  'self.err = None')


    def _pred_(self, _node):
        self._ext('v = %s' % self._proc(node(1)),
                  'if v:',
                  self.istr + 'self.val = v',
                  self.istr + 'self.err = None',
                  'else:',
                  self.istr + 'self.err = "pred check failed"',
                  self.istr + 'self.val = None')

    def _lit_(self, node):
        self._ext("self._expect('%s')" % node[1].replace("'", "\\'"))

    def _paren_(self, node):
        self._ext('def group():')
        self._indent()
        self._proc(node[1])
        self._dedent()
        self._ext('group()')

    def _py_plus_(self, node):
        return '%s + %s' % (self._proc(node[1]), self._proc(node[2]))

    def _py_qual_(self, node):
        v = self._proc(node[1])
        for p in node[2]:
            v += self._proc(p)
        return v

    def _py_getitem_(self, node):
        return '[' + str(self._proc(node[1])) + ']'

    def _py_getattr_(self, node):
        return '.' + node[1]

    def _py_call_(self, node):
        args = [self._proc(e) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _py_lit_(self, node):
        return "'%s'" % node[1].replace("'", "\\'")

    def _py_var_(self, node):
        return 'v_%s' % node[1]

    def _py_num_(self, node):
        return node[1]

    def _py_arr_(self, node):
        return '[' + ', '.join(self._proc(e) for e in node[1]) + ']'
