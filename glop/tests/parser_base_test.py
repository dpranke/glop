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

import unittest

from glop.parser_base import ParserBase


class TestParser(unittest.TestCase):
    def test_unknown_rule(self):
        p = ParserBase("grammar = 'i'*", '')
        v, err = p.parse(rule='foo')
        self.assertEqual(v, None)
        self.assertEqual(err, ':1:1 expecting unknown rule "foo"')
