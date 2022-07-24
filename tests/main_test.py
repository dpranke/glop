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

import io
import unittest

from glop.host import Host
import glop.tool
from .host_fake import FakeHost


SIMPLE_GRAMMAR = "grammar = anything*:as end -> join('', as) ,"


class InterpreterTestMixin:
    tmpdir = None

    def _write_files(self, host, files):
        for path, contents in list(files.items()):
            host.write_text_file(path, contents)

    def _read_files(self, host, tmpdir):
        out_files = {}
        for f in host.files_under(tmpdir):
            out_files[f] = host.read_text_file(host.join(tmpdir, f))
        return out_files

    def assert_files(self, expected_files, actual_files):
        for k, v in actual_files.items():
            self.assertEqual(expected_files[k], v)
        self.assertEqual(set(actual_files.keys()), set(expected_files.keys()))

    def check_match(self, grammar, input_txt, returncode=0, out=None, err=None):
        host = self._host()
        try:
            self.tmpdir = host.mkdtemp()
            input_path = host.join(self.tmpdir, 'input.txt')
            grammar_path = host.join(self.tmpdir, 'grammar.g')
            host.write_text_file(input_path, input_txt)
            host.write_text_file(grammar_path, grammar)
            args = ['-i', input_path, grammar_path]
            return self._call(host, args, None, returncode, out, err)
        finally:
            if self.tmpdir:
                host.rmtree(self.tmpdir)
                self.tmpdir = None

    def check_cmd(self, args, stdin=None, files=None,
                  returncode=None, out=None, err=None, output_files=None):
        host = self._host()
        orig_wd, tmpdir = None, None
        try:
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()
            host.chdir(tmpdir)
            if files:
                self._write_files(host, files)
            rv = self._call(host, args, stdin, returncode, out, err)
            actual_ret, actual_out, actual_err = rv
            actual_output_files = self._read_files(host, host.getcwd())
        finally:
            if tmpdir:
                host.rmtree(tmpdir)
            if orig_wd:
                host.chdir(orig_wd)

        if output_files:
            self.assert_files(output_files, actual_output_files)
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


class IntegrationTestMixin:
    def _host(self):
        return Host()

    def check_match(self, grammar, input_txt, returncode=0, out=None, err=None):
        host = self._host()
        tmpdir = None
        try:
            tmpdir = host.mkdtemp()
            compiler_argv = [
                host.python_interpreter, glop.tool.__file__,
                '-c', '--main',
                host.join(tmpdir, 'grammar.g'),
                '-o', host.join(tmpdir, 'parser.py'),
                ]

            parser_argv = [
                host.python_interpreter, host.join(tmpdir, 'parser.py'),
                host.join(tmpdir, 'input.txt'),
                ]

            input_path = host.join(tmpdir, 'input.txt')
            grammar_path = host.join(tmpdir, 'grammar.g')
            host.write_text_file(input_path, input_txt)
            host.write_text_file(grammar_path, grammar)

            ret, compiler_out, compiler_err = host.call(compiler_argv)
            host.stdout = io.StringIO()
            host.stderr = io.StringIO()
            ret = glop.tool.main(host, compiler_argv[2:])
            compiler_out = host.stdout.getvalue()
            compiler_err = host.stdout.getvalue()
            self.assertEqual(ret, 0)
            self.assertEqual(compiler_out, '')
            self.assertEqual(compiler_err, '')

            actual_ret, actual_out, actual_err = host.call(parser_argv)
            if returncode is not None:
                self.assertEqual(returncode, actual_ret)
            if out is not None:
                self.assertEqual(str(out), actual_out)
            if err is not None:
                self.assertEqual(str(err), actual_err)
            return actual_ret, actual_out, actual_err
        finally:
            if tmpdir:
                host.rmtree(tmpdir)


class TestGrammarPrettyPrinter(InterpreterTestMixin, unittest.TestCase):
    maxDiff = None

    def test_glop(self):
        h = Host()
        glop_contents = h.read_text_file(
            h.join(h.dirname(h.path_to_host_module()), '..',
                   'grammars', 'glop.g'))

        files = {'glop.g': glop_contents}
        host = self._host()
        orig_wd, tmpdir = None, None
        try:
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()
            host.chdir(tmpdir)
            if files:
                self._write_files(host, files)
            ret, _, _ = self._call(host,
                                  ['--pretty-print', 'glop.g',
                                   '-o', 'glop2.g'])
            self.assertEqual(0, ret)
            ret, _, _ = self._call(host,
                                   ['--pretty-print', 'glop2.g',
                                    '-o', 'glop3.g'])
            self.assertEqual(0, ret)
            actual_output_files = self._read_files(host, host.getcwd())
            self.assertMultiLineEqual(actual_output_files['glop2.g'],
                                      actual_output_files['glop3.g'])
        finally:
            if tmpdir:
                host.rmtree(tmpdir)
            if orig_wd:
                host.chdir(orig_wd)


class ToolTests(InterpreterTestMixin, unittest.TestCase):
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

    def test_no_grammar(self):
        self.check_cmd([], returncode=2)

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


class SharedTestsMixin:
    def test_apply(self):
        self.check_match("""
            grammar = (foo | bar)
            foo     = 'foo'
            bar     = 'bar'
            """, 'foo', 0, '"o"\n', '')

    def test_basic(self):
        self.check_match(SIMPLE_GRAMMAR,
                         'hello, world',
                         returncode=0,
                         out='"hello, world"\n',
                         err='')

    def test_double_quoted_literals(self):
        self.check_match('grammar = "a"+ end ,', 'aa')

    def test_eq(self):
        self.check_match("grammar = 'abc':v ={v} end", 'abcc')
        self.check_match("grammar = 'abc':v ={v} end", 'abccba', returncode=1)

    def test_error_positions(self):
        _, _, err = self.check_match(
            "grammar = 'a'+ '\n' end -> 'ok'",
            'bc', returncode=1)
        self.assertIn('Unexpected "b" at column 1', err)

        # Check that a partial match of a string reports the first char
        # that failed the match, not the first char of the string.
        _, _, err = self.check_match("grammar = 'abc' end -> 'ok'",
                                     'abd', returncode=1)
        self.assertIn('Unexpected "d" at column 3', err)

    def test_escaping(self):
        self.check_match("grammar = '\\'' end -> 'ok'", '\'')
        self.check_match("grammar = '\\n' end -> 'ok'", '\n')
        self.check_match("grammar = '\\\\' end -> 'ok'", '\\')

    def test_capture(self):
        self.check_match("grammar = 'a' {'b'+}:bs 'c' -> bs", 'abbc',
                         out='"bb"\n')

    def test_choice(self):
        self.check_match("grammar = 'foo' | 'bar'", 'foo',
                         0, '"o"\n', '')
        self.check_match("grammar = 'foo' | 'bar'", 'bar',
                         0, '"r"\n', '')

    def disabled_test_left_recursion(self):
        direct = """\
            expr = expr '+' expr
                 | ('0'..'9')+
            """
        self.check_match(direct, '12 + 3', returncode=1)

    def test_no_match(self):
        self.check_match("grammar = 'foo' | 'bar',", 'baz', returncode=1)

    def test_no_trailing_commas_on_rules(self):
        self.check_match("grammar = a b end a = 'a' b = 'b'", 'ab')

    def test_not(self):
        g = """grammar = '"' (~'"' anything)*:as '"' end -> join('', as)"""
        self.check_match(g, '""')
        self.check_match(g, '"hello"', out='"hello"\n')

    def test_opt(self):
        self.check_match("grammar = 'a'? end ,", '')
        self.check_match("grammar = 'a'? end ,", 'a')
        self.check_match("grammar = 'a'? end ,", 'aa', returncode=1)

    def test_plus(self):
        self.check_match("grammar = 'a'+ end", '', returncode=1)
        self.check_match("grammar = 'a'+ end", 'a')
        self.check_match("grammar = 'a'+ end", 'aa')

    def test_pos(self):
        self.check_match("grammar = 'a' {}:p 'b\n' end -> p", 'ab\n', out='1\n')

    def test_pred(self):
        self.check_match("grammar = ?{ true } end", '')

        # Predicates must explicitly evaluate to true or false, rather than just
        # being false-y. This allows pos() to return 0 at the start of string.
        self.check_match("grammar = ?{ 0 } end", '', returncode=1)
        self.check_match("grammar = ?{ false } end", '', returncode=1)

    def test_py_getitem(self):
        self.check_match("grammar = end -> 'bar'[1] ,", '',
                         returncode=0, out='"a"\n')

    def test_py_plus(self):
        self.check_match("grammar = end -> 1 + 1 ,", '',
                         returncode=0, out='2\n')

    def test_star(self):
        self.check_match("grammar = 'a'* end", '')
        self.check_match("grammar = 'a'* end", 'a')
        self.check_match("grammar = 'a'* end", 'aa')

    def test_weird_error_reporting_in_predicates(self):
        # You would think that you'd get 'Unexpected "2" at column 2 here.
        # You don't, because the parser consumes the 2 as part of `anything:x`
        # and there's no good way for the semantic predicate to report what
        # it is looking at, so the parser have to assume the next character
        # is what fails, rather than the character that is actually causing
        # the problem. See https://github.com/dpranke/glop/issues/3 for more
        # on this.
        _, _, err = self.check_match(
            "grammar = (anything:x ?{ is_unicat(x, 'Ll')})* '\n' end -> 'ok'",
            'a23', returncode=1)
        self.assertIn('Unexpected "3" at column 3', err)


class InterpreterTests(unittest.TestCase, InterpreterTestMixin,
        SharedTestsMixin):
    pass


class IntegrationTests(unittest.TestCase, IntegrationTestMixin,
        SharedTestsMixin):
    pass
