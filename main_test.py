import unittest

from host_fake import FakeHost
from main import main


SIMPLE_GRAMMAR = "grammar = anything*:as end -> ''.join(as) ,"


class TestMain(unittest.TestCase):
    def _host(self):
        return FakeHost()

    def _call(self, host, args, returncode=None, out=None, err=None):
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

    def _write_files(self, host, files):
        for path, contents in list(files.items()):
            host.write(path, contents)

    def _read_files(self, host, tmpdir):
        out_files = {}
        for f in host.files_under(tmpdir):
            out_files[f] = host.read(tmpdir, f)
        return out_files

    def assert_files(self, host, expected_files):
        read_files = self._read_files(host, host.cwd)
        for k, v in read_files.items():
            self.assertEqual(expected_files[k], v)
        self.assertEqual(set(read_files.keys()), set(expected_files.keys()))

    def check_match(self, grammar, input_txt, returncode=0, out='', err=''):
        host = self._host()
        args = ['-c', grammar, '-i', input_txt]
        self._call(host, args, returncode, out, err)

    def check_cmd(self, args, files=None, returncode=None, out=None, err=None,
                  output_files=None):
        host = self._host()
        if files:
            self._write_files(host, files)
        actual_ret, actual_out, actual_err = self._call(host, args,
                                                        returncode, out, err)
        if output_files:
            self.assert_files(host, output_files)
        return actual_ret, actual_out, actual_err

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
                         err="'a'\n")
        self.check_match("grammar = 'a'+ end ,", 'a')
        self.check_match("grammar = 'a'+ end ,", 'aa')

    def test_opt(self):
        self.check_match("grammar = 'a'? end ,", '')
        self.check_match("grammar = 'a'? end ,", 'a')
        self.check_match("grammar = 'a'? end ,", 'aa', returncode=1,
                         err='the end\n')

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
                         returncode=1, err='pred returned False\n')

    def test_py_plus(self):
        self.check_match("grammar = end -> 1 + 1 ,", '',
                         returncode=0, out='2')

    def test_py_getitem(self):
        self.check_match("grammar = end -> 'bar'[1] ,", '',
                         returncode=0, out='a')

    def test_files(self):
        files = {
            'simple.g': SIMPLE_GRAMMAR,
            'input.txt': 'hello, world\n',
        }
        out_files = files.copy()
        out_files['output.txt'] = 'hello, world\n'
        self.check_cmd(['-g', 'simple.g', '-o', 'output.txt', 'input.txt'],
                       files=files, returncode=0, out='', err='',
                       output_files=out_files)

    def test_no_grammar(self):
        self.check_cmd([], returncode=1,
                       err='must specify one of -c or -g\n')

    def test_grammar_file_not_found(self):
        self.check_cmd(['-g', 'missing.pom'], returncode=1,
                       err='grammar file "missing.pom" not found\n')

    def test_input_file_not_found(self):
        self.check_cmd(['-c', '', 'missing.txt'], returncode=1,
                       err='input file "missing.txt" not found\n')
