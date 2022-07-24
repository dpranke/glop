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
        ast, _, _ = Parser(inp, '').parse()
        g = Grammar(ast)
        actual_outp = Printer(g).dumps()
        self.assertEqual(expected_outp, actual_outp)

    def test_basic_stuff(self):
        self.check('grammar  =  "hello"\n', 
                   "grammar = 'hello'\n")

    def test_escaping(self):
        self.check(r"grammar = '\b\f\n\r\t\v\u0260'",
                   r"grammar = '\b\f\n\r\t\v\u0260'" + '\n')
