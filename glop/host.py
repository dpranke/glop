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

import os
import shutil
import subprocess
import sys
import tempfile


_path_to_host_module = os.path.abspath(__file__)


class Host:
    python_interpreter = sys.executable
    stderr = sys.stderr
    stdin = sys.stdin
    stdout = sys.stdout

    def basename(self, path):
        return os.path.basename(path)

    def call(self, argv, stdin=None, env=None):
        if stdin:
            stdin_pipe = subprocess.PIPE
        else:
            stdin_pipe = None
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=stdin_pipe,
                                env=env)
        if stdin:
            proc.stdin.write(stdin.encode('utf-8'))
        stdout, stderr = proc.communicate()

        # pylint type checking bug - pylint: disable=E1103
        return (proc.returncode,
                stdout.decode('utf-8'),
                stderr.decode('utf-8'))

    def chdir(self, *comps):
        return os.chdir(self.join(*comps))

    def dirname(self, *comps):
        return os.path.dirname(self.join(*comps))

    def exists(self, path):
        return os.path.exists(path)

    def getcwd(self):
        return os.getcwd()

    def join(self, *comps):
        return os.path.join(*comps)

    def make_executable(self, path):
        os.chmod(path, 0o755)

    def mkdtemp(self, **kwargs):
        return tempfile.mkdtemp(**kwargs)

    def path_to_host_module(self):
        return _path_to_host_module

    def print_(self, msg, end='\n', stream=None):
        stream = stream or self.stdout
        stream.write(msg + end)
        stream.flush()

    def read_text_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def rmtree(self, path):
        shutil.rmtree(path, ignore_errors=True)

    def splitext(self, path):
        return os.path.splitext(path)

    def write_text_file(self, path, contents):
        with open(path, 'wb') as f:
            f.write(contents.encode('utf-8'))
