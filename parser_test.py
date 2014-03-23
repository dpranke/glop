import unittest

from parser import Parser


class TestParser(unittest.TestCase):
    def test_unknown_rule(self):
        p = Parser("grammar = 'i'*", '')
        v, err = p.parse(rule='foo')
        self.assertEqual(v, None)
        self.assertEqual(err, ':1:1 expecting unknown rule "foo"')
