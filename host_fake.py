# FIXME: make this work w/ python3.
from StringIO import StringIO


class FakeHost(object):
    # "too many instance attributes" pylint: disable=R0902
    # "redefining built-in" pylint: disable=W0622

    def __init__(self):
        self.stdin = StringIO()
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.sep = '/'
        self.dirs = set([])
        self.files = {}
        self.written_files = {}
        self.cwd = '/'

    def abspath(self, *comps):
        relpath = self.join(*comps)
        if relpath.startswith('/'):
            return relpath
        return self.join(self.cwd, relpath)

    def dirname(self, path):
        return '/'.join(path.split('/')[:-1])

    def exists(self, *comps):
        path = self.join(self.cwd, *comps)
        return path in self.files or path in self.dirs

    def join(self, *comps):
        p = ''
        for c in comps:
            if c in ('', '.'):
                continue
            elif c.startswith('/'):
                p = c
            elif p:
                p += '/' + c
            else:
                p = c
        return p

    def maybe_mkdir(self, *comps):
        path = self.join(*comps)
        if not path in self.dirs:
            self.dirs.add(path)

    def print_err(self, msg, end='\n'):
        self.stderr.write(msg + end)

    def print_out(self, msg, end='\n'):
        self.stdout.write(msg + end)

    def read(self, *comps):
        return self.files[self.abspath(*comps)]

    def write(self, path, contents):
        full_path = self.abspath(path)
        self.maybe_mkdir(self.dirname(full_path))
        self.files[full_path] = contents
        self.written_files[full_path] = contents
