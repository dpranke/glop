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

from glop.fakes.host_fake import FakeHost
from glop.host import Host
from glop.main import main, VERSION


SIMPLE_GRAMMAR = "grammar = anything*:as end -> ''.join(as) ,"


class CheckMixin(object):
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
            tmpdir = host.mkdtemp()
            input_path = host.join(tmpdir, 'input.txt')
            grammar_path = host.join(tmpdir, 'grammar.g')
            host.write_text_file(input_path, input_txt)
            host.write_text_file(grammar_path, grammar)
            args = ['-i', input_path, grammar_path]
            self._call(host, args, None, returncode, out, err)
        finally:
            host.rmtree(tmpdir)

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


class UnitTestMixin(object):
    def _host(self):
        return FakeHost()

    def _call(self, host, args, stdin=None,
              returncode=None, out=None, err=None):
        if stdin is not None:
            host.stdin.write(unicode(stdin))
            host.stdin.seek(0)
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


class TestGrammarPrettyPrinter(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_glop(self):
        h = Host()
        glop_contents = h.read_text_file(
            h.join(h.dirname(h.path_to_host_module()), '..',
                   'grammars', 'glop.g'))
        files = {'glop.g': glop_contents}
        output_files = files.copy()
        output_files['new_glop.g'] = glop_contents
        self.check_cmd(['--pretty-print', 'glop.g', '-o', 'new_glop.g'],
                       files=files, returncode=0, output_files=output_files)



class UnitTestMain(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_ctrl_c(self):
        host = FakeHost()

        def raise_ctrl_c(*_comps):
            raise KeyboardInterrupt

        host.read_text_file = raise_ctrl_c
        host.write_text_file('simple.g', SIMPLE_GRAMMAR)

        self._call(host, ['simple.g'], returncode=130,
                   out='', err='Interrupted, exiting ...\n')


class TestMain(UnitTestMixin, CheckMixin, unittest.TestCase):
    def test_files(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
            'input.txt': 'hello, world\n',
        }
        out_files = files.copy()
        out_files['output.txt'] = 'hello, world\n'
        self.check_cmd(['-i', 'input.txt', '-o', 'output.txt',
                        'simple.g'],
                       files=files, returncode=0, out='', err='',
                       output_files=out_files)

    def test_no_grammar(self):
        self.check_cmd([], returncode=2)

    def test_grammar_file_not_found(self):
        self.check_cmd(['missing.g'], returncode=1,
                       err='Error: no such file: "missing.g"\n')

    def test_input_on_stdin(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        self.check_cmd(['simple.g'], stdin="hello, world\n",
                       files=files, returncode=0, out="hello, world\n", err='')

    def test_pretty_print(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
        }
        out_files = files.copy()
        self.check_cmd(['-p', 'simple.g'], files=files,
                       returncode=0,
                       out="grammar = anything*:as end -> ''.join(as),\n",
                       output_files=out_files)

    def test_parse_bad_grammar(self):
        files = {
            'bad.g': 'grammar =',
        }
        self.check_cmd(['bad.g'], files=files,
                       returncode=1, out='', err=None)

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
        self.check_match("grammar = 'foo' | 'bar',", 'baz', returncode=1)

    def test_star(self):
        self.check_match("grammar = 'a'* end ,", '')
        self.check_match("grammar = 'a'* end ,", 'a')
        self.check_match("grammar = 'a'* end ,", 'aa')

    def test_plus(self):
        self.check_match("grammar = 'a'+ end ,", '', returncode=1)
        self.check_match("grammar = 'a'+ end ,", 'a')
        self.check_match("grammar = 'a'+ end ,", 'aa')

    def test_opt(self):
        self.check_match("grammar = 'a'? end ,", '')
        self.check_match("grammar = 'a'? end ,", 'a')
        self.check_match("grammar = 'a'? end ,", 'aa', returncode=1)

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
        self.check_match("grammar = ?( 0 ) end ,", '', returncode=1)

    def test_py_plus(self):
        self.check_match("grammar = end -> 1 + 1 ,", '',
                         returncode=0, out='2')

    def test_py_getitem(self):
        self.check_match("grammar = end -> 'bar'[1] ,", '',
                         returncode=0, out='a')

    def test_escaping(self):
        self.check_match(r"grammar = '\'' end -> 'ok',", '\'')
        self.check_match(r"grammar = '\n' end -> 'ok',", '\n')
        self.check_match(r"grammar = '\\\'' end -> 'ok',", '\\\'')
        self.check_match(r"grammar = '\\' end -> 'ok',", '\\')

    def test_double_quoted_literals(self):
        self.check_match('grammar = "a"+ end ,', 'aa')


if __name__ == '__main__':
    unittest.main()
