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
        self.rules = []
        self.current_rule_name = None
        self.subrule_indices = {}

    def compile(self):
        ast = self.grammar.ast
        ast = ir.rewrite_left_recursion(ast)
        ast = ir.add_builtin_vars(ast)

        parse_state = ('self.val = None' +
                       '\n' + ' ' * 8 + 'self.pos = 0' +
                       '\n' + ' ' * 8 + 'self.failed = False' +
                       '\n' + ' ' * 8 + 'self.errpos = 0')

        if ir.has_labels(ast):
            parse_state += '\n' + ' ' * 8 + 'self._scopes = []'

        if ir.check_for_left_recursion(ast) != set():
            parse_state += ('\n' + ' ' * 8 + 'self._blocked = set()' +
                            '\n' + ' ' * 8 + 'self._seeds = {}')

        if self.memoize:
            ast = ir.memoize(ast)
            parse_state += '\n' + ' ' * 8 + 'self._cache = {}'

        self.grammar = ir.Grammar(ast)

        if self.main_wanted:
            b = _MAIN_HEADER
        else:
            b = _DEFAULT_HEADER

        b += _BASE_CLASS_DEFS.format(
            classname=self.classname,
            starting_rule=self._rule_to_method_name(
                self.grammar.starting_rule),
            parse_state=parse_state)

        self.rules = []
        self.subrule_indices = {}
        self.current_rule = None

        for rule in self.grammar.rules:
            name = self._rule_to_method_name(rule[1])
            node = rule[2].copy()
            self.subrule_indices[name] = 0
            self.rules.append([name, node])

        # b += '\n' + _BUILTINS
        builtin_list = _BUILTINS.split('\n\n')
        builtins = {}
        for fn in builtin_list:
            m = re.search('def ([a-z_]+)', fn)
            assert m
            builtins[m.group(1)] = '    ' + fn.strip() + '\n'

        methods = {}
        while self.rules:
            self.current_rule_name, node = self.rules.pop(0)
            methods[self.current_rule_name] = self._gen_rule_text(node)

        all_method_names = sorted(methods.keys(), key=self._split_rule_name)

        all_method_text = ''.join(methods[n] for n in all_method_names)
        b += all_method_text + '\n'

        needed = set()
        for name, text in methods.items():
            for fn in builtins:
                if fn in text:
                    needed.add(fn)

        for name, text in builtins.items():
            for fn in builtins:
                if 'self.' + fn in text:
                    needed.add(fn)

        for fn in sorted(needed):
            b += builtins[fn] + '\n'

        if self.main_wanted:
            b += _MAIN_FOOTER.format(classname=self.classname)
        else:
            b += _DEFAULT_FOOTER

        return b.strip() + '\n'

    def _dedent(self, s):
        s = textwrap.dedent(s)
        s = textwrap.indent(s, ' ' * 4)
        return s

    def _rule_to_method_name(self, rule):
        return '_r_' + rule + '_0'

    def _base_rule_name(self, rule):
        return self._split_rule_name(rule)[0] + '_0'

    def _split_rule_name(self, rule):
        name, idx = rule.rsplit('_', maxsplit=1)
        return (name, int(idx))

    def _arg_text(self, starting_offset, args):
        arg_text = ', '.join(args)
        if len(arg_text) + starting_offset > 60:
            sp = ' ' * 20
            arg_text = ('\n' + sp +
                        (',\n' + sp).join(args) +
                        '\n' + ' '*16)
        return arg_text

    def _handle_subrule(self, node, starting_offset):
        if node[0] == 'apply':
            arg = 'self.' + self._rule_to_method_name(node[1])
        elif node[0] == 'lit':
            arg = 'lambda: self._h_str(' + lit.encode(node[1]) + ')'
        else:
            subrule_name = self._queue_subrule(node)
            arg = 'self.' + subrule_name
        return self._arg_text(starting_offset, [arg])

    def _handle_subrules(self, node, starting_offset):
        args = []
        for subrule in node:
            if subrule[0] == 'apply':
                args.append('self.' + self._rule_to_method_name(subrule[1]))
            elif subrule[0] == 'lit':
                args.append('lambda: self._h_str(' +
                        lit.encode(subrule[1]) + ')')
            else:
                subrule_name = self._queue_subrule(subrule)
                args.append('self.' + subrule_name)
        return self._arg_text(starting_offset, args)

    def _gen_rule_text(self, node):
        "Generate the text of a method and save it for collating, later."
        ast_method = getattr(self, '_' + node[0])
        s = ast_method(node)
        if not s.startswith('\n    def'):
            s = ('\n'
                 '    def %s(self):\n'
                 '        %s\n' % (self.current_rule_name, s))
        return s

    def _queue_subrule(self, subrule_node):
        "Queue up a new subrule for generation and return its name."
        name, _ = self._split_rule_name(self.current_rule_name)
        base_name = self._base_rule_name(self.current_rule_name)
        self.subrule_indices[base_name] += 1
        subrule_name = '{}_{}'.format(name, self.subrule_indices[base_name])
        self.rules.append([subrule_name, subrule_node])
        return subrule_name

    def _gen_expr(self, node):
        "Generate the text for this expression node for use in a method."
        ast_method = getattr(self, '_' + node[0])
        return ast_method(node)

    #
    # One function for each node type in the AST.
    #

    def _action(self, node):
        val = self._gen_expr(node[1])
        return 'self._h_succeed({})'.format(val)

    def _apply(self, node):
        rule_to_apply = self._rule_to_method_name(node[1])
        return 'self.{}()'.format(rule_to_apply)

    def _capture(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_capture(self.{})'.format(subrule_name)

    def _choice(self, node):
        arg_text = self._handle_subrules(node[1], 20)
        return 'self._h_choice([{}])'.format(arg_text)

    def _empty(self, node):
        del node
        return 'self._h_succeed(None)'

    def _eq(self, node):
        expr = self._gen_expr(node[1])
        return self._dedent('''
            def {}(self):
                val = {}
                if self.msg[self.pos:].startswith(val):
                    self._h_succeed(val, self.pos + 1)
                else:
                    self._fail()
            '''.format(self.current_rule_name, expr))

    def _label(self, node):
        arg_text = self._handle_subrule(node[1], 20)
        return 'self._h_label({}, {})'.format(arg_text, lit.encode(node[2]))

    def _leftrec(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_leftrec(self.{}, {})'.format(subrule_name,
                       lit.encode(self.current_rule_name))

    def _lit(self, node):
        return 'self._h_str({})'.format(lit.encode(node[1]))

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
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_memo(self.{}, {})'.format(subrule_name,
                       lit.encode(self.current_rule_name))

    def _not(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_not(self.{})'.format(subrule_name)

    def _opt(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_opt(self.{})'.format(subrule_name)

    def _paren(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_paren(self.{})'.format(subrule_name)

    def _plus(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_plus(self.{})'.format(subrule_name)

    def _pos(self, node):
        del node
        return 'self._h_succeed(self.pos)'

    def _pred(self, node):
        return self._dedent('''
            def {}(self):
                if {} == True:
                    return self._h_succeed(True)
                else:
                    return self._h_fail()
            '''.format(self.current_rule_name, self._gen_expr(node[1])))

    def _range(self, node):
        return 'self._h_range({}, {})'.format(lit.encode(node[1][1]),
                       lit.encode(node[2][1]))

    def _scope(self, node):
        arg_text = self._handle_subrules(
                node[1], 20 + len(self.current_rule_name))
        return 'self._h_scope({}, [{}])'.format(
                       lit.encode(self.current_rule_name),
                       arg_text)

    def _seq(self, node):
        arg_text = self._handle_subrules(node[1], 20)
        return 'self._h_seq([{}])'.format(arg_text)

    def _star(self, node):
        subrule_name = self._queue_subrule(node[1])
        return 'self._h_star(self.{})'.format(subrule_name)


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
        self.{starting_rule}()
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

    def _h_eq(self, var):
        self._h_str(var)

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

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, name, rules):
        self._scopes.append([name, {}])
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
