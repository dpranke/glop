import os
import sys


class Host(object):
    stderr = sys.stderr
    stdin = sys.stdin
    stdout = sys.stdout

    def exists(self, *comps):
        return os.path.exists(self.join(*comps))

    def join(self, *comps):
        return os.path.join(*comps)

    def print_err(self, msg, end='\n'):
        self.stderr.write(str(msg) + end)

    def print_out(self, msg, end='\n'):
        self.stdout.write(str(msg) + end)
        self.stdout.flush()

    def read(self, *comps):
        path = self.join(*comps)
        with open(path) as f:
            return f.read()

    def write(self, path, contents):
        with open(path, 'w') as f:
            f.write(contents)
