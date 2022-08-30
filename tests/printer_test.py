# Copyright 2022 Dirk Pranke. All rights reserved.
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

import unittest

from glop.ir import Grammar
from glop.parser import Parser
from glop.printer import Printer


class PrinterTest(unittest.TestCase):
    def check(self, inp, expected_outp):
        ast, err, _ = Parser(inp, '').parse()
        assert err is None
        g = Grammar(ast)
        actual_outp = Printer(g).dumps()

        self.assertEqual(expected_outp, actual_outp)

    def test_basic_stuff(self):
        self.check('grammar  =  "hello"\n',
                   "grammar = 'hello'\n")

    def test_escaping(self):
        self.check(r"grammar = '\b\f\n\r\t\v\u0260'",
                   r"grammar = '\b\f\n\r\t\v\u0260'" + '\n')

    def test_empty(self):
        self.check("grammar = 'foo'|",
                   "grammar = 'foo' |\n")

    def test_dec(self):
        self.check("grammar = -> 14",
                   "grammar = -> 14\n")

    def test_eq(self):
        self.check("grammar = ={true} -> true\n",
                   "grammar = ={ true } -> true\n")


    def test_hex(self):
        self.check("grammar = -> 0x14",
                   "grammar = -> 0x14\n")

    def test_paren(self):
        self.check("grammar = ('a'|'b')+ -> 'ab'",
                   "grammar = ('a' | 'b')+ -> 'ab'\n")

    def test_pos(self):
        self.check("grammar = {}:x -> x",
                   "grammar = {}:x -> x\n")

    def test_pred(self):
        self.check("grammar = ?{true} -> true\n",
                   "grammar = ?{ true } -> true\n")
