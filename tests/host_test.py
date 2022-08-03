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

"""Test routines needed to get host and fake_host.py fully covered.

Most of the Host() and FakeHost() routines are actually tested by
the tests in main_test.py. But, some of them are only executed in
a subprocess, and so we don't get code coverage reported for them.

This file exists to test those routines directly, so that we can
reach 100% coverage. Alternatively, we could just mark those blocks
of code with '# pragma: no cover' (like we do in some places below),
but this approach has the merit of collecting things in one place
with one explanations all in one place.
"""

import io
import os
import sys
import unittest

test_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.dirname(test_dir)
if not src_root in sys.path:  # pragma: no cover
    sys.path.insert(0, src_root)

# pylint: disable=wrong-import-position

from glop.host import Host
from tests.host_fake import FakeHost

class FakeHostTests(unittest.TestCase):
    def test_chdir(self):
        host = FakeHost()
        host.chdir('foo', 'bar')
        self.assertEqual(host.getcwd(), '/tmp/foo/bar')

    def test_join(self):
        host = FakeHost()
        self.assertEqual('foo/bar', host.join('foo', '', 'bar'))
        self.assertEqual('foo/baz', host.join('foo', 'bar', '..', 'baz'))

    def test_make_executable(self):
        host = FakeHost()

        # We don't actually need to test that this does anything (we don't
        # care what it does, only that it exists as a method).
        host.make_executable(__file__)

class RealHostTests(unittest.TestCase):
    def test_basename(self):
        host = Host()
        self.assertEqual("bar.py", host.basename("foo/bar.py"))

    def test_call(self):
        host = Host()
        greeting = "hello\n"
        cmd = [host.python_interpreter, __file__]
        _, out, _ = host.call(cmd, stdin=greeting)
        self.assertEqual(out, greeting)

    def test_getcwd(self):
        host = Host()
        self.assertNotEqual(host.getcwd(), "")

    def test_print(self):
        host = Host()
        strm = io.StringIO()
        greeting = "hello\n"
        host.print_(greeting, end='', stream=strm)
        self.assertEqual(strm.getvalue(), greeting)

    def test_splitext(self):
        host = Host()
        self.assertEqual(host.splitext('foo.txt'),
                         ('foo', '.txt'))


if __name__ == '__main__':  # pragma: no cover
    msg = sys.stdin.read()
    print(msg, end='')
