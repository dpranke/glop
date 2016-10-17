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
        self.files = {}
        self.written_files = {}

    def basename(self, path):
        return '/'.join(path.split('/')[-1])

    def exists(self, path):
        return path in self.files

    def print_(self, msg, end='\n', stream=None):
        stream = stream or self.stdout
        stream.write(msg + end)
        stream.flush()

    def read(self, path):
        return self.files[path]

    def write(self, path, contents):
        self.files[path] = contents
        self.written_files[path] = contents
