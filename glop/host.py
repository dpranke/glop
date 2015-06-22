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

import os
import shutil
import subprocess
import sys
import tempfile


class Host(object):
    python_interpreter = sys.executable
    stderr = sys.stderr
    stdin = sys.stdin
    stdout = sys.stdout

    def call(self, args, stdin=None):
        proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=stdin)
        return proc.returncode, stdout, stderr

    def chdir(self, *comps):
        return os.chdir(self.join(*comps))

    def dirname(self, *comps):
        return os.path.dirname(self.join(*comps))

    def exists(self, *comps):
        return os.path.exists(self.join(*comps))

    def files_under(self, top):
        all_files = []
        for root, _, files in os.walk(top):
            for f in files:
                relpath = self.relpath(os.path.join(root, f), top)
                all_files.append(relpath)
        return all_files

    def getcwd(self):
        return os.getcwd()

    def join(self, *comps):
        return os.path.join(*comps)

    def mkdtemp(self, **kwargs):
        return tempfile.mkdtemp(**kwargs)

    def print_err(self, msg, end='\n'):
        self.stderr.write(str(msg) + end)

    def print_out(self, msg, end='\n'):
        self.stdout.write(str(msg) + end)
        self.stdout.flush()

    def read(self, *comps):
        path = self.join(*comps)
        with open(path) as f:
            return f.read()

    def relpath(self, path, start):
        return os.path.relpath(path, start)

    def rmtree(self, path):
        shutil.rmtree(path, ignore_errors=True)

    def write(self, path, contents):
        with open(path, 'w') as f:
            f.write(contents)

    def path_to_host_module(self):
        return os.path.abspath(__file__)
