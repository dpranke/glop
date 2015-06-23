# Copyright 2014 Google Inc. All rights reserved.
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

import textwrap
import unittest

from glop.hand_rolled_grammar_parser import HandRolledGrammarParser


class TestGrammarHandParser(unittest.TestCase):
    def check(self, text, ast=None, dedent=True, err=None):
        text_to_parse = textwrap.dedent(text) if dedent else text
        parser = HandRolledGrammarParser(text_to_parse, 'glop.g')
        actual_ast, actual_err = parser.parse()
        self.assertEqual(actual_ast, ast)
        self.assertEqual(actual_err, err)

    def check_seq(self, expr, nodes):
        self.check("grammar = " + expr + ",",
                   [['rule', 'grammar', ['choice', [['seq', nodes]]]]])

    def check_expr(self, expr, node):
        self.check_seq(expr, [node])

    def test_grammar(self):
        self.check('''
            grammar = foo:f end -> f,

            foo = 'foo',
            ''', [['rule', 'grammar', ['choice', [
                   ['seq', [['label', ['apply', 'foo'], 'f'],
                            ['apply', 'end'],
                            ['action', ['py_var', 'f']]]]]]],
                  ['rule', 'foo', ['choice', [['seq', [['lit', 'foo']]]]]]])

    def test_sp(self):
        self.check('', [])
        self.check(' \n', [], dedent=False)

        # this tests that tab chars are accepted as spaces w/o having to
        # embed an actual tab character in this file.
        self.check(chr(9), [], dedent=False)

    def test_choice(self):
        self.check("grammar = foo | bar,",
                   [['rule', 'grammar', ['choice', [
                     ['seq', [['apply', 'foo']]],
                     ['seq', [['apply', 'bar']]]
                     ]]]])

        self.check("grammar = foo | bar | baz,",
                   [['rule', 'grammar', ['choice', [
                       ['seq', [['apply', 'foo']]],
                       ['seq', [['apply', 'bar']]],
                       ['seq', [['apply', 'baz']]]
                   ]]]])

    def test_action(self):
        self.check_seq("foo:f -> f",
                       [['label', ['apply', 'foo'], 'f'],
                        ['action', ['py_var', 'f']]])

    def test_not(self):
        self.check_expr("~'foo'",
                        ['not', ['lit', 'foo']])

    def test_semantic_predicate(self):
        self.check_expr("?( 1 + 1 )",
                        ['pred', ['py_plus', ['py_num', 1],
                                             ['py_num', 1]]])

    def test_parenthesized_expr(self):
        self.check_seq("('foo')",
                       [['paren', ['choice', [['seq', [['lit', 'foo']]]]]]])

    def test_post_ops(self):
        self.check_expr("foo?",
                        ['post', ['apply', 'foo'], '?'])
        self.check_expr("foo*",
                        ['post', ['apply', 'foo'], '*'])
        self.check_expr("foo+",
                        ['post', ['apply', 'foo'], '+'])

    def test_py_post_op(self):
        self.check_expr("?(foo[1])",
                        ['pred', ['py_qual', ['py_var', 'foo'],
                                             [['py_getitem', ['py_num', 1]]]]])
        self.check_expr("?(foo())",
                        ['pred', ['py_qual', ['py_var', 'foo'],
                                             [['py_call', []]]]])
        self.check_expr("?(foo(1))",
                        ['pred', ['py_qual', ['py_var', 'foo'],
                                             [['py_call', [['py_num', 1]]]]]])
        self.check_expr("?(foo(1, 2))",
                        ['pred', ['py_qual', ['py_var', 'foo'],
                                             [['py_call',
                                               [['py_num', 1],
                                                ['py_num', 2]]]]]])
        self.check_expr("?(foo.bar)",
                        ['pred', ['py_qual', ['py_var', 'foo'],
                                             [['py_getattr', 'bar']]]])

    def test_py_prim(self):
        self.check_expr("?('foo')",
                        ['pred', ['py_lit', 'foo']])

        self.check_expr("?('')",
                        ['pred', ['py_lit', '']])

        self.check_expr("?((1))",
                        ['pred', ['py_paren', ['py_num', 1]]])

    def test_unexpected_end(self):
        self.check('''
            grammar =
                   ''', ast=None, err='glop.g:2:2 expecting the end')
