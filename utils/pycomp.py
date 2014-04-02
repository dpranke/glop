#!/usr/bin/python
#
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

import atexit
import sys


def main():
    if '-MMD' in sys.argv and '-MF' in sys.argv:
        sys.argv.remove('-MMD')
        idx = sys.argv.index('-MF')
        deps_file = sys.argv[idx + 1]
        sys.argv = sys.argv[:idx] + sys.argv[idx + 2:]
        atexit.register(write_deps, deps_file, sys.argv[1])

    fname = sys.argv[1]
    sys.argv = sys.argv[1:]
    __import__(fname.replace('/', '.').replace('.py', ''))


def write_deps(deps_file, source_file):
    deps = [source_file]
    for m in list(sys.modules.values()):
        mf = getattr(m, '__file__', None)
        if mf and (not mf.startswith('/System') and
                   not mf.startswith('/Library')):
            deps.append(mf.replace('.pyc', '.py').replace(' ', '\\ '))

    with open(deps_file, 'w') as df:
        df.write("%s : %s\n" % (source_file.replace('.py', '.pyc'),
                                ' '.join(deps)))


if __name__ == '__main__':
    main()
