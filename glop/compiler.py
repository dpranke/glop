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


_DEFAULT_HEADER = '''\
# pylint: disable=line-too-long

import sys

if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr
    range = xrange
    str = unicode
'''


_DEFAULT_FOOTER = ''


_MAIN_HEADER = '''\
#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import os
import sys

if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr
    range = xrange
    str = unicode

# pylint: disable=line-too-long

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
    obj, err, _ = %s(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1
    print(json.dumps(obj), file=stdout)
    return 0
'''


_MAIN_FOOTER = '''\


if __name__ == '__main__':
    sys.exit(main())
'''


_PUBLIC_METHODS = """\


class %s(object):
    def __init__(self, msg, fname):
        self.msg = str(msg)
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.err = False
        self.errpos = 0
        self._scopes = []

    def parse(self):
        self._%s_()
        if self._failed():
            return None, self._err_str(), self.errpos
        return self.val, None, self.pos
"""

_HELPER_METHODS = """\
    def _err_str(self):
        lineno, colno = self._err_offsets()
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = '"%%s"' %% self.msg[self.errpos]
        return u'%%s:%%d Unexpected %%s at column %%d' %% (
            self.fname, lineno, thing, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        for i in range(self.errpos):
            if self.msg[i] == u'\\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        return lineno, colno

    def _succeed(self, v, newpos):
        self.val = v
        self.err = False
        self.pos = newpos

    def _fail(self):
        self.val = None
        self.err = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _failed(self):
        return self.err

    def _rewind(self, newpos):
        self.val = None
        self.err = False
        self.pos = newpos

    def _not(self, rule):
        p = self.pos
        rule()
        if self._failed():
            self._succeed(None, p)
        else:
            self._fail()
            self._rewind(p)

    def _seq(self, rules):
        for rule in rules:
            rule()
            if self._failed():
                return

    def _choose(self, rules):
        for rule in rules:
            p = self.pos
            rule()
            if not self._failed():
                return
            self._rewind(p)
"""

_EXPECT = """\

    def _expect(self, expr, l):
        p = self.pos
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self._succeed(expr, self.pos + l)
        else:
            self._fail()
"""

_RANGE = """\

    def _range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._succeed(self.msg[p], self.pos + 1)
        else:
            self._fail()
"""

_BINDINGS = """\

    def _push(self, name):
        self._scopes.append((name, {}))

    def _pop(self, name):
        actual_name, _ = self._scopes.pop()
        assert name == actual_name

    def _get(self, var):
        return self._scopes[-1][1][var]

    def _set(self, var, val):
        self._scopes[-1][1][var] = val
"""


def d(s):
    return textwrap.dedent(s).splitlines()


_DEFAULT_FUNCTIONS = {
    'is_unicat': d('''\
        def _is_unicat(self, var, cat):
            import unicodedata
            return unicodedata.category(var) == cat
        '''),
    'itou': d('''\
        def _itou(self, n):
            return chr(n)
        '''),
    'join': d('''\
        def _join(self, s, vs):
            return s.join(vs)
        '''),
    'utoi': d('''\
        def _atoi(self, s):
            return int(s)
        '''),
    'xtoi': d('''\
        def _xtoi(self, s):
            return int(s, base=16)
        '''),
    'xtou': d('''\
        def _xtou(self, s):
            return chr(int(s, base=16))
        '''),
}


_DEFAULT_IDENTIFIERS = {
    'null': 'None',
    'true': 'True',
    'false': 'False',
}


_DEFAULT_RULES = {
    'anything': d('''\
        if self.pos < self.end:
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()
    '''),
    'end': d('''\
        if self.pos == self.end:
            self._succeed(None, self.pos)
        else:
            self._fail()
    '''),
    'letter': d('''\
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()
    '''),
    'digit': d('''\
        if self.pos < self.end and self.msg[self.pos].isdigit():
            self._succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._fail()
    '''),
}


class Compiler(object):
    def __init__(self, grammar, classname, main_wanted):
        self.grammar = grammar
        self.classname = classname
        self.starting_rule = grammar.rules.keys()[0]
        self.val = None
        self.err = False
        self.indent = 0
        if main_wanted:
            self.header = _MAIN_HEADER % self.classname
            self.footer = _MAIN_FOOTER
        else:
            self.header = _DEFAULT_HEADER
            self.footer = _DEFAULT_FOOTER
        self.builtin_functions = _DEFAULT_FUNCTIONS
        self.builtin_identifiers = _DEFAULT_IDENTIFIERS
        self.builtin_rules = _DEFAULT_RULES

        self._builtin_functions_needed = set()
        self._builtin_rules_needed = set()
        self._bindings_needed = False
        self._expect_needed = False
        self._range_needed = False
        self._methods = {}

    def compile(self):
        for rule, node in self.grammar.rules.items():
            assert node[0] == 'choice'
            self._choice_(rule, node, top_level=True)
            if not rule in self._methods:
                self._methods[rule] = self.val
            self.val = []

        text = self.header + _PUBLIC_METHODS % (
            self.classname, self.starting_rule)

        for rule in self.grammar.rules.keys():
            text += self._method_text(rule, self._methods[rule])
            names = [m for m in self._methods if m.startswith(rule + '_')]
            for name in sorted(names):
                text += self._method_text(name, self._methods[name])

        for name in sorted(self._builtin_rules_needed):
            text += self._method_text(name, self.builtin_rules[name])

        for name in sorted(self._builtin_functions_needed):
            text += self._method_text(name, self.builtin_functions[name])

        if self._expect_needed:
            text += _EXPECT
        if self._range_needed:
            text += _RANGE
        if self._bindings_needed:
            text += _BINDINGS

        return text + _HELPER_METHODS + self.footer, None

    def _method_text(self, name, lines):
        text = '\n'
        text += '    def _%s_(self):\n' % name
        for line in lines:
            text += '        %s\n' % line
        return text

    def _compile_rule(self, rule, node, top_level=False):
        self.val = []
        if rule not in self._methods:
            if top_level:
                assert node[0] == 'seq'
                self._seq_(rule, node, top_level)
            else:
                fn = getattr(self, '_' + node[0] + '_')
                fn(rule, node)
        if rule not in self._methods:
            self._methods[rule] = self.val
            self.val = []

    def _compile_sub_rule(self, rule, node, sub_type, index, top_level=False):
        if node[0] == 'apply':
            if node[1] not in self.grammar.rules:
                self._builtin_rules_needed.add(node[1])
            return 'self._%s_' % node[1]
        elif node[0] == 'lit':
            self._expect_needed = True
            expr = repr(node[1])
            return 'lambda : self._expect(%s, %d)' % (expr, len(node[1]))
        else:
            self._compile_rule('%s__%s%d' % (rule, sub_type, index), node,
                               top_level)
            return 'self._%s__%s%d' % (rule, sub_type, index)

    def _dedent(self):
        self.indent -= 1

    def _esc(self, val):
        return unicode(repr(unicode(val)))

    def _eval_rule(self, rule, node):
        fn = getattr(self, '_' + node[0] + '_')
        return fn(rule, node)

    def _ext(self, *lines):
        self.val.extend(lines)

    def _has_labels(self, node):
        if node and node[0] == 'label':
            return True
        for n in node:
            if isinstance(n, list) and self._has_labels(n):
                return True
        return False

    def _indent(self):
        self.indent += 1

    def _rule_can_fail(self, node):
        if node[0] == 'post':
            if node[2] in ('?', '*'):
                return False
            return True
        if node[0] == 'label':
            return self._rule_can_fail(node[1])
        if node[0] in ('choice', 'seq'):
            if any(self._rule_can_fail(n) for n in node[1]):
                return True
            return False
        if node[0] == 'apply':
            if node[1] in self.grammar.rules:
              return self._rule_can_fail(self.grammar.rules[node[1]])
            # This must be a builtin, and all of the builtin rules can fail.
            return True
        return True

    #
    # Handlers for each non-host node in the glop AST follow.
    #

    def _action_(self, rule, node):
        self._ext('self._succeed(%s, self.pos)' %
                  self._eval_rule(rule, node[1]))

    def _apply_(self, _rule, node):
        if node[1] not in self.grammar.rules:
            self._builtin_rules_needed.add(node[1])
        self._ext('self._%s_()' % node[1])

    def _choice_(self, rule, node, top_level=False):
        sub_rules = []
        if len(node[1]) == 1:
            self._compile_rule(rule, node[1][0], top_level)
            return

        for i, s in enumerate(node[1]):
            sub_rules.append(self._compile_sub_rule(rule, s, 'c', i, top_level))

        self._ext('self._choose([%s,' % sub_rules[0])
        for sub_rule in sub_rules[1:-1]:
            self._ext('              %s,' % sub_rule)
        self._ext('              %s])' % sub_rules[-1])

    def _empty_(self, _rule, _node):
        return

    def _label_(self, rule, node):
        self._compile_rule('%s_l' % rule, node[1])
        self._ext('self._%s_l()' % rule,
                  'if not self.err:',
                  '    self._set(\'%s\', self.val)' % node[2])

    def _lit_(self, _rule, node):
        self._expect_needed = True
        expr = repr(node[1])
        self._ext('self._expect(%s, %d)' % (expr, len(node[1])))

    def _not_(self, rule, node):
        sub_rule = self._compile_sub_rule(rule, node[1], 'n', 1)
        self._ext('self._not(self._%s_n)' % rule)

    def _paren_(self, rule, node):
        self._compile_rule(rule + '_g', node[1])
        self._ext('self._%s_g()' % rule)

    def _post_(self, rule, node):
        self._compile_rule(rule + '_p', node[1])
        if node[2] == '?':
            self._ext('p = self.pos',
                      'self._%s_p()' % rule,
                      'if self._failed():',
                      '    self._succeed([], p)',
                      'else:',
                      '    self._succeed([self.val], self.pos)')
            return

        self._ext('vs = []')
        if node[2] == '+':
            self._ext(rule + '_p()',
                      'if not self._failed():',
                      '    vs.append(self.val)')
        self._ext('while not self._failed():',
                  '    p = self.pos',
                  '    ' + rule + '_p()',
                  '    if self._failed():',
                  '        self._rewind(p)',
                  '    else:',
                  '        vs.append(self.val)',
                  '    self._succeed(vs, self.pos)')

    def _pred_(self, rule, node):
        self._ext('v = %s' % self._eval_rule(rule, node[1]),
                  'if v:',
                  '    self._succeed(v, self.pos)',
                  'else:',
                  '    self._fail()')

    def _range_(self, _rule, node):
        self._range_needed = True
        self._ext('self._range(%s, %s)' % (repr(node[1][1]), repr(node[2][1])))

    def _seq_(self, rule, node, top_level=False):
        if len(node[1]) == 1:
            # A sequence of length one doesn't need a scope.
            self._compile_rule(rule, node[1][0])
            return
        sub_rules = []
        for i, s in enumerate(node[1]):
            sub_rules.append(self._compile_sub_rule(rule, s, 's', i))
        needs_scope = top_level and self._has_labels(node)
        if needs_scope:
            self._bindings_needed = True
            self._ext("self._push('%s')" % rule)
        self._ext('self._seq([%s,' % sub_rules[0])
        for sub_rule in sub_rules[1:-1]:
            self._ext('           %s,' % sub_rule)
        self._ext('           %s])' % sub_rules[-1])
        if needs_scope:
            self._ext("self._pop('%s')" % rule)

    #
    # Handlers for the host nodes in the AST
    #

    def _ll_arr_(self, rule, node):
        return '[' + ', '.join(self._eval_rule(rule, e) for e in node[1]) + ']'

    def _ll_call_(self, rule, node):
        args = [str(self._eval_rule(rule, e)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _ll_getattr_(self, _rule, node):
        return '.' + node[1]

    def _ll_getitem_(self, rule, node):
        return '[' + str(self._eval_rule(rule, node[1])) + ']'

    def _ll_lit_(self, _rule, node):
        return repr(str(node[1]))

    def _ll_num_(self, _rule, node):
        return node[1]

    def _ll_plus_(self, rule, node):
        return '%s + %s' % (self._eval_rule(rule, node[1]),
                            self._eval_rule(rule, node[2]))

    def _ll_qual_(self, rule, node):
        v = self._eval_rule(rule, node[1])
        for p in node[2]:
            v += self._eval_rule(rule, p)
        return v

    def _ll_var_(self, _rule, node):
        if node[1] in self.builtin_functions:
            self._builtin_functions_needed.add(node[1])
            return 'self._%s' % node[1]
        if node[1] in self.builtin_identifiers:
            return self.builtin_identifiers[node[1]]
        return 'self._get(\'%s\')' % node[1]

