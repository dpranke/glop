import unittest

from parser_base import ParserBase


class TestParser(unittest.TestCase):
    def test_unknown_rule(self):
        p = ParserBase("grammar = 'i'*", '')
        v, err = p.parse(rule='foo')
        self.assertEqual(v, None)
        self.assertEqual(err, ':1:1 expecting unknown rule "foo"')
