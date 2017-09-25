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

from . import string_literal


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
        self.failed = False
        self.errpos = 0
        self._scopes = []
        self._cache = {}

    def parse(self):
        self._%s_()
        if self.failed:
            return None, self._err_str(), self.errpos
        return self.val, None, self.pos
"""

_HELPER_METHODS = """\

    def _err_str(self):
        lineno, colno = self._err_offsets()
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = '"%s"' % self.msg[self.errpos]
        return '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        for i in range(self.errpos):
            if self.msg[i] == '\\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        return lineno, colno

    def _succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos

    def _fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _rewind(self, newpos):
        self._succeed(None, newpos)

    def _bind(self, rule, var):
        rule()
        if not self.failed:
            self._set(var, self.val)

    def _not(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._succeed(None, p)
        else:
            self._rewind(p)
            self._fail()

    def _opt(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._succeed([], p)
        else:
            self._succeed([self.val])

    def _plus(self, rule):
        vs = []
        rule()
        vs.append(self.val)
        if self.failed:
            return
        self._star(rule, vs)

    def _star(self, rule, vs=None):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._rewind(p)
                break
            else:
                vs.append(self.val)
        self._succeed(vs)

    def _seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _choose(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._rewind(p)
        rules[-1]()
"""

_EXPECT = """\

    def _ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._succeed(ch, self.pos + 1)
        else:
            self._fail()

    def _str(self, s, l):
        p = self.pos
        if (p + l <= self.end) and self.msg[p:p + l] == s:
            self._succeed(s, self.pos + l)
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
        def _anything_(self):
            if self.pos < self.end:
                self._succeed(self.msg[self.pos], self.pos + 1)
            else:
                self._fail()
    '''),
    'end': d('''\
        def _end_(self):
            if self.pos == self.end:
                self._succeed(None)
            else:
                self._fail()
    '''),
}


class Compiler(object):
    def __init__(self, grammar, classname, main_wanted):
        self.grammar = grammar
        self.classname = classname
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
        self._method_lines = []

    def compile(self):
        for rule, node in self.grammar.rules.items():
            self._compile(node, rule, top_level=True)

        text = self.header + _PUBLIC_METHODS % (
            self.classname, self.grammar.starting_rule) + _HELPER_METHODS

        if self._expect_needed:
            text += _EXPECT
        if self._range_needed:
            text += _RANGE
        if self._bindings_needed:
            text += _BINDINGS

        for name in sorted(self._builtin_functions_needed):
            text += '\n'
            for line in self.builtin_functions[name]:
                text += '    %s\n' % line

        for rule in self.grammar.rules.keys():
            text += self._method_text(rule, self._methods[rule], memoize=True)
            names = [m for m in self._methods if m.startswith(rule + '_')]
            for name in sorted(names):
                text += self._method_text(name, self._methods[name])

        for name in sorted(self._builtin_rules_needed):
            text += '\n'
            for line in self.builtin_rules[name]:
                text += '    %s\n' % line

        text += self.footer
        return text, None

    def _method_text(self, name, lines, memoize=False):
        text = '\n'
        text += '    def _%s_(self):\n' % name
        if memoize:
            text += '        r = self._cache.get(("%s", self.pos))\n' % name
            text += '        if r is not None:\n'
            text += '            self.val, self.failed, self.pos = r\n'
            text += '            return\n'
            text += '        pos = self.pos\n'
        for line in lines:
            text += '        %s\n' % line
        if memoize:
            text += '        self._cache[("%s", pos)] = (' % name
            text += 'self.val, self.failed, self.pos)\n'
        return text

    def _compile(self, node, rule, sub_type='', index=0, top_level=False):
        assert node
        assert self._method_lines == []
        if node[0] == 'apply':
            if node[1] not in self.grammar.rules:
                self._builtin_rules_needed.add(node[1])
            return 'self._%s_' % node[1]
        elif node[0] == 'lit' and not top_level:
            self._expect_needed = True
            expr = string_literal.encode(node[1])
            if len(node[1]) == 1:
                return 'lambda: self._ch(%s)' % (expr,)
            else:
                return 'lambda: self._str(%s, %d)' % (expr, len(node[1]))
        else:
            if sub_type:
                sub_rule = '%s__%s%d' % (rule, sub_type, index)
            else:
                sub_rule = rule
            fn = getattr(self, '_%s_' % node[0])
            if top_level and node[0] in ('seq', 'choice'):
                fn(sub_rule, node, top_level)
            else:
                fn(sub_rule, node)

            if (not top_level and len(self._method_lines) == 1 and
                    not 'lambda' in self._method_lines[0]):
                r = 'lambda: ' + self._method_lines[0]
                self._method_lines = []
                return r

            assert sub_rule not in self._methods
            self._methods[sub_rule] = self._method_lines
            self._method_lines = []
            return 'self._%s_' % sub_rule

    def _dedent(self):
        self.indent -= 1

    def _eval_rule(self, rule, node):
        fn = getattr(self, '_' + node[0] + '_')
        return fn(rule, node)

    def _ext(self, *lines):
        self._method_lines.extend(lines)

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

    def _chain(self, name, args):
        if len(args) == 1:
            self._ext('self._%s([%s])' % (name, args[0]))
            return
        pfx = 'self._%s([' % name
        line = '%s%s' % (pfx, args[0])
        for arg in args[1:-1]:
            if len(line) + len(arg) < 70:
                line += ', %s' % arg
            else:
                self._ext(line + ',')
                line = ' ' * len(pfx) + arg
        if len(line) + len(args[-1]) < 70:
            self._ext('%s, %s])' % (line, args[-1]))
        else:
            self._ext('%s,' % line)
            self._ext('%s%s])' % (' ' * len(pfx), args[-1]))

    #
    # Handlers for each non-host node in the glop AST follow.
    #

    def _choice_(self, rule, node, top_level=False):
        sub_rules = [self._compile(sub_node, rule, 'c', i, top_level)
                     for i, sub_node in enumerate(node[1])]
        self._chain('choose', sub_rules)

    def _seq_(self, rule, node, top_level=False):
        sub_rules = [self._compile(sub_node, rule, 's', i)
                     for i, sub_node in enumerate(node[1])]
        needs_scope = top_level and self._has_labels(node)
        if needs_scope:
            self._bindings_needed = True
            self._ext("self._push('%s')" % rule)
        self._chain('seq', sub_rules)
        if needs_scope:
            self._ext("self._pop('%s')" % rule)

    def _apply_(self, _rule, node):
        sub_rule = node[1]
        if sub_rule not in self.grammar.rules:
            self._builtin_rules_needed.add(sub_rule)
        self._ext('self._%s_()' % sub_rule)

    def _lit_(self, _rule, node):
        self._expect_needed = True
        expr = string_literal.encode(node[1])
        if len(node[1]) == 1:
            self._ext('self._ch(%s)' % (expr,))
        else:
            self._ext('self._str(%s, %d)' % (expr, len(node[1])))

    def _label_(self, rule, node):
        sub_rule = self._compile(node[1], rule + '_l')
        self._ext('self._bind(%s, %s)' % (sub_rule,
                                          string_literal.encode(node[2])))

    def _action_(self, rule, node):
        self._ext('self._succeed(%s)' % self._eval_rule(rule, node[1]))

    def _empty_(self, _rule, _node):
        return

    def _not_(self, rule, node):
        sub_rule = self._compile(node[1], rule + '_n')
        self._ext('self._not(%s)' % sub_rule)

    def _paren_(self, rule, node):
        sub_rule = self._compile(node[1], rule + '_g')
        self._ext('(%s)()' % sub_rule)

    def _post_(self, rule, node):
        sub_rule = self._compile(node[1], rule + '_p')
        if node[2] == '?':
            self._ext('self._opt(%s)' % sub_rule)
        elif node[2] == '+':
            self._ext('self._plus(%s)' % sub_rule)
        else:
            self._ext('self._star(%s)' % sub_rule)

    def _pred_(self, rule, node):
        self._ext('v = %s' % self._eval_rule(rule, node[1]),
                  'if v:',
                  '    self._succeed(v)',
                  'else:',
                  '    self._fail()')

    def _range_(self, _rule, node):
        self._range_needed = True
        self._ext('self._range(%s, %s)' % (string_literal.encode(node[1][1]),
                                           string_literal.encode(node[2][1])))

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
        return string_literal.encode(node[1])

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
