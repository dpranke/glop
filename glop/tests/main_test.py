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

from glop.host import Host
from glop.fakes.host_fake import FakeHost
from glop.main import main, VERSION


SIMPLE_GRAMMAR = "grammar = anything*:as end -> ''.join(as) ,"


class CheckMixin(object):
    def _write_files(self, host, files):
        for path, contents in list(files.items()):
            host.write(path, contents)

    def _read_files(self, host, tmpdir):
        out_files = {}
        for f in host.files_under(tmpdir):
            out_files[f] = host.read(tmpdir, f)
        return out_files

    def assert_files(self, expected_files, actual_files):
        for k, v in actual_files.items():
            self.assertEqual(expected_files[k], v)
        self.assertEqual(set(actual_files.keys()), set(expected_files.keys()))

    def check_match(self, grammar, input_txt, returncode=0, out='', err=''):
        host = self._host()
        try:
            tmpdir = host.mkdtemp()
            fname = host.join(tmpdir, 'input.txt')
            host.write(fname, input_txt)
            args = ['-i', '-e', grammar, fname]
            self._call(host, args, None, returncode, out, err)
        finally:
            host.rmtree(tmpdir)

    def check_cmd(self, args, stdin=None, files=None,
                  returncode=None, out=None, err=None, output_files=None):
        host = self._host()
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
            host.rmtree(tmpdir)
            host.chdir(orig_wd)

        if output_files:
            self.assert_files(output_files, actual_output_files)
        return actual_ret, actual_out, actual_err


class UnitTestMixin(object):
    use_compiled_grammar_parser = False

    def _host(self):
        return FakeHost()

    def _call(self, host, args, stdin=None,
              returncode=None, out=None, err=None):
        if stdin is not None:
            host.stdin.write(stdin)
            host.stdin.seek(0)
        if self.use_compiled_grammar_parser:
            args = ['--use-compiled-grammar-parser'] + args
        actual_ret = main(host, args)
        actual_out = host.stdout.getvalue()
        actual_err = host.stderr.getvalue()
        if returncode is not None:
            self.assertEqual(returncode, actual_ret)
        if out is not None:
            self.assertEqual(out, actual_out)
        if err is not None:
            self.assertEqual(err, actual_err)
        return actual_ret, actual_out, actual_err


class TestGrammarPrinter(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_glop(self):
        h = Host()
        glop_contents = h.read(h.join(h.dirname(h.path_to_host_module()),
                                      '..', 'grammars', 'glop.g'))
        files = {'glop.g': glop_contents}
        output_files = files.copy()
        output_files['new_glop.g'] = glop_contents
        self.check_cmd(['-p', 'glop.g', '-o', 'new_glop.g'],
                       files=files, returncode=0, output_files=output_files)

    def test_pred(self):
        # semantic predicates aren't used in the main glop grammar,
        # so we test those separately.
        files = {'test.g': "grammar = ?(1) -> 'pass',\n"}
        output_files = files.copy()
        output_files['new_test.g'] = files['test.g']
        self.check_cmd(['-p', 'test.g', '-o', 'new_test.g'],
                       files=files, returncode=0, output_files=output_files)


class UnitTestMain(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_ctrl_c(self):
        host = FakeHost()

        def raise_ctrl_c(*_comps):
            raise KeyboardInterrupt

        host.read = raise_ctrl_c
        host.write('simple.g', SIMPLE_GRAMMAR)

        self._call(host, ['-i', 'simple.g'], returncode=130,
                   out='', err='Interrupted, exiting ..\n')


class TestMain(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_files(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
            'input.txt': 'hello, world\n',
        }
        out_files = files.copy()
        out_files['output.txt'] = 'hello, world\n'
        self.check_cmd(['-i', '-o', 'output.txt', 'simple.g', 'input.txt'],
                       files=files, returncode=0, out='', err='',
                       output_files=out_files)

    def test_no_grammar(self):
        self.check_cmd([], returncode=1,
                       err='Must specify a grammar file or a string with -e.\n')

    def test_grammar_file_not_found(self):
        self.check_cmd(['-i', 'missing.g'], returncode=1,
                       err='grammar file "missing.g" not found\n')

    def test_input_on_stdin(self):
        self.check_cmd(['-i', '-e', SIMPLE_GRAMMAR], stdin="hello, world\n",
                       returncode=0, out="hello, world\n", err='')

    def test_print_grammar_to_out(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        out_files = files.copy()
        self.check_cmd(['-p', 'simple.g'], files=files,
                       returncode=0,
                       out="grammar = anything*:as end -> ''.join(as),\n",
                       output_files=out_files)

    def test_print_bad_grammar(self):
        self.check_cmd(['-p', '-e', 'grammar ='],
                       returncode=1, out='',
                       err='-e:1:2 expecting the end\n')

    def test_parse_bad_grammar(self):
        self.check_cmd(['-i', '-e', 'grammar ='],
                       returncode=1, out='',
                       err='-e:1:2 expecting the end\n')

    def test_version(self):
        self.check_cmd(['-V'], returncode=0, out=(VERSION + '\n'),
                       err=None)
        self.check_cmd(['--version'], returncode=0, out=(VERSION + '\n'),
                       err=None)


class TestInterpreter(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_basic(self):
        self.check_match(SIMPLE_GRAMMAR,
                         'hello, world',
                         returncode=0,
                         out='hello, world',
                         err='')

    def test_no_match(self):
        self.check_match("grammar = 'foo' | 'bar',", 'baz',
                         1, '', 'no choice matched\n')

    def test_star(self):
        self.check_match("grammar = 'a'* end ,", '')
        self.check_match("grammar = 'a'* end ,", 'a')
        self.check_match("grammar = 'a'* end ,", 'aa')

    def test_plus(self):
        self.check_match("grammar = 'a'+ end ,", '', returncode=1,
                         err='no choice matched\n')
        self.check_match("grammar = 'a'+ end ,", 'a')
        self.check_match("grammar = 'a'+ end ,", 'aa')

    def test_opt(self):
        self.check_match("grammar = 'a'? end ,", '')
        self.check_match("grammar = 'a'? end ,", 'a')
        self.check_match("grammar = 'a'? end ,", 'aa', returncode=1,
                         err='no choice matched\n')

    def test_choice(self):
        self.check_match("grammar = 'foo' | 'bar',", 'foo',
                         0, 'foo', '')
        self.check_match("grammar = 'foo' | 'bar',", 'bar',
                         0, 'bar', '')

    def test_apply(self):
        self.check_match("""
            grammar = (foo | bar) end ,
            foo     = 'foo' ,
            bar     = 'bar' ,
            """, 'foo')

    def test_not(self):
        g = """grammar = '"' (~'"' anything)*:as '"' end -> ''.join(as) ,"""
        self.check_match(g, '""')
        self.check_match(g, '"hello"', out='hello')

    def test_pred(self):
        self.check_match("grammar = ?( 1 ) end ,", '')
        self.check_match("grammar = ?( 0 ) end ,", '',
                         returncode=1, err='no choice matched\n')

    def test_py_plus(self):
        self.check_match("grammar = end -> 1 + 1 ,", '',
                         returncode=0, out='2')

    def test_py_getitem(self):
        self.check_match("grammar = end -> 'bar'[1] ,", '',
                         returncode=0, out='a')


class TestCompiledParser(TestInterpreter):
    use_compiled_grammar_parser = True


if __name__ == '__main__':
    unittest.main()
