import textwrap
import unittest

from hand_rolled_grammar_parser import HandRolledGrammarParser


class TestGrammarHandParser(unittest.TestCase):
    def check(self, text, ast=None, dedent=True, err=None):
        text_to_parse = textwrap.dedent(text) if dedent else text
        parser = HandRolledGrammarParser(text_to_parse, 'glop.g')
        actual_ast, actual_err = parser.parse()
        self.assertEqual(actual_ast, ast)
        self.assertEqual(actual_err, err)

    def test_grammar(self):
        self.check('''
            grammar = foo:f end -> f,

            foo = 'foo',
            ''', [['rule', 'grammar',
                   ['seq', [['label', ['apply', 'foo'], 'f'],
                            ['apply', 'end'],
                            ['action', ['py_var', 'f']]]]],
                  ['rule', 'foo', ['lit', 'foo']]])

    def test_sp(self):
        self.check('', [])
        self.check(' \n', [], dedent=False)

        # this tests that tab chars are accepted as spaces w/o having to
        # embed an actual tab character in this file.
        self.check(chr(9), [], dedent=False)

    def test_choice(self):
        self.check('''
            grammar = foo | bar ,
            ''', [['rule', 'grammar',
                   ['choice', [['apply', 'foo'],
                               ['apply', 'bar']]]]])

        self.check('''
            grammar = foo | bar | baz,
            ''', [['rule', 'grammar',
                   ['choice', [['apply', 'foo'],
                               ['apply', 'bar'],
                               ['apply', 'baz']]]]])

    def test_action(self):
        self.check('''grammar = foo:f -> f,''',
                   [['rule', 'grammar',
                             ['seq', [['label', ['apply', 'foo'], 'f'],
                                      ['action', ['py_var', 'f']]]]]])

    def test_not(self):
        self.check('''grammar = ~'foo' ,''',
                   [['rule', 'grammar',
                             ['not', ['lit', 'foo']]]])

    def test_semantic_predicate(self):
        self.check('''grammar = ?( 1 + 1 ) ,''',
                   [['rule', 'grammar',
                             ['pred', ['py_plus', ['py_num', 1],
                                       ['py_num', 1]]]]])

    def test_parenthesized_expr(self):
        self.check('''grammar = ( 'foo' ) ,''',
                   [['rule', 'grammar', ['paren', ['lit', 'foo']]]])

    def test_post_ops(self):
        self.check('''grammar = foo? , ''',
                   [['rule', 'grammar', ['post', ['apply', 'foo'], '?']]])
        self.check('''grammar = foo* , ''',
                   [['rule', 'grammar', ['post', ['apply', 'foo'], '*']]])
        self.check('''grammar = foo+ , ''',
                   [['rule', 'grammar', ['post', ['apply', 'foo'], '+']]])

    def test_py_post_op(self):
        self.check('''grammar = ?( foo[1] ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_qual', ['py_var', 'foo'],
                                       [['py_getitem', ['py_num', 1]]]]]]])
        self.check('''grammar = ?( foo() ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_qual', ['py_var', 'foo'],
                                       [['py_call', []]]]]]])
        self.check('''grammar = ?( foo(1) ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_qual', ['py_var', 'foo'],
                                       [['py_call', [['py_num', 1]]]]]]]])
        self.check('''grammar = ?( foo(1, 2) ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_qual', ['py_var', 'foo'],
                                       [['py_call',
                                         [['py_num', 1],
                                          ['py_num', 2]]]]]]]])
        self.check('''grammar = ?( foo.bar ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_qual', ['py_var', 'foo'],
                                       [['py_getattr', 'bar']]]]]])

    def test_py_prim(self):
        self.check('''grammar = ?( 'foo' ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_lit', 'foo']]]])

        self.check('''grammar = ?( '' ) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_lit', '']]]])

        self.check('''grammar = ?( (1)) , ''',
                   [['rule', 'grammar',
                             ['pred', ['py_paren', ['py_num', 1]]]]])

    def test_unexpected_end(self):
        self.check('''
            grammar =
                   ''', ast=None, err='glop.g:2:2 expecting the end')
