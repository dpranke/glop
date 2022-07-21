# Copyright 2017 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
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

from glop import box


class TestUnquote(unittest.TestCase):
    def test_bare(self):
        self.assertEqual(['foo', ['bar', 'baz']],
                         box.unquote(['foo', ['bar', 'baz']], {}))

    def test_bare_for(self):
        self.assertEqual([1, 2, 3],
                         box.unquote(['for', 'els', ['var', '.']],
                                     {'els': [1, 2, 3]}))

    def test_bare_if(self):
        self.assertEqual(['baz'],
                         box.unquote(['if', '.bar', 'baz'],
                                     {'bar': True}))

        self.assertEqual([],
                         box.unquote(['if', '.bar', 'baz'],
                                     {'bar': False}))

        self.assertEqual(['snob'],
                         box.unquote(['if', '.bar', 'baz', 'snob'],
                                     {'bar': False})) 

    def test_bare_var(self):
        self.assertEqual(4, 
                         box.unquote(['var', '.baz'],
                                     {'baz': 4}))

    def test_spliced_for(self):
        self.assertEqual(['foo', 1, 2, 3, 'baz'],
                         box.unquote(['foo',
                                      ['for', 'els', ['var', '.']],
                                      'baz'],
                                     {'els': [1, 2, 3]}))

    def test_spliced_if_true(self):
        self.assertEqual(['foo', 'baz', 'quux'],
                         box.unquote(['foo', ['if', '.bar', 'baz'], 'quux'],
                                     {'bar': True}))

    def test_spliced_if_false_is_empty(self):
        self.assertEqual(['foo', 'quux'],
                         box.unquote(['foo', ['if', '.bar', 'baz'], 'quux'],
                                     {'bar': False}))

    def test_spliced_if_false_value(self):
        self.assertEqual(['foo', 'snob', 'quux'],
                         box.unquote(['foo',
                                      ['if', '.bar', 'baz', 'snob'],
                                      'quux'],
                                     {'bar': False}))

    def test_spliced_var(self):
        self.assertEqual(['foo', 4, 'quux'],
                          box.unquote(['foo', ['var', '.baz'], 'quux'],
                                      {'baz': 4}))


class TestFormat(unittest.TestCase):
    def test_h(self):
        self.assertEqual('foobar',
                         box.format(['h', 'foo', 'bar']))

    def test_iv(self):
        self.assertEqual('    foo\n    bar',
                         box.format(['iv', 'foo', 'bar']))

    def test_v(self):
        self.assertEqual('foo\nbar',
                         box.format(['v', 'foo', 'bar']))


if __name__ == '__main__':
    unittest.main()
