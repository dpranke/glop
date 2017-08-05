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


class FakeHost(object):
    def __init__(self):
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.sep = '/'
        self.dirs = set([])
        self.files = {}
        self.written_files = {}

    def abspath(self, *comps):
        relpath = self.join(*comps)
        if relpath.startswith('/'):
            return relpath
        return self.join(self.cwd, relpath)

    def basename(self, path):
        return '/'.join(path.split('/')[-1])

    def exists(self, path):
        return path in self.files

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

        # Handle ./
        p = p.replace('/./', '/')

        # Handle ../
        while '/..' in p:
            comps = p.split('/')
            idx = comps.index('..')
            comps = comps[:idx-1] + comps[idx+1:]
            p = '/'.join(comps)
        return p

    def print_(self, msg, end='\n', stream=None):
        stream = stream or self.stdout
        stream.write(msg + end)
        stream.flush()

    def read(self, path):
        return self.files[path]

    def write(self, path, contents):
        self.files[path] = contents
        self.written_files[path] = contents

    def rmtree(self, *comps):
        path = self.abspath(*comps)
        for f in self.files:
            if f.startswith(path):
                self.files[f] = None
                self.written_files[f] = None
        self.dirs.remove(path)

    def rmtree(self, path):
        path = self.abspath(*comps)
        for f in self.files:
            if f.startswith(path):
                self.files[f] = None
                self.written_files[f] = None
        self.dirs.remove(path)

