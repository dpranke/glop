# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
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


DEFAULT_HEADER = '''\
#!/usr/bin/env python

# pylint: disable=line-too-long

from __future__ import print_function

import argparse
import json
import os
import sys


def main(argv=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout,
         stderr=sys.stderr, exists=os.path.exists, opener=open):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='?')
    args = arg_parser.parse_args(argv)

    if not args.file or args.file[1] == '-':
        fname = '<stdin>'
        fp = stdin
    elif not exists(args.file):
        print('Error: file "%%s" not found.' %% args.file, file=stderr)
        return 1
    else:
        fname = args.file
        fp = opener(fname)

    msg = fp.read()
    obj, err = %s(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1
    print(json.dumps(obj), file=stdout)
    return 0


'''


DEFAULT_FOOTER = '''\

if __name__ == '__main__':
    sys.exit(main())
'''

_BASE_METHODS = """\
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
            if self.msg[i] == '\\n':
                lineno += 1
                colno = 1
                begpos = i
            else:
                colno += 1
            i += 1
        return lineno, colno, begpos

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
                self.errset.add(repr(expr))
                self.errpos = self.pos
        return
"""


def d(s):
    return '    ' + '\n    '.join(textwrap.dedent(s).splitlines())


BUILTIN_FUNCTIONS = {
    'atoi': d('''\
        def _atoi(self, s):
            if s.startswith('0x'):
                return int(s, base=16)
            return int(s)
        '''),
    'itoa': d('''\
        def _itoa(self, n):
            return str(n)
        '''),
    'join': d('''\
        def _join(self, s, vs):
            return s.join(vs)
        '''),
}


BUILTIN_RULES = {
    'anything': d('''\
        def _anything_(self):
            if self.pos < self.end:
                self.val = self.msg[self.pos]
                self.err = None
                self.pos += 1
            else:
                self.val = None
                self.err = "anything"
        '''),
    'end': d('''\
        def _end_(self):
            if self.pos == self.end:
                self.val = None
                self.err = None
            else:
                self.val = None
                self.err = "the end"
            return
        '''),
    'letter': d('''\
        def _letter_(self):
            if self.pos < self.end and self.msg[self.pos].isalpha():
                self.val = self.msg[self.pos]
                self.err = None
                self.pos += 1
            else:
                self.val = None
                self.err = "a letter"
            return
    '''),
    'digit': d('''\
        def _digit_(self):
            if self.pos < self.end and self.msg[self.pos].isdigit():
                self.val = self.msg[self.pos]
                self.err = None
                self.pos += 1
            else:
                self.val = None
                self.err = "a digit"
            return
    '''),
}

class Compiler(object):
    def __init__(self, grammar):
        self.grammar = grammar
        self.starting_rule = grammar.rules.keys()[0]
        self.val = None
        self.err = None
        self.indent = 0
        self.shiftwidth = 4
        self.istr = ' ' * self.shiftwidth
        self.builtin_functions_needed = set()
        self.builtin_rules_needed = set()

    def compile(self, classname, header=None, footer=None):
        self.val = []
        self._ext('class %s(object):' % classname,
                  '    def __init__(self, msg, fname, starting_rule=\'%s\', '
                  'starting_pos=0):' % self.starting_rule,
                  _BASE_METHODS)

        for rule_name, node in self.grammar.rules.items():
            self._indent()
            self._ext('',
                      'def _%s_(self):' % rule_name)
            self._indent()
            self._proc(node)
            self._dedent()
            self._dedent()

        self._ext('')
        for name in self.builtin_rules_needed:
            self._ext(BUILTIN_RULES[name])

        self._ext('')
        for name in self.builtin_functions_needed:
            self._ext(BUILTIN_FUNCTIONS[name])

        if self.err:
            return None, self.err

        if header is None:
            header = DEFAULT_HEADER % classname
        if footer is None:
            footer = DEFAULT_FOOTER

        cls_text = '\n'.join(v.rstrip() for v in self.val) + '\n'
        return header + cls_text + footer, None

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
                self._ext('self.err = False')
                self._ext('self.pos = p')

    def _empty_(self, node):
        return

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
            self._ext('p = self.pos')
            self._proc(node[1])
            self._ext('if self.err:',
                      '    self.val = []',
                      '    self.err = None',
                      '    self.pos = p')
            self._ext('else:')
            self._ext('    self.val = [self.val]')
            return

        self._ext('vs = []')
        if node[2] == '+':
            self._proc(node[1])
            self._ext('if self.err:',
                      self.istr + 'return')
            self._ext('vs.append(self.val)')

        self._ext('while not self.err:')
        self._indent()
        self._ext('p = self.pos')
        self._proc(node[1])
        self._ext('if not self.err:',
                  self.istr + 'vs.append(self.val)',
                  'else:',
                  self.istr + 'self.pos = p')
        self._dedent()
        self._ext('self.val = vs',
                  'self.err = None')

    def _apply_(self, node):
        if node[1] in BUILTIN_RULES:
            self.builtin_rules_needed.add(node[1])
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


    def _pred_(self, node):
        self._ext('v = %s' % (self._proc(node[1]),),
                  'if v:',
                  self.istr + 'self.val = v',
                  self.istr + 'self.err = None',
                  'else:',
                  self.istr + 'self.err = "pred check failed"',
                  self.istr + 'self.val = None')

    def _lit_(self, node):
        self._ext("self._expect('%s')" % node[1])

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
        args = [str(self._proc(e)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _py_lit_(self, node):
        return repr(node[1])

    def _py_var_(self, node):
        if node[1] in BUILTIN_FUNCTIONS:
            self.builtin_functions_needed.add(node[1])
            return 'self._%s' % node[1]
        if node[1] == 'true':
            return 'True'
        if node[1] == 'false':
            return 'False'
        if node[1] == 'null':
            return 'None'
        return 'v_%s' % node[1]

    def _py_num_(self, node):
        return node[1]

    def _py_arr_(self, node):
        return '[' + ', '.join(self._proc(e) for e in node[1]) + ']'
