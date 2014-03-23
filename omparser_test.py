import textwrap
import unittest

from omparser import OMParser


class TestOMParser(unittest.TestCase):
    def check(self, text, ast=None, dedent=True, err=None):
        text_to_parse = textwrap.dedent(text) if dedent else text
        parser = OMParser(text_to_parse, 'pom.pom')
        actual_ast, actual_err = parser.parse()
        self.assertEqual(actual_ast, ast)
        self.assertEqual(actual_err, err)

    def test_grammar(self):
        self.check('''
            grammar = foo:f end -> f,

            foo = 'foo',
            ''',
            [['rule', 'grammar',
                      ['seq', [['label', ['apply', 'foo'], 'f'],
                               ['apply', 'end'],
                               ['action', 'f']]]],
             ['rule', 'foo',
                      ['lit', 'foo']]])

    def test_sp(self):
        self.check('', [])
        self.check(' \n', [], dedent=False)

    def test_unexpected_end(self):
        self.check('''
            grammar =
                   ''', ast=None, err='pom.pom:2:2 expecting the end')

