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

import pprint
import textwrap

from . import lit
from . import ir

class Compiler:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, grammar, classname, main_wanted, memoize):
        self.grammar = grammar
        self.classname = classname
        self.shiftwidth = 4
        self.main_wanted = main_wanted
        self.memoize = memoize
        self.methods = {}
        self.method_name = None
        self.rules = []
        self.rule_name = None
        self.index = 0

    def _dedent(self, s, tabs):
        s = textwrap.dedent(s)
        s = textwrap.indent(s, ' ' * tabs * self.shiftwidth)
        return s

    def compile(self):
        ast = self.grammar.ast
        ast = ir.rewrite_left_recursion(ast)
        ast = ir.add_builtin_vars(ast)
        self.grammar = ir.Grammar(ast)
        self.rules = self.grammar.rules.copy()

        if self.main_wanted:
            b = self._dedent(_MAIN_HEADER, 0)
        else:
            b = self._dedent(_DEFAULT_HEADER, 0)

        b += "\n'''\n" + pprint.pformat(self.grammar.rules) + "\n'''\n\n\n"

        b += self._dedent(_BASE_CLASS_DEFS.format(
            classname=self.classname,
            starting_rule=self.grammar.starting_rule), 0)

        i = 0
        while self.rules:
            i += 1
            rule = self.rules.pop()
            if rule[1].startswith('_s_'):
                self.rule_name = rule[1]
            else:
                self.subindex = 0
                self.base_rule = rule[1]
                self.rule_name = '_r_' + rule[1]
            self.gen(node=rule[2])

        all_method_names = sorted(self.methods.keys())
        all_method_text = ''.join(self.methods[n] for n in all_method_names)
        b += all_method_text

        b += '\n' + _BUILTINS

        if self.main_wanted:
            b += _MAIN_FOOTER.format(classname=self.classname)
        else:
            b += _DEFAULT_FOOTER

        return b

    #
    # Generate the text of a method and save it for collating, later.
    #
    def gen(self, node):
        try:
            ast_method = getattr(self, '_' + node[0])
            self.methods[self.rule_name] = ast_method(node)
        except AttributeError:
            pass

    #
    # one function for each node type in the AST.
    #

    def _apply(self, node):
        rule_to_apply = node[1]
        if not rule_to_apply.startswith('_s_'):
            rule_to_apply = '_r_' + rule_to_apply
        return self._dedent('''
            def {method_name}(self):
                self.{rule_to_apply}()
            '''.format(method_name=self.rule_name,
                       rule_to_apply=rule_to_apply),
            1)

    def _choice(self, node):
        args = []
        for i, subrule in enumerate(node[1]):
            self.subindex += 1
            subrule_name = '_s_{}_{}'.format(self.base_rule, self.subindex)
            new_rule = ['rule', subrule_name, subrule]
            self.rules.insert(i, new_rule)
            args.append('self.' + subrule_name)

        return self._dedent('''
            def {}(self):
                self._h_choice([{}])
            '''.format(self.rule_name, ', '.join(args)),
            1)

    def _lit(self, node):
        return self._dedent('''
            def {method_name}(self):
                self._h_str({s})
            '''.format(method_name=self.rule_name, s = lit.encode(node[1])),
            1)

    def _not(self, node):
        raise NotImplementedError

    def _opt(self, node):
        raise NotImplementedError

    def _paren(self, node):
        args = []
        subrule = node[1]
        self.subindex += 1
        subrule_name = '_s_{}_{}'.format(self.base_rule, self.subindex)
        new_rule = ['rule', subrule_name, subrule]
        self.rules.insert(0, new_rule)
        args.append('self.' + subrule_name)

        return self._dedent('''
            def {}(self):
                self._h_paren({})
            '''.format(self.rule_name, ', '.join(args)),
            1)

    def _plus(self, node):
        raise NotImplementedError

    def _range(self, node):
        raise NotImplementedError

    def _seq(self, node):
        args = []
        for i, subrule in enumerate(node[1]):
            self.subindex += 1
            subrule_name = '_s_{}_{}'.format(self.base_rule, self.subindex)
            new_rule = ['rule', subrule_name, subrule]
            self.rules.insert(i, new_rule)
            args.append('self.' + subrule_name)
        return self._dedent('''
            def {}(self):
                self._h_seq([{}])
            '''.format(self.rule_name, ', '.join(args)),
            1)

    def _star(self, node):
        raise NotImplementedError



_DEFAULT_HEADER = ''

_DEFAULT_FOOTER = ''

_MAIN_HEADER = '''\
#!/usr/bin/env python3

import argparse
import json
import os
import sys

'''

_MAIN_FOOTER = '''\


def main(argv,
         stdin=sys.stdin,
         stdout=sys.stdout,
         stderr=sys.stderr,
         exists=os.path.exists,
         opener=open):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='?')
    args = arg_parser.parse_args(argv)

    if not args.file or args.file[0] == '-':
        fname = '<stdin>'
        fp = stdin
    elif not exists(args.file):
        print('Error: file "%s" not found.' % args.file,
              file=stderr)
        return 1
    else:
        fname = args.file
        fp = opener(fname)

    msg = fp.read()
    obj, err, _ = {classname}(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1

    print(json.dumps(obj, ensure_ascii=False), file=stdout)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
'''

_BASE_CLASS_DEFS = '''\
class {classname}:
    def __init__(self, msg, fname):
        self.msg = msg
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0
        self._scopes = []
        self._seeds = {{}}
        self._blocked = set()
        self._cache = {{}}

    def parse(self):
        self._r_{starting_rule}()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos
'''

_BUILTINS = '''\
    def _h_bind(self, rule, var):
        rule()
        if not self.failed:
            self._h_set(var, self.val)

    def _h_capture(self, rule):
        start = self.pos
        rule()
        if not self.failed:
            self._h_succeed(self.msg[start:self.pos], self.pos)

    def _h_ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._h_succeed(ch, p+1)
        else:
            self._h_fail()

    def _h_choice(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._h_rewind(p)
        rules[-1]()

    def _h_eq(self, var):
        self._h_str(var)

    def _h_err(self):
        lineno = 1
        colno = 1
        for ch in self.msg[:self.errpos]:
            if ch == '\\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = repr(self.msg[self.errpos]).replace(
               "'", "\\"")
        err_str = '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)
        return None, err_str, self.errpos

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_get(self, var):
        return self._scopes[-1][1][var]

    def _h_leftrec(self, rule, rule_name):
        pos = self.pos
        key = (rule_name, pos)
        seed = self._seeds.get(key)
        if seed:
            self.val, self.failed, self.pos = seed
            return
        if rule_name in self._blocked:
            self._h_fail()
        current = (None, True, self.pos)
        self._seeds[key] = current
        self._blocked.add(rule_name)
        while True:
            rule()
            if self.pos > current[2]:
                current = (self.val, self.failed, self.pos)
                self._seeds[key] = current
                self.pos = pos
            else:
                del self._seeds[key]
                self._seeds.pop(rule_name, pos)
                if rule_name in self._blocked:
                    self._blocked.remove(rule_name)
                self.val, self.failed, self.pos = current
                return

    def _h_memo(self, rule, rule_name):
        r = self._cache.get((rule_name, self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        rule()
        self._cache[(rule_name, pos)] = (self.val, self.failed,
                                         self.pos)

    def _h_not(self, rule):
        p = self.pos
        errpos = self.errpos
        rule()
        if self.failed:
            self._h_succeed(None, p)
        else:
            self._h_rewind(p)
            self.errpos = errpos
            self._h_fail()

    def _h_opt(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._h_succeed([], p)
        else:
            self._h_succeed([self.val])

    def _h_paren(self, rule):  # pylint: disable=no-self-use
        rule()

    def _h_plus(self, rule):
        rule()
        if self.failed:
            return
        self._h_star(rule, [self.val])

    def _h_pos(self):
        self._h_succeed(self.pos)

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, name, rules):
        self._scopes.append((name, {{}}))
        for rule in rules:
            rule()
            if self.failed:
                self._scopes.pop()
                return
        self._scopes.pop()

    def _h_seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _h_set(self, var, val):
        self._scopes[-1][1][var] = val

    def _h_star(self, rule, vs=None):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._h_rewind(p)
                break
            vs.append(self.val)
        self._h_succeed(vs)

    def _h_str(self, s):
        i = 0
        while not self.failed and i < len(s):
            self._h_ch(s[i])
            i += 1

    def _h_succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos

    def _r_anything(self):
        if self.pos < self.end:
            self._h_succeed(self.msg[self.pos, self.pos + 1])
        else:
            self._h_fail()

    def _r_end(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()
'''
