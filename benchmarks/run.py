#!/usr/bin/env python
# Copyright 2017 Google Inc. All rights reserved.
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

from __future__ import print_function

import argparse
import os
import sys
import time


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_DIR  = os.path.dirname(THIS_DIR)

if not REPO_DIR in sys.path:
    sys.path.insert(0, REPO_DIR)

from glop.parser import Parser
from glop.analyzer import Analyzer
from glop.interpreter import Interpreter


def main():
    DEFAULT_DURATION = 10
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--duration', type=float,
         default=DEFAULT_DURATION,
         help='# of seconds to run for (default is %(default)s)')
    args = arg_parser.parse_args()
    path = os.path.join(REPO_DIR, 'grammars', 'glop.g')
    with open(path) as fp:
        contents = fp.read()

    start_time = time.time()
    stop_time = time.time()
    iterations = 0
    while stop_time - start_time < args.duration:
        parser = Parser(contents, path)
        ast, err, nextpos = parser.parse()
        if err:
            print(err, stream=sys.stderr)
            return 1
        grammar = Analyzer(ast).analyze()
        out, err, nextpos = Interpreter(grammar).interpret(contents, path)
        if err:
            print(err, stream=sys.stderr)
            return 1
        stop_time = time.time()
        iterations += 1

    print('%.1f iterations' % (iterations * DEFAULT_DURATION /
                               (stop_time - start_time)))

    return 0


if __name__ == '__main__':
    sys.exit(main())
