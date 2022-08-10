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

    def check_match(self, grammar, input_txt, returncode=0, out=None, err=None,
                    compiler_returncode=None, memoize=False):
        del compiler_returncode
        host = self._host()
        try:
            self.tmpdir = host.mkdtemp()
            input_path = host.join(self.tmpdir, 'input.txt')
            grammar_path = host.join(self.tmpdir, 'grammar.g')
            host.write_text_file(input_path, input_txt)
            host.write_text_file(grammar_path, grammar)
            args = ['-i', input_path, grammar_path]
            if memoize:
                args += ['--memoize']
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

    def check_match(self, grammar, input_txt, returncode=0, out=None, err=None,
                    compiler_returncode=None, memoize=False):
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
            if memoize:
                compiler_argv += ['--memoize']

            parser_argv = [
                host.python_interpreter, host.join(tmpdir, 'parser.py'),
                host.join(tmpdir, 'input.txt'),
                ]

            input_path = host.join(tmpdir, 'input.txt')
            grammar_path = host.join(tmpdir, 'grammar.g')
            host.write_text_file(input_path, input_txt)
            host.write_text_file(grammar_path, grammar)

            actual_compiler_ret, compiler_out, compiler_err = host.call(
                compiler_argv)
            if compiler_returncode is not None:
                self.assertEqual(actual_compiler_ret, compiler_returncode)
                return actual_compiler_ret, compiler_out, compiler_err

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
    def test_anything(self):
        self.check_match('grammar = anything end', 'a')
        self.check_match('grammar = anything end', '', returncode=1)

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

    def test_capture(self):
        self.check_match("grammar = 'a' {'b'+}:bs 'c' -> bs", 'abbc',
                         out='"bb"\n')

    def test_cat(self):
        self.check_match('grammar = ("a"+):as -> cat(as)',
                         'aaaaa',
                         out='"aaaaa"\n')

    def test_choice(self):
        self.check_match("grammar = 'foo' | 'bar'", 'foo',
                         0, '"o"\n', '')
        self.check_match("grammar = 'foo' | 'bar'", 'bar',
                         0, '"r"\n', '')

    def test_c_style_comments(self):
        self.check_match("grammar = 'a' /* skip */ end", 'a')

    def test_cpp_style_comments(self):
        self.check_match("grammar = 'a' // skip\nend", 'a')

    def test_control_char_in_grammar(self):
        self.check_match("grammar = '\x01' end", '\x01')

    def test_double_quoted_literals(self):
        self.check_match('grammar = "a"+ end ,', 'aa')

    def test_empty(self):
        self.check_match('grammar = "a"+ end |', '')

    def test_eq(self):
        self.check_match("grammar = 'abc':v ={v} end", 'abcc')
        self.check_match("grammar = 'abc':v ={v} end", 'abcd', returncode=1)

    def test_error_positions(self):
        grammar = "grammar = 'a'+ '\n' 'b' end -> ok"
        _, _, err = self.check_match(grammar, 'bc', returncode=1)
        self.assertIn('input.txt:1 Unexpected "b" at column 1', err)

        _, _, err = self.check_match(grammar, 'a\nc', returncode=1)
        self.assertIn('input.txt:2 Unexpected "c" at column 1', err)

        # Check that a partial match of a string reports the first char
        # that failed the match, not the first char of the string.
        _, _, err = self.check_match("grammar = 'abc' end -> 'ok'",
                                     'abd', returncode=1)
        self.assertIn('input.txt:1 Unexpected "d" at column 3', err)

    def test_escaping(self):
        self.check_match("grammar = '\\'' end -> 'ok'", '\'')
        self.check_match("grammar = '\\n' end -> 'ok'", '\n')
        self.check_match("grammar = '\\\\' end -> 'ok'", '\\')

    def test_escape_chars(self):
        self.check_match(r"grammar = '\b\f' end -> 'ok'", '\b\f')

    def test_fn_number(self):
        self.check_match("grammar = -> number('41')", '', out='41\n')
        self.check_match("grammar = -> number('4.1')", '', out='4.1\n')

    def test_fn_xtou(self):
        self.check_match("grammar = ={ xtou('41') } -> 'ok'", 'A')

    def disabled_test_left_recursion(self): # pragma: no cover
        direct = """\
            expr = expr '+' expr
                 | ('0'..'9')+
            """
        self.check_match(direct, '12 + 3', returncode=1)

    def test_ll_dec(self):
        self.check_match("grammar = -> 14", '14')

    def test_ll_hex(self):
        self.check_match("grammar = -> 0x0e", '14')

    def test_memoize(self):
        grammar = '''
            grammar = foo 'b' | foo 'c'
            
            foo     = 'a'
            '''
        self.check_match(grammar, 'ac', memoize=True)

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

    def test_ll_paren(self):
        self.check_match("grammar = -> (1 + 2)", '3')

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

    def test_range(self):
        self.check_match("grammar = 'a'..'z' end", 'c')

    def test_star(self):
        self.check_match("grammar = 'a'* end", '')
        self.check_match("grammar = 'a'* end", 'a')
        self.check_match("grammar = 'a'* end", 'aa')

    def test_syntax_errors_in_grammar(self):
        # test_error_positions, above, tests what happens if you get
        # errors in the input. This routine tests error handling in
        # the parsing of the grammar itself.
        _, _, err = self.check_match("grammar\nrule = 'a'+ end", 'a',
                                     returncode=1,
                                     compiler_returncode=1)
        self.assertIn('grammar.g:2 Unexpected "r" at column 1', err)

        _, _, err = self.check_match('grammar = "', '', returncode=1,
                                     compiler_returncode=1)
        self.assertIn('grammar.g:1 Unexpected end of input at column 12', err)

    def test_unicode_long_escape_in_strings(self):
        # U+1f600 == 'grinning face'
        self.check_match(r'grammar = "\U0001f600" end', '\U0001f600')

    def test_unicode_short_escape_in_strings(self):
        # U+212b == angstrom sign
        self.check_match(r'grammar = "\u212b" end', '\u212b')

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


class LeftRecMixin:
    # The two grammars are from "Left Recursion in Parsing 
    # Expression Grammars" by Sergio Medeiros, Fabio Mascarenhas,
    # and Roberto Ierusalimschy, but converted into glop's syntax
    # and returning an AST rather than just being a recognizer.

    def test_both_left_and_right_recursion(self):
        grammar = """
            grammar = expr           
            expr    = expr '*' expr -> [_1, '*', _3]
                    | expr '+' expr -> [_1, '+', _3]
                    | expr '-' expr -> [_1, '-', _3]
                    | {num}         -> _1

            num     = ('0'..'9')+
            """
        # Note that this result is right-associative; when there is
        # both left- and right-recursion, right always wins.
        # TODO: This might not be the behavior we really want.
        self.check_match(grammar, '3+4+5',
                         out='["3", "+", ["4", "+", "5"]]\n')

    def test_direct_left_recursion(self):
        grammar = """
            grammar = expr

            expr    = expr '*' {num} -> [_1, '*', _3]
                    | expr '+' {num} -> [_1, '+', _3]
                    | expr '-' {num} -> [_1, '-', _3]
                    | {num}          -> _1

            num     = ('0'..'9')+
            """

        # This should match and produce a left-associative parse tree.
        self.check_match(grammar, '3+4-5',
                         out='[["3", "+", "4"], "-", "5"]\n')

    def test_indirect_left_recursion(self):
        grammar = """
            grammar = L 
            
            L       = P '.x'
                    | 'x'
            
            P       = P '(n)'
                    | L
            """

        self.check_match(grammar, 'x')
        self.check_match(grammar, 'x(n)(n).x(n).x')
        self.check_match(grammar, 'x.x')
        self.check_match(grammar, 'x(n).x')


class InterpreterTests(unittest.TestCase, InterpreterTestMixin,
        SharedTestsMixin, LeftRecMixin):
    pass

class IntegrationTests(unittest.TestCase, IntegrationTestMixin,
        SharedTestsMixin, LeftRecMixin):
    pass
