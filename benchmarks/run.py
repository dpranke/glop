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

from glop.ir import Grammar
from glop.compiler import Compiler
from glop.parser import Parser


def main():
    DEFAULT_DURATION = 10
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--memoize', action='store_true')
    arg_parser.add_argument('-d', '--duration', type=float,
         default=DEFAULT_DURATION,
         help='# of seconds to run for (default is %(default)s)')
    args = arg_parser.parse_args()
    path = os.path.join(REPO_DIR, 'grammars', 'glop.g')
    with open(path) as fp:
        contents = fp.read()

    iterations = 0
    scope = {}
    parser = Parser(contents, path)
    ast, err, nextpos = parser.parse()
    if err:
        print(err, file=sys.stderr)
        return 1
    grammar = Grammar(ast)
    comp = Compiler(grammar, 'Glop', main_wanted=False, memoize=args.memoize)
    compiled_text, err = comp.compile()
    if err:
        print(err, file=sys.stderr)
        return 1
    exec compiled_text in scope
    parser_cls = scope['Glop']

    start_time = time.time()
    stop_time = time.time()
    while stop_time - start_time < args.duration:
        parser = parser_cls(contents, path)
        ast, err, nextpos = parser.parse()
        if err:
            print(err, file=sys.stderr)
            return 1
        grammar = Grammar(ast)
        comp = Compiler(grammar, 'Glop', main_wanted=False, memoize=False)
        _, err = comp.compile()
        if err:
            print(err, file=sys.stderr)
            return 1
        stop_time = time.time()
        iterations += 1

    print('%.1f iterations' % (iterations * DEFAULT_DURATION /
                               (stop_time - start_time)))

    return 0


if __name__ == '__main__':
    sys.exit(main())
