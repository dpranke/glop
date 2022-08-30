# Copyright 2014 Dirk Pranke. All rights reserved.
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

from glop.host import Host
import glop.tool
from .host_fake import FakeHost


SIMPLE_GRAMMAR = "grammar = anything*:as end -> join('', as) ,"


class ToolTests(unittest.TestCase):
    maxDiff = None

    def check_call_and_return_files(self, host, args, files):
        orig_wd = None
        tmpdir = None
        try:
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()

            host.chdir(tmpdir)
            host.write_text_files(files)
            self._call(host, args, returncode=0)

            return host.read_text_files(tmpdir)

        finally:
            if tmpdir:
                host.rmtree(tmpdir)
            if orig_wd:
                host.chdir(orig_wd)

    def check_cmd(self, args, stdin=None, files=None,
                  returncode=None, out=None, err=None, output_files=None,
                  actual_output_files=None):
        host = self._host()
        orig_wd = None
        tmpdir = None
        try:
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()
            host.chdir(tmpdir)
            if files:
                host.write_text_files(files)

            rv = self._call(host, args, stdin, returncode, out, err)
            actual_ret, actual_out, actual_err = rv

            if output_files:
                actual_output_files = host.read_text_files(host.getcwd())
        finally:
            if tmpdir:
                host.rmtree(tmpdir)
            if orig_wd:
                host.chdir(orig_wd)

        if output_files:
            self._assert_files(output_files, actual_output_files)
        return actual_ret, actual_out, actual_err

    def _host(self):
        return FakeHost()

    def _call(self, host, args, stdin=None, returncode=None, out=None,
            err=None):
        if stdin is not None:
            host.stdin.write(str(stdin))
            host.stdin.seek(0)
        actual_ret = glop.tool.main(host, args)
        actual_out = host.stdout.getvalue()
        actual_err = host.stderr.getvalue()
        if returncode is not None:
            self.assertEqual(returncode, actual_ret)
        if out is not None:
            self.assertEqual(str(out), actual_out)
        if err is not None:
            self.assertEqual(str(err), actual_err)
        return actual_ret, actual_out, actual_err

    def _assert_files(self, expected_files, actual_files):
        for k, v in actual_files.items():
            self.assertEqual(expected_files[k], v)
        self.assertEqual(set(actual_files.keys()), set(expected_files.keys()))

    def test_bad_command_line_switch(self):
        self.check_cmd(['--not-a-switch'], returncode=2)

    def test_ctrl_c(self):
        host = FakeHost()

        def raise_ctrl_c(*_comps):
            raise KeyboardInterrupt

        host.read_text_file = raise_ctrl_c
        host.write_text_file('simple.g', SIMPLE_GRAMMAR)

        self._call(host, ['simple.g'], returncode=130,
                   out='', err='Interrupted, exiting ...\n')

    def test_compile_bad_grammar(self):
        files = {
            'bad.g': 'grammar',
        }
        self.check_cmd(['-c', 'bad.g'], files=files,
                       returncode=1, out='', err=None)

    def test_files(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
            'input.txt': 'hello, world\n',
        }
        out_files = files.copy()
        out_files['output.txt'] = '"hello, world\\n"\n'
        self.check_cmd(['-i', 'input.txt', '-o', 'output.txt',
                        'simple.g'],
                       files=files, returncode=0, out='', err='',
                       output_files=out_files)

    def test_grammar_file_not_found(self):
        self.check_cmd(['missing.g'], returncode=1,
                       err='Error: no such file: "missing.g"\n')

    def test_help(self):
        self.check_cmd(['--help'], returncode=0)

    def test_input_is_expr(self):
        self.check_cmd(['-e', SIMPLE_GRAMMAR], stdin='hello, world\n',
                       returncode=0)

    def test_input_on_stdin(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        self.check_cmd(['-i', '-', 'simple.g'], stdin="hello, world\n",
                       files=files, returncode=0, out='"hello, world\\n"\n',
                       err='')

    def test_main(self):
        host = self._host()
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        args = ['-c', '--main', 'simple.g']

        output_files = self.check_call_and_return_files(host, args, files)
        self.assertIn('simple.py', output_files.keys())
        self.assertIn("if __name__ == '__main__'",
                      output_files['simple.py'])

    def test_no_grammar(self):
        self.check_cmd([], returncode=2)

    def test_no_main(self):
        host = self._host()
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        args = ['-c', 'simple.g']

        output_files = self.check_call_and_return_files(host, args, files)
        self.assertIn('simple.py', output_files.keys())
        self.assertNotIn("if __name__ == '__main__'",
                         output_files['simple.py'])

    def test_interpret_bad_grammar(self):
        files = {
            'bad.g': 'grammar',
        }
        self.check_cmd(['bad.g'], files=files,
                       returncode=1, out='', err=None)

    def test_output_flags(self):
        self.check_cmd(['-e', 'grammar = -> "ok"'],
                       returncode=0, out = '"ok"\n')
        self.check_cmd(['-e', 'grammar = -> "ok"', '--as-string'],
                       returncode=0, out = 'ok\n')
        self.check_cmd(['-e', 'grammar = -> "ok"', '--as-string',
                        '--no-appended-newline'],
                       returncode=0, out = 'ok')
        self.check_cmd(['-e', 'grammar = -> ["o", "k"]', '--as-string'],
                       returncode=0, out = 'ok\n')

    def test_pretty_print(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        self.check_cmd(['-p', 'simple.g'], files=files,
                       returncode=0,
                       out="grammar = anything*:as end -> join('', as)\n")

    def test_pretty_print_glop(self):
        # This tests pretty-printing of a non-trivial grammar (glop itself)
        # in a limited way: it tests that pretty-printing an already
        # pretty-printed grammar doesn't change anything.

        h = Host()
        glop_contents = h.read_text_file(
            h.join(h.dirname(h.path_to_host_module()), '..',
                   'grammars', 'glop.g'))

        files = {'glop.g': glop_contents}

        host = self._host()
        orig_wd = None
        tmpdir = None
        try:
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()
            host.chdir(tmpdir)
            if files:
                host.write_text_files(files)
            ret, _, _ = self._call(host,
                                  ['--pretty-print', 'glop.g',
                                   '-o', 'glop2.g'])
            self.assertEqual(0, ret)
            ret, _, _ = self._call(host,
                                   ['--pretty-print', 'glop2.g',
                                    '-o', 'glop3.g'])
            self.assertEqual(0, ret)
            actual_output_files = host.read_text_files(host.getcwd())
            self.assertMultiLineEqual(actual_output_files['glop2.g'],
                                      actual_output_files['glop3.g'])
        finally:
            if tmpdir:
                host.rmtree(tmpdir)
            if orig_wd:
                host.chdir(orig_wd)

    def test_print_ast(self):
        self.check_cmd(['-e', 'grammar = "hello"', '--ast'],
                       returncode=0,
                       out='[\n'
                           '  "rules",\n'
                           '  [\n'
                           '    [\n'
                           '      "rule",\n'
                           '      "grammar",\n'
                           '      [\n'
                           '        "lit",\n'
                           '        "hello"\n'
                           '      ]\n'
                           '    ]\n'
                           '  ]\n'
                           ']\n')

    def test_version(self):
        self.check_cmd(['-V'], returncode=0, out=(glop.tool.VERSION + '\n'),
                       err=None)
        self.check_cmd(['--version'], returncode=0, out=(glop.tool.VERSION + '\n'),
                       err=None)
