# Copyright 2014 Dirk Pranke
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

import os
import sys


class Host(object):
    python_interpreter = sys.executable
    stderr = sys.stderr
    stdin = sys.stdin
    stdout = sys.stdout

    def basename(self, path):
        return os.path.basename(path)

    def exists(self, path):
        return os.path.exists(path)

    def print_(self, msg, end='\n', stream=None):
        stream = stream or self.stdout
        stream.write(str(msg) + end)
        stream.flush()

    def read_text_file(self, path):
        with open(path) as f:
            return f.read().decode('utf8')

    def splitext(self, path):
        return os.path.splitext(path)

    def write_text_file(self, path, contents):
        with open(path, 'w') as f:
            f.write(contents.encode('utf8'))
