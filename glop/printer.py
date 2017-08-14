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
        rules, max_rule_len, max_choice_len = self._build_rules()
        return self._format_rules(rules, max_rule_len, max_choice_len)

    def _build_rules(self):
        rules = []
        max_choice_len = 0
        max_rule_len = 0
        for rule_name, node in self.grammar.rules.items():
            cs = []
            if self._node_is_only_a_few_short_terms(node):
                cs.append((' | '.join(self._proc(e) for e in node[1]), ''))
            else:
                for choice in node[1]:
                    seq = choice[1]
                    if seq[-1][0] == 'action':
                        act = ' ' + self._proc(seq.pop())
                    else:
                        act = ''
                    choice = ' '.join(self._proc(e) for e in seq)
                    max_choice_len = max(len(choice), max_choice_len)
                    cs.append((choice, act))

            max_rule_len = max(len(rule_name), max_rule_len)
            rules.append((rule_name, cs))
        return rules, max_rule_len, max_choice_len

    def _node_is_only_a_few_short_terms(self, node):
        assert node[0] == 'choice'
        assert all(e[0] == 'seq' for e in node[1])
        length = 0
        for el in node[1]:
            assert el[0] == 'seq'
            if len(el[1]) != 1:
                return False
            tag = el[1][0][0]
            if tag == 'lit':
                length += len(el[1][0][1]) + 5
            elif tag == 'apply':
                length += len(el[1][0][1]) + 3
            elif tag == 'range':
                length += len(el[1][0][1]) + len(el[1][0][2]) + 7
            else:
                return False
        return length < 36 

    def _format_rules(self, rules, max_rule_len, max_choice_len):
        line_fmt = ('%%-%ds' % max_rule_len + ' %s ' +
                    '%%-%ds' % max_choice_len + '%s')
        lines = []
        for rule_name, choices in rules:
            choice, act = choices[0]
            lines.append((line_fmt % (rule_name, '=', choice, act)).rstrip())
            for choice, act in choices[1:]:
                lines.append((line_fmt % ('', '|', choice, act)).rstrip())
            lines.append('')
        return '\n'.join(lines).strip() + '\n'

    def _proc(self, node):
        fn = getattr(self, '_' + node[0] + '_')
        return fn(node)

    #
    # Handlers for each node in the glop AST follow.
    #

    def _action_(self, node):
        return '-> %s' % self._proc(node[1])

    def _apply_(self, node):
        return node[1]

    def _choice_(self, node):
        return '|'.join(self._proc(e) for e in node[1])

    def _empty_(self, node):
        return ''

    def _label_(self, node):
        return '%s:%s' % (self._proc(node[1]), node[2])

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

    def _ll_arr_(self, node):
        return '[%s]' % ', '.join(self._proc(el) for el in node[1])

    def _ll_call_(self, node):
        return '(%s)' % ', '.join(self._proc(arg) for arg in node[1])

    def _ll_getattr_(self, node):
        return '.%s' % node[1]

    def _ll_getitem_(self, node):
        return '[%s]' % self._proc(node[1])

    def _ll_lit_(self, node):
        return self._lit_(node)

    def _ll_num_(self, node):
        return str(node[1])

    def _ll_plus_(self, node):
        return '%s + %s' % (self._proc(node[1]), self._proc(node[2]))
    
    def _ll_qual_(self, node):
        _, e, ops = node
        v = self._proc(e)
        return '%s%s' % (v, ''.join(self._proc(op) for op in ops))

    def _ll_var_(self, node):
        return node[1]

    def _range_(self, node):
        return '%s..%s' % (self._proc(node[1]), self._proc(node[2]))
    def _not_(self, node):
        return '~%s' % self._proc(node[1])

    def _pred_(self, node):
        return '?(%s)' % self._proc(node[1])

    def _post_(self, node):
        return '%s%s' % (self._proc(node[1]), node[2])

    def _seq_(self, node):
        return ' '.join(self._proc(e) for e in node[1])

    def _sp_(self, node):
        return ' '

    def _paren_(self, node):
        return '(' + self._proc(node[1]) + ')'

