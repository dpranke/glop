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
        self.last_tmpdir = None
        self.current_tmpno = 0
        self.cwd = '/tmp'

    def abspath(self, *comps):
        relpath = self.join(*comps)
        if relpath.startswith('/'):
            return relpath
        return self.join(self.cwd, relpath)

    def chdir(self, *comps):
        path = self.join(*comps)
        self.cwd = path

    def dirname(self, path):
        return '/'.join(path.split('/')[:-1])

    def exists(self, *comps):
        path = self.join(self.cwd, *comps)
        return path in self.files or path in self.dirs

    def files_under(self, top):
        files = []
        for f in self.files:
            if self.files[f] is not None and f.startswith(top):
                files.append(self.relpath(f, top))
        return files

    def getcwd(self):
        return self.cwd

    def join(self, *comps):
        p = ''
        for c in comps:
            if c.startswith('/'):
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

    def mkdtemp(self, suffix='', prefix='tmp', dir=None, **_kwargs):
        if dir is None:
            dir = self.sep + '__im_tmp'
        curno = self.current_tmpno
        self.current_tmpno += 1
        self.last_tmpdir = self.join(dir, '%s_%u_%s' % (prefix, curno, suffix))
        return self.last_tmpdir

    def print_err(self, msg, end='\n'):
        self.stderr.write(msg + end)

    def print_out(self, msg, end='\n'):
        self.stdout.write(msg + end)

    def read(self, *comps):
        # For some reason, pylint complains if someone overrides
        # an instance method directly, which we do in
        # main_test.UnitTestMain.test_ctrl_c.
        # pylint: disable=E0202
        return self.files[self.abspath(*comps)]

    def relpath(self, path, start):
        return path.replace(start + '/', '')

    def rmtree(self, *comps):
        path = self.abspath(*comps)
        for f in self.files:
            if f.startswith(path):
                self.files[f] = None
                self.written_files[f] = None

    def write(self, path, contents):
        full_path = self.abspath(path)
        self.maybe_mkdir(self.dirname(full_path))
        self.files[full_path] = contents
        self.written_files[full_path] = contents
