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

class Printer(object):
    def __init__(self, grammar):
        self.grammar = grammar

    def dumps(self):
        rules = []
        max_choice_len = 0
        max_rule_len = 0
        for rule_name, node in self.grammar.rules.items():
            cs = []
            for choice in node[1]:
                seq = choice[1]
                es = [self._proc(e) for e in seq[:-1]]
                if seq[-1][0] == 'action':
                    act = self._proc(seq[-1])
                else:
                    es.append(self._proc(seq[-1]))
                    act = None

                choice = ' '.join(es)
                max_choice_len = max(len(choice), max_choice_len)
                cs.append((choice, act))

            max_rule_len = max(len(rule_name), max_rule_len)
            rules.append((rule_name, cs))

        rule_fmt = '%%-%ds' % max_rule_len
        choice_fmt = '%%-%ds' % max_choice_len
        lines = []
        for rule_name, choices in rules:
            delim = '='
            pfx = rule_name
            for choice, act in choices:
                if choice == choices[-1][0]:
                    nl = ',\n'
                else:
                    nl = '\n'
                if act:
                    line = '%s %s %s %s%s' % (rule_fmt % pfx,
                                              delim,
                                              choice_fmt % choice,
                                              act,
                                              nl)
                else:
                    line = '%s %s %s%s' % (rule_fmt % pfx,
                                           delim,
                                           choice,
                                           nl)
                delim = '|'
                pfx = ''
                lines.append(line)
            lines.append('\n')
        return ''.join(lines).strip() + '\n'

    def _proc(self, node):
        try:
            fn = getattr(self, '_' + node[0] + '_')
            return fn(node)
        except Exception as e:
            import pdb; pdb.set_trace()

    def _sp_(self, node):
        return ' '

    def _choice_(self, node):
        return '|'.join(self._proc(e) for e in node[1])

    def _seq_(self, node):
        return ' '.join(self._proc(e) for e in node[1])

    def _label_(self, node):
        return '%s:%s' % (self._proc(node[1]), node[2])

    def _post_(self, node):
        return '%s%s' % (self._proc(node[1]), node[2])

    def _apply_(self, node):
        return node[1]

    def _action_(self, node):
        return '-> %s' % self._proc(node[1])

    def _not_(self, node):
        return '~%s' % self._proc(node[1])

    def _pred_(self, node):
        return '?(%s)' % self._proc(node[1])

    def _lit_(self, node):
        s = "'"
        i, l, expr = 0, len(node[1]), node[1]
        while i < l:
            if i < l - 1 and expr[i] == "\\":
                if expr[i+1] == "'":
                    s += "\\\\\\'"
                elif expr[i+1] == "\\":
                    s += "\\\\\\\\"
                else:
                    s += "\\" + expr[i+1]
                i += 2
            elif expr[i] == "\\":
                s += "\\\\"
                i += 1
            elif expr[i] == "'":
                s += "\\'"
                i += 1
            else:
                s += expr[i]
                i += 1
        return s + "'"

    def _paren_(self, node):
        return '(' + self._proc(node[1]) + ')'

    def _py_plus_(self, node):
        return '%s + %s' % (self._proc(node[1]), self._proc(node[2]))

    def _py_qual_(self, node):
        _, e, ops = node
        v = self._proc(e)
        os = []
        for op in ops:
            if op[0] == 'py_getitem':
                os.append('[%s]' % self._proc(op[1]))
            if op[0] == 'py_call':
                os.append('(%s)' % (', '.join(self._proc(a) for a in op[1])))
            if op[0] == 'py_getattr':
                os.append('.%s' % op[1])
        return '%s%s' % (v, ''.join(os))

    def _py_lit_(self, node):
        return self._lit_(node)

    def _py_var_(self, node):
        return node[1]

    def _py_num_(self, node):
        return str(node[1])

    def _py_arr_(self, node):
        return '[%s]' % ', '.join(self._proc(e) for e in node[1])
