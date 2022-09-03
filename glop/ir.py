# Copyright 2014 Dirk Pranke. All rights reserved.
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


class Grammar:
    def __init__(self, ast):
        ast = rewrite_sequences_with_labels(ast)
        self.ast = simplify(ast)
        self.rules = self.ast[1]
        self.rule_names = set(r[1] for r in self.rules)
        self.starting_rule = self.rules[0][1]


def has_labels(node):
    if node[0] == 'label':
        return True
    if node[0] in ('choice', 'rules', 'scope', 'seq'):
        return any(has_labels(subnode) for subnode in node[1])
    if node[0] in ('capture', 'leftrec', 'not', 'opt', 'paren',
                   'plus', 'star'):
        return has_labels(node[1])
    if node[0] in ('rule',):
        return has_labels(node[2])
    return False


def has_left_recursion(ast):
    return left_recursive_rules(ast) != set()


def left_recursive_rules(ast):
    """Returns a list of all potentially left-recursive rules."""
    lr_rules = set()
    rules = {}
    for _, name, body in ast[1]:
        rules[name] = body
    for _, name, body in ast[1]:
        seen = set()
        has_lr = _check_lr(name, body, rules, seen)
        if has_lr:
            lr_rules.add(name)
    return lr_rules


def rewrite_left_recursion(ast):
    lr_rules = left_recursive_rules(ast)
    new_rules = []
    for rule in ast[1]:
        if rule[1] in lr_rules:
            new_rules.append([rule[0], rule[1], ['leftrec', rule[2], rule[1]]])
        else:
            new_rules.append(rule)
    return ['rules', new_rules]


def _check_lr(name, node, rules, seen):
    # pylint: disable=too-many-branches
    ty = node[0]
    if ty == 'action':
        return False
    if ty == 'apply':
        if node[1] == name:
            return True  # Direct recursion.
        if node[1] in ('anything', 'end'):
            return False
        if node[1] in seen:
            # We've hit left recursion on a different rule, so, no.
            return False
        seen.add(node[1])
        return _check_lr(name, rules[node[1]], rules, seen)
    if ty == 'capture':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'choice':
        for n in node[1]:
            # All branches in a choice have to return False for us
            # to be sure the choice doesn't have recursion.
            ret = _check_lr(name, n, rules, seen)
            if ret or ret is None:
                return True
        return False
    if ty == 'empty':
        return False
    if ty == 'eq':
        return None
    if ty == 'label':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'leftrec':
        return True
    if ty == 'lit':
        return False
    if ty == 'memo':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'not':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'opt':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'paren':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'plus':
        return _check_lr(name, node[1], rules, seen)
    if ty == 'pos':
        return None
    if ty == 'pred':
        return None
    if ty == 'range':
        return False
    if ty == 'scope':
        for subnode in node[1]:
            r = _check_lr(name, subnode, rules, seen)
            if r is not None:
                return r
        return False
    if ty == 'seq':
        for subnode in node[1]:
            r = _check_lr(name, subnode, rules, seen)
            if r is not None:
                return r
        return False
    if ty == 'star':
        return _check_lr(name, node[1], rules, seen)

    assert False, 'unexpected AST node type %s' % ty  # pragma: no cover


def memoize(ast):
    """Returns a new AST with the given rules memoized."""
    new_rules = []
    for rule in ast[1]:
        _, name, node = rule
        new_rules.append(['rule', name, ['memo', node, name]])
    return ['rules', new_rules]


def add_builtin_vars(node):
    """Returns a new AST rewritten to support the _* vars."""
    if node[0] == 'rules':
        return ['rules', [add_builtin_vars(rule) for rule in node[1]]]

    assert node[0] == 'rule', 'unexpected AST node %s' % node[0]

    name = node[1]
    body = node[2]
    if body[0] == 'leftrec':
        if body[1][0] == 'choice':
            choices = body[1][1]
        else:
            choices = [body[1]]
    elif body[0] == 'choice':
        choices = body[1]
    else:
        choices = [body]
    new_choices = _rewrite_choices(name, choices)

    if body[0] == 'leftrec':
        if len(new_choices) > 1:
            return ['rule', name, ['leftrec', ['choice', new_choices], body[2]]]
        return ['rule', name, ['leftrec', new_choices[0], body[2]]]
    if len(new_choices) > 1:
        return ['rule', name, ['choice', new_choices]]
    return ['rule', name, new_choices[0]]


def _rewrite_choices(rule_name, choices):
    new_choices = []
    for seq in choices:
        tag = seq[0]
        if tag not in ('seq', 'scope'):
            new_choices.append(seq)
            continue

        terms = seq[1]
        new_terms = []
        for i, term in enumerate(terms[:-1]):
            pos_var = '_%d' % (i + 1)
            pos_is_needed = (any(_var_is_needed(pos_var, st)
                                 for st in terms[i+1:]))
            if pos_is_needed:
                tag = 'scope'
                new_terms.append(['label', term, pos_var])
            else:
                new_terms.append(term)
        new_terms.append(terms[-1])
        if tag == 'scope':
            new_choices.append([tag, new_terms, rule_name])
        else:
            new_choices.append([tag, new_terms])
    return new_choices


def _var_is_needed(name, node):
    ty = node[0]
    if ty == 'll_var' and node[1] == name:
        return True
    if ty in ('eq', 'pred', 'action',
                'll_paren', 'll_getitem', 'll_getattr'):
        return _var_is_needed(name, node[1])
    if ty == 'll_plus':
        return (_var_is_needed(name, node[1]) or
                _var_is_needed(name, node[2]))
    if ty == 'll_qual':
        return (_var_is_needed(name, node[1]) or
                any(_var_is_needed(name, sn) for sn in node[2]))
    if ty in ('choice', 'seq', 'll_arr', 'll_call'):
        return any(_var_is_needed(name, sn) for sn in node[1])
    return False


def simplify(node):
    """Returns a new, simplified version of an AST:

    * Any `choice`, `seq`, or `scope` node with only one child is replaced
      the child.
    * Any `paren` node is replaced by its child node.
    """
    node_type = node[0]
    if node_type == 'rules':
        return [node_type, [simplify(n) for n in node[1]]]
    if node_type == 'rule':
        return [node_type, node[1], simplify(node[2])]
    if node_type in ('choice', 'seq'):
        if len(node[1]) == 1:
            return simplify(node[1][0])
        return [node_type, [simplify(n) for n in node[1]]]
    if node_type in ('capture', 'not', 'opt', 'plus', 're', 'star'):
        return [node_type, simplify(node[1])]
    if node_type == 'paren':
        # TODO: simplify when it is safe to do so.
        return [node_type, simplify(node[1])]
    if node_type in ('label', 'leftrec', 'memo'):
        return [node_type, simplify(node[1]), node[2]]
    if node_type == 'scope':
        return [node_type, [simplify(n) for n in node[1]], node[2]]
    return node


def rewrite_sequences_with_labels(ast):
    for rule in ast[1]:
        rule_name = rule[1]
        if rule[2][0] == 'choice':
            new_choices = []
            for choice in rule[2][1]:
                if choice[0] == 'seq':
                    if _has_labels(choice[1]):
                        new_choice = ['scope', choice[1], rule_name]
                    else:
                        new_choice = choice
                else:
                    new_choice = choice
                new_choices.append(new_choice)
            rule[2][1] = new_choices
    return ast


def _has_labels(node):
    if node and node[0] == 'label':
        return True
    for n in node:
        if isinstance(n, list) and _has_labels(n):
            return True
    return False
