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

    def test_blanks(self):
        self.check('', [])
        self.check(' \n', [], dedent=False)
