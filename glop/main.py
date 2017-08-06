# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
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

import argparse
import json
import os
import sys

d = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if not d in sys.path:
    sys.path.append(d)

from glop.analyzer import Analyzer
from glop.compiler import Compiler
from glop.printer import Printer
from glop.host import Host
from glop.interpreter import Interpreter
from glop.parser import Parser
from glop.version import VERSION


def main(host=None, argv=None):
    host = host or Host()

    arg_parser = argparse.ArgumentParser(prog='glop')
    arg_parser.add_argument('-o', '--output', metavar='file',
                            help='path to write output to')
    arg_parser.add_argument('-i', '--input', metavar='file',
                            help='path to read input from')
    arg_parser.add_argument('--interpret', action='store_true',
                            help=('parse the input text using the '
                                  'supplied grammar'))
    arg_parser.add_argument('-V', '--version', action='store_true',
                            help='print glop version ("%s")' % VERSION)
    arg_parser.add_argument('--class-name', default='Parser',
                            help=('class name for the generated class '
                                 '("%(default)s" is the default)'))
    arg_parser.add_argument('--pretty-print', action='store_true',
                            help='pretty-print grammar')
    arg_parser.add_argument('grammar', nargs='?')
    args = arg_parser.parse_args(argv)

    if args.version:
        host.print_(VERSION)
        return 0

    if not args.grammar:
        host.print_('Must provide a grammar file.', stream=host.stderr)
        return 2

    try:
        if not host.exists(args.grammar):
            host.print_('Error: no such file: "%s"' % args.grammar,
                        stream=host.stderr)
            return 1

        try:
            grammar_txt = host.read_text_file(args.grammar)
        except Exception as e:
            host.print_('Error: %s' % str(e), stream=host.stderr)
            return 1

        parser = Parser(grammar_txt, args.grammar)
        ast, err = parser.parse()
        if err:
            host.print_(err, stream=host.stderr)
            return 1

        grammar = Analyzer(ast).analyze()
        out, err = '', ''

        if args.pretty_print:
            out, err = Printer(grammar).dumps(), None
            if err:
                host.print_(err, stream=host.stderr)
                return 1
            if not args.output:
                args.output = '-'
            if args.output == '-':
                host.print_(out, end='')
            else:
                host.write_text_file(args.output, out)
            return 0


        out, err = Compiler(grammar).compile(args.class_name)
        if err:
            host.print_(err, stream=host.stderr)
            return 1

        if args.interpret:
            if not args.output:
                args.output = '-'
            if args.input and args.input != '-':
                path, contents = (args.input, host.read_text_file(args.input))
            else:
                path, contents = ('<stdin>', host.stdin.read())
            out, err = Interpreter(out, args.class_name).interpret(
                contents, path)
            if err:
                host.print_(err, stream=host.stderr)
                return 1
            if not out:
                out = ''
            if not isinstance(out, basestring):
                out = json.dumps(out, indent=2, sort_keys=True)
        else:
           if not args.output:
                args.output = host.splitext(
                    host.basename(args.grammar))[0] + '.py'

        if args.output == '-':
            host.print_(out, end='')
        else:
            host.write_text_file(args.output, out)
        return 0

    except KeyboardInterrupt:
        host.print_('Interrupted, exiting ...', stream=host.stderr)
        return 130  # SIGINT


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
