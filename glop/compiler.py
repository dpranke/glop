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

from . import box
from . import ir
from . import lit
from .python_templates import defs


class Compiler:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, grammar, classname, main_wanted, memoize):
        self.grammar = grammar
        self.classname = classname
        self.memoize = memoize
        self.main_wanted = main_wanted

        self._methods = {}
        self._method_lines = []
        self._identifiers = defs['identifiers']
        self._imports = defs['imports']
        self._main_imports = defs['main_imports']
        self._natives = defs['methods']
        self._needed = set(['_h_err'])
        self._text = defs['text']

    def compile(self):
        ast = self.grammar.ast
        ast = ir.rewrite_left_recursion(ast)
        ast = ir.add_builtin_vars(ast)
        ast = ir.flatten(ast, self._should_flatten)
        if self.memoize:
            original_names = set('_r_' + name
                                 for name in self.grammar.rule_names)
            ast = ir.memoize(ast, original_names)
        self.grammar = ir.Grammar(ast)

        for _, rule, node in self.grammar.rules:
            self._methods[rule] = self._gen(node, as_callable=False)

        imports = set(self._imports)
        for name in self._needed:
            for imp in self._natives.get(name, {}).get('imports', []):
                imports.add(imp)
        if self.main_wanted:
            for imp in self._main_imports:
                imports.add(imp)

        methods = []
        for _, rule, _ in self.grammar.rules:
            methods.append({'lines': ['v', 'def %s(self):' % rule,
                                           ['iv', self._methods[rule] ]]})

        methods.extend(self._native_methods_of_type('_r_'))
        methods.extend(self._native_methods_of_type('_f_'))
        methods.extend(self._native_methods_of_type('_h_'))

        scopes_wanted = ('_h_set' in self._needed and
                         '_h_scope' in self._needed)
        seeds_wanted = ('_h_leftrec' in self._needed)
        args = {
          'classname': self.classname,
          'imports': sorted(imports),
          'main_wanted': self.main_wanted,
          'memoize': self.memoize,
          'methods': methods,
          'scopes_wanted': scopes_wanted,
          'seeds_wanted': seeds_wanted,
          'starting_rule': self.grammar.starting_rule,
        }

        b = box.format(box.unquote(self._text, args))
        return b + '\n'

    def _native_methods_of_type(self, ty):
        methods = []
        for name in sorted(r for r in self._needed if r.startswith(ty)):
            methods.append({
                'name': name,
                'lines': self._natives[name]['lines']
            })
        return methods

    def _gen(self, node, as_callable):
        fn = getattr(self, '_%s_' % node[0])
        return fn(node, as_callable)

    # Using a MAX_DEPTH of three ensures that we don't unroll expressions
    # too much; in particular, by making sure that any of the nodes that
    # contain more than one child are set to MAX_DEPTH, we don't nest
    # two of them at once. This keeps things fairly readable.
    _MAX_DEPTH = 3

    def _depth(self, node):
        ty = node[0]
        if ty in ('choice', 'scope', 'seq'):
            return max(self._depth(n) for n in node[1]) + self._MAX_DEPTH
        if ty in ('label', 'not', 'opt', 'paren', 'plus', 're', 'star'):
            return self._depth(node[1]) + 1
        return 1

    def _should_flatten(self, node):
        return self._depth(node) > self._MAX_DEPTH

    def _inv(self, name, as_callable, args):
        if name in self._natives:
            self._need(name)
        if as_callable:
            return ['h', 'lambda: self.%s(' % name] + args + [')']
        return ['h', 'self.%s(' % name] + args + [')']

    def _need(self, name):
        self._needed.add(name)
        for need in self._natives.get(name, {}).get('needs', []):
            self._need(need)

    def _args(self, args):
        box_args = ['v']
        for arg in args[:-1]:
            box_args.append(['h', self._gen(arg, True), ','])
        box_args.append(['h', self._gen(args[-1], True)])
        return ['h', '[', box_args, ']']

    #
    # Handlers for each AST node follow.
    #

    def _action_(self, node, as_callable):
        return self._inv('_h_succeed', as_callable, [self._gen(node[1], True)])

    def _apply_(self, node, as_callable):
        rule_name = node[1]
        if rule_name not in self.grammar.rule_names:
            self._need(rule_name)
        if as_callable:
            return 'self.%s' % rule_name
        return 'self.%s()' % rule_name

    def _capture_(self, node, as_callable):
        val = self._gen(node[1], True)
        return self._inv('_h_capture', as_callable, [val])

    def _choice_(self, node, as_callable):
        return self._inv('_h_choose', as_callable, [self._args(node[1])])

    def _empty_(self, _node, as_callable):
        if as_callable:
            return 'lambda: None'
        return ''

    def _eq_(self, node, as_callable):
        val = self._gen(node[1], as_callable)
        return self._inv('_h_eq', as_callable, [val])

    def _label_(self, node, as_callable):
        var = lit.encode(node[2])
        val = self._gen(node[1], True)
        return self._inv('_h_bind', as_callable, [val, ', ', var])

    def _label_all_(self, node, as_callable):
        rule = lit.encode(node[1])
        return self._inv('_h_bind_all', as_callable, [rule, ', ', node[2]])

    def _leftrec_(self, node, as_callable):
        var = lit.encode(node[2])
        val = self._gen(node[1], True)
        return self._inv('_h_leftrec', as_callable, [val, ', ', var])

    def _lit_(self, node, as_callable):
        arg = lit.encode(node[1])
        if len(node[1]) == 1:
            self._need('_h_ch')
            if as_callable:
                return ['h', 'lambda: self._h_ch(', arg, ')']
            return ['h', 'self._h_ch(', arg, ')']
        self._need('_h_str')
        if as_callable:
            return ['h', 'lambda: self._h_str(', arg, ')']
        return ['h', 'self._h_str(', arg, ')']

    def _ll_call_(self, node, as_callable):
        del as_callable
        args = [str(self._gen(e, True)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _ll_dec_(self, node, as_callable):
        del as_callable
        return node[1]

    def _ll_getitem_(self, node, as_callable):
        del as_callable
        return '[' + str(self._gen(node[1], True)) + ']'

    def _ll_hex_(self, node, as_callable):
        del as_callable
        return '0x' + node[1]

    def _ll_paren_(self, node, as_callable):
        return self._gen(node[1], True)

    def _ll_plus_(self, node, as_callable):
        del as_callable
        return '%s + %s' % (self._gen(node[1], True), self._gen(node[2], True))

    def _ll_qual_(self, node, as_callable):
        del as_callable
        v = self._gen(node[1], True)
        for p in node[2]:
            v += self._gen(p, True)
        return v

    def _ll_str_(self, node, as_callable):
        del as_callable
        return lit.encode(node[1])

    def _ll_var_(self, node, as_callable):
        del as_callable
        name = node[1]
        if name in self._identifiers:
            return self._identifiers[name]
        if '_f_' + name in self._natives:
            self._need('_f_%s' % name)
            return 'self._f_%s' % name
        self._need('_h_get')
        return 'self._h_get(\'%s\')' % name

    def _memo_(self, node, as_callable):
        var = lit.encode(node[2])
        val = self._gen(node[1], True)
        return self._inv('_h_memo', as_callable, [val, ', ', var])

    def _not_(self, node, as_callable):
        val = self._gen(node[1], True)
        return self._inv('_h_not', as_callable, [val])

    def _opt_(self, node, as_callable):
        val = self._gen(node[1], True)
        return self._inv('_h_opt', as_callable, [val])

    def _paren_(self, node, as_callable):
        return self._gen(node[1], as_callable)

    def _plus_(self, node, as_callable):
        val = self._gen(node[1], True)
        return self._inv('_h_plus', as_callable, [val])

    def _pos_(self, node, as_callable):
        del node
        return self._inv('_h_pos', as_callable, [])

    def _pred_(self, node, as_callable):
        self._need('_h_succeed')
        self._need('_h_fail')
        val = self._gen(node[1], True)
        if as_callable:
            return ['h',
                    'lambda: ('
                    'lambda x: self._h_succeed(x) if x is True else self._h_fail())(',
                    val,
                    ')']
        return ['v',
                'v = %s' % self._gen(node[1], True),
                'if v:',
                '    self._h_succeed(v)',
                'else:',
                '    self._h_fail()']

    def _range_(self, node, as_callable):
        x = lit.encode(node[1][1])
        y = lit.encode(node[2][1])
        return self._inv('_h_range', as_callable, [x, ', ', y])

    def _scope_(self, node, as_callable):
        val = self._args(node[1])
        name = '\'%s\'' % node[2]
        return self._inv('_h_scope', as_callable, [name, ', ', val])

    def _seq_(self, node, as_callable):
        val = self._args(node[1])
        return self._inv('_h_seq', as_callable, [val])

    def _star_(self, node, as_callable):
        val = self._gen(node[1], True)
        return self._inv('_h_star', as_callable, [val])
