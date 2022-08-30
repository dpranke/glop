# Copyright 2014 Dirk Pranke.
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


class FakeHost:
    def __init__(self):
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.sep = '/'
        self.dirs = set([])
        self.files = {}
        self.written_files = {}
        self.last_tmpdir = None
        self.current_tmpno = 0
        self.cwd = '/tmp'

    def basename(self, path):
        return path.split('/')[-1].split('.')[0]

    def chdir(self, *comps):
        self.cwd = self.join(self.cwd, *comps)

    def dirname(self, path):
        return '/'.join(path.split('/')[:-1])

    def exists(self, path):
        return self._abspath(path) in self.files

    def files_under(self, top):
        # This is only used by test code, so there's no analog in host.py.
        files = []
        top = self._abspath(top)
        for path, contents in self.files.items():
            if contents is not None and path.startswith(top):
                files.append(self._relpath(path, top))
        return files

    def getcwd(self):
        # This is only used by test code, so there's no analog in host.py.
        return self.cwd

    def join(self, *comps):
        # This implementation has code to handle some situations that
        # don't arise in glop's tests, but we've left the code in for
        # completeness sake and so we're not surprised if some test code
        # actually starts to need this. It's not a lot of code.
        p = ''
        for c in comps:
            if c in ('', '.'):  # pragma: no cover
                continue
            if c.startswith('/'):
                p = c
            elif p:
                p += '/' + c
            else:
                p = c

        # Handle ./
        p = p.replace('/./', '/')

        # Handle ../
        while '/..' in p:  # pragma: no cover
            comps = p.split('/')
            idx = comps.index('..')
            comps = comps[:idx-1] + comps[idx+1:]
            p = '/'.join(comps)
        return p

    def make_executable(self, path):
        pass

    def mkdtemp(self, suffix='', prefix='tmp', directory=None, **_kwargs):
        if directory is None:
            directory = self.sep + '__im_tmp'
        curno = self.current_tmpno
        self.current_tmpno += 1
        self.last_tmpdir = self.join(directory,
            '%s_%u_%s' % (prefix, curno, suffix))
        self.dirs.add(self.last_tmpdir)
        return self.last_tmpdir

    def print_(self, msg, end='\n', stream=None):
        stream = stream or self.stdout
        stream.write(msg + end)
        stream.flush()

    def read_text_file(self, *comps):
        return self.files[self._abspath(*comps)]

    def read_text_files(self, directory):
        # This is used only in test code, so there's no analog in host.py
        out_files = {}
        for f in self.files_under(directory):
            out_files[f] = self.read_text_file(self.join(directory, f))
        return out_files

    def rmtree(self, *comps):
        path = self._abspath(*comps)
        for f in self.files:
            if f.startswith(path):
                self.files[f] = None
                self.written_files[f] = None
        self.dirs.remove(path)

    def splitext(self, path):
        return path.split('.')

    def write_text_file(self, path, contents):
        full_path = self._abspath(path)
        self._maybe_mkdir(self.dirname(full_path))
        self.files[full_path] = contents
        self.written_files[full_path] = contents

    def write_text_files(self, files):
        # This is used only in test code, so there's no analog in host.py
        for path, contents in list(files.items()):
            self.write_text_file(path, contents)

    def _abspath(self, *comps):
        relpath = self.join(*comps)
        if relpath.startswith('/'):
            return relpath
        return self.join(self.cwd, relpath)

    def _maybe_mkdir(self, *comps):
        # This is only used by test code, so there's no analog in host.py.
        path = self._abspath(self.join(*comps))
        if path not in self.dirs:
            self.dirs.add(path)

    def _relpath(self, path, start):
        return path.replace(start + '/', '')
