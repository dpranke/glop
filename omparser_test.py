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

    def disabled_test_pom(self):
        self.check('''
            grammar = (sp rule)*:vs sp end  -> vs,
            ''', [['rule', 'grammar',
                   [['seq', ]]]])

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
