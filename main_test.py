import unittest

from host_fake import FakeHost
from main import main


class TestMain(unittest.TestCase):
    def _host(self):
        return FakeHost()

    def check_cmd(self, cmd, input_txt, returncode=None, out=None, err=None):
        host = self._host()
        args = ['-c', cmd, '-i', input_txt]
        actual_ret = main(host, args)
        if returncode is not None:
            self.assertEqual(returncode, actual_ret)
        if out is not None:
            actual_out = host.stdout.getvalue()
            self.assertEqual(out, actual_out)
        if err is not None:
            actual_err = host.stderr.getvalue()
            self.assertEqual(err, actual_err)

    def test_basic(self):
        self.check_cmd("grammar = anything*:as -> ''.join(as) ,",
                       'hello, world',
                       returncode=0,
                       out='hello, world',
                       err='')
