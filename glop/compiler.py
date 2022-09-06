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
import re
import textwrap

from . import lit
from . import ir


class Compiler:
    def __init__(self, grammar, classname, main_wanted, memoize):
        self.grammar = grammar
        self.classname = classname
        self.main_wanted = main_wanted
        self.memoize = memoize
        self.pending_methods = []
        self.current_method_name = None
        self.submethod_indices = {}

    def compile(self):
        self._rewrite_ast()

        parse_state = self._parse_state()

        if self.main_wanted:
            b = _MAIN_HEADER
        else:
            b = _DEFAULT_HEADER

        starting_method = _rule_to_method_name(self.grammar.starting_rule)
        b += _BASE_CLASS_DEFS.format(
            classname=self.classname,
            starting_method=starting_method,
            parse_state=parse_state)

        methods = self._methods()
        all_method_names = sorted(methods.keys(), key=_split_rule_name)
        all_method_text = ''.join(methods[n] for n in all_method_names)
        b += all_method_text + '\n'

        b += self._needed_builtin_text(methods)

        if self.main_wanted:
            b += _MAIN_FOOTER.format(classname=self.classname)
        else:
            b += _DEFAULT_FOOTER

        return b.rstrip() + '\n'

    def _rewrite_ast(self):
        ast = self.grammar.ast
        ast = ir.rewrite_left_recursion(ast)
        ast = ir.add_builtin_vars(ast)
        if self.memoize:
            ast = ir.memoize(ast)
        self.grammar = ir.Grammar(ast)

    def _parse_state(self):
        ast = self.grammar.ast
        parse_state = ('self.val = None' +
                       '\n' + ' ' * 8 + 'self.pos = 0' +
                       '\n' + ' ' * 8 + 'self.failed = False' +
                       '\n' + ' ' * 8 + 'self.errpos = 0')

        if ir.has_labels(ast):
            parse_state += '\n' + ' ' * 8 + 'self._scopes = []'

        if ir.has_left_recursion(ast):
            parse_state += ('\n' + ' ' * 8 + 'self._blocked = set()' +
                            '\n' + ' ' * 8 + 'self._seeds = {}')

        if self.memoize:
            parse_state += '\n' + ' ' * 8 + 'self._cache = {}'

        return parse_state

    def _methods(self):
        self.pending_methods = []
        for rule in self.grammar.rules:
            method_name = _rule_to_method_name(rule[1])
            node = rule[2]
            self.submethod_indices[method_name] = 0
            self.pending_methods.append([method_name, node])

        methods = {}
        dups = 0
        while self.pending_methods:
            method_name, node = self.pending_methods.pop(0)
            self.current_method_name = method_name
            methods[method_name] = self._gen_method_text(node)
        return methods

    def _gen_method_text(self, node):
        "Generate the text of a method and save it for collating, later."
        ast_method = getattr(self, '_' + node[0])
        method_body = ast_method(node)

        return ('\n'
                '    def %s(self):\n'
                '        %s\n' % (self.current_method_name, method_body)
               )

    def _arg_text(self, args):
        arg_text = ', '.join(args)
        length = len(arg_text)
        sp = ' ' * 12
        if length < 50:
            return arg_text
        if length < 64:
            return ('\n' + sp + arg_text +
                    '\n' + ' ' * 8)
        return ('\n' + sp +
                (',\n' + sp).join(args) +
                '\n' + ' ' * 8)

    def _handle_subrule(self, node):
        method = getattr(self, '_' + node[0])
        return method(node)

    def _handle_subrules(self, node):
        return [self._handle_subrule(subnode) for subnode in node]

    def _gen_expr(self, node):
        "Generate the text for this expression node for use in a method."
        ast_method = getattr(self, '_' + node[0])
        return ast_method(node)

    def _needed_builtin_text(self, methods):
        builtin_list = _BUILTINS.split('\n\n')
        builtins = {}
        for fn in builtin_list:
            m = re.search('def ([a-z_]+)', fn)
            assert m
            builtins[m.group(1)] = '    ' + fn.strip() + '\n'

        needed = set()
        for name, text in methods.items():
            for fn in builtins:
                if fn in text:
                    needed.add(fn)

        for name, text in builtins.items():
            for fn in builtins:
                if 'self.' + fn in text:
                    needed.add(fn)

        b = ''
        for fn in sorted(needed):
            b += builtins[fn] + '\n'
        return b

    #
    # One function for each node type in the AST.
    #

    def _action(self, node):
        val = self._gen_expr(node[1])
        return 'self._h_succeed(' + val + ')'

    def _apply(self, node):
        arg = _rule_to_method_name(node[1])
        return 'self.{}()'.format(arg)

    def _capture(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_capture(lambda: {})'.format(arg)

    def _choice(self, node):
        args = self._handle_subrules(node[1])
        return 'self._h_choice([lambda: {}])'.format(', lambda: '.join(args))

    def _empty(self, node):
        del node
        return 'self._h_succeed(None)'

    def _eq(self, node):
        expr = self._gen_expr(node[1])
        return 'self._h_eq({})'.format(expr)

    def _label(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_label(lambda: {}, {})'.format(arg, lit.encode(node[2]))

    def _leftrec(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_leftrec(lambda: {}, {})'.format(arg,
                       lit.encode(self.current_method_name))

    def _lit(self, node):
        method = '_h_ch' if len(node[1]) == 1 else '_h_str'
        return 'self.' + method + '(' + lit.encode(node[1]) + ')'

    def _ll_arr(self, node):
        args = [str(self._gen_expr(e)) for e in node[1]]
        return '[' + ', '.join(args) + ']'

    def _ll_call(self, node):
        args = [str(self._gen_expr(e)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _ll_dec(self, node):
        return node[1]

    def _ll_getitem(self, node):
        return '[' + self._gen_expr(node[1]) + ']'

    def _ll_hex(self, node):
        return '0x' + node[1]

    def _ll_paren(self, node):
        return self._gen_expr(node[1])

    def _ll_plus(self, node):
        return '{} + {}'.format(self._gen_expr(node[1]),
                                self._gen_expr(node[2]))

    def _ll_qual(self, node):
        v = self._gen_expr(node[1])
        for e in node[2]:
            v += self._gen_expr(e)
        return v

    def _ll_str(self, node):
        return lit.encode(node[1])

    def _ll_var(self, node):
        builtin_fns = (
            'cat', 'is_unicat', 'itou', 'join', 'number', 'xtoi', 'xtou',
            )
        if node[1] in builtin_fns:
            return 'self._f_' + node[1]

        builtin_identifiers = {
          'null': 'None',
          'true': 'True',
          'false': 'False'
        }
        if node[1] in builtin_identifiers:
            return builtin_identifiers[node[1]]

        return 'self._h_get(\'%s\')' % node[1]

    def _memo(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_memo(lambda: {}, {})'.format(arg,
                       lit.encode(self.current_method_name))

    def _not(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_not(lambda: {})'.format(arg)

    def _opt(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_opt(lambda: {})'.format(arg)

    def _paren(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_paren(lambda: {})'.format(arg)

    def _plus(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_plus(lambda: {})'.format(arg)

    def _pos(self, node):
        del node
        return 'self._h_succeed(self.pos)'

    def _pred(self, node):
        expr = self._gen_expr(node[1])
        return 'self._h_pred({})'.format(expr)

    def _range(self, node):
        return 'self._h_range({}, {})'.format(lit.encode(node[1][1]),
                       lit.encode(node[2][1]))

    def _scope(self, node):
        args = self._handle_subrules(node[1])
        return 'self._h_scope([lambda: {}])'.format(', lambda: '.join(args))

    def _seq(self, node):
        args = self._handle_subrules(node[1])
        return 'self._h_seq([lambda: {}])'.format(', lambda: '.join(args))

    def _star(self, node):
        arg = self._handle_subrule(node[1])
        return 'self._h_star(lambda: {})'.format(arg)


def _rule_to_method_name(rule):
    return '_r_' + rule + '_0'


def _base_rule_name(rule):
    return _split_rule_name(rule)[0] + '_0'


def _split_rule_name(rule):
    name, idx = rule.rsplit('_', maxsplit=1)
    return (name, int(idx))


_DEFAULT_HEADER = '''\
# pylint: disable=too-many-lines

'''

_DEFAULT_FOOTER = ''

_MAIN_HEADER = '''\
#!/usr/bin/env python3

import argparse
import json
import os
import sys

# pylint: disable=too-many-lines

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
        {parse_state}

    def parse(self):
        self.{starting_method}()
        if self.failed:
            return self._err()
        return self.val, None, self.pos

    def _err(self):
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
'''

_BUILTINS = '''\
    def _f_cat(self, vals):  # pylint: disable=no-self-use
        return ''.join(vals)

    def _f_is_unicat(self, var, cat):  # pylint: disable=no-self-use
        import unicodedata
        return unicodedata.category(var) == cat

    def _f_itou(self, n):  # pylint: disable=no-self-use
        return chr(n)

    def _f_join(self, var, val):  # pylint: disable=no-self-use
        return var.join(val)

    def _f_number(self, var):  # pylint: disable=no-self-use
        return float(var) if ('.' in var or 'e' in var) else int(var)

    def _f_xtoi(self, s):  # pylint: disable=no-self-use
        return int(s, base=16)

    def _f_xtou(self, s):  # pylint: disable=no-self-use
        return chr(int(s, base=16))

    def _h_label(self, rule, var):
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

    def _h_eq(self, expr):
        if self.msg[self.pos:].startswith(expr):
            self._h_succeed(expr, self.pos + 1)
        else:
            self._h_fail()

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_get(self, var):
        return self._scopes[-1][var]

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
        self._cache[(rule_name, pos)] = (self.val, self.failed, self.pos)

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

    def _h_pred(self, expr):
        if expr == True:  # Must be an actual boolean value, not just truthy.
            return self._h_succeed(True)
        else:
            return self._h_fail()

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, rules):
        self._scopes.append({})
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
        self._scopes[-1][var] = val

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

    def _r_anything_0(self):
        if self.pos < self.end:
            self._h_succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._h_fail()

    def _r_end_0(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()
'''
