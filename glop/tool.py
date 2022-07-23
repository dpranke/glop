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
if not d in sys.path:  # pragma: no cover
    sys.path.insert(0, d)

# We use absolute paths rather than relative paths because this file can be
# invoked directly as a script (and isn't considered part of a module in
# that case).
# pylint: disable=wrong-import-position
from glop.ir import Grammar # , check_for_left_recursion
from glop.compiler import Compiler
from glop.printer import Printer
from glop.host import Host
from glop.interpreter import Interpreter
from glop.parser import Parser
from glop.version import VERSION

# pylint: enable=wrong-import-position


def main(host=None, argv=None):
    host = host or Host()

    try:
        args, err = _parse_args(host, argv)
        if err is not None:
            return err

        grammar, err = _read_grammar(host, args)
        if err:
            return err
        if args.pretty_print:
            return _pretty_print_grammar(host, args, grammar)

        if args.ast:
            contents = json.dumps(grammar.ast, indent=2) + '\n'
            _write(host, args.output, contents)
            return 0

        #lr_rules = check_for_left_recursion(grammar.ast)
        #if lr_rules:
        #    for rule in lr_rules:
        #        host.print_('Rule `%s` is left-recursive.' % rule,
        #                    stream=host.stderr)
        #    return 1

        if args.compile:
            comp = Compiler(grammar, args.class_name, args.main, args.memoize)
            contents = comp.compile()
            _write(host, args.output, contents)
            if args.output != '-' and args.main:
                host.make_executable(args.output)
            return 0

        return _interpret_grammar(host, args, grammar)

    except KeyboardInterrupt:
        host.print_('Interrupted, exiting ...', stream=host.stderr)
        return 130  # SIGINT


def _parse_args(host, argv):
    class ArgumentParser(argparse.ArgumentParser):
        status = None
        message = None

        def exit(self, status=0, message=None):
            self.status = status
            self.message = message

        def error(self, message):
            self.exit(2, message)

    ap = ArgumentParser(prog='glop', add_help=False)
    ap.add_argument('-a', '--ast', action='store_true')
    ap.add_argument('-c', '--compile', action='store_true')
    ap.add_argument('-e', '--expr', action='store')
    ap.add_argument('-h', '--help', action='store_true')
    ap.add_argument('-i', '--input', default='-')
    ap.add_argument('-n', '--no-appended-newline', action='store_true')
    ap.add_argument('-o', '--output')
    ap.add_argument('-p', '--pretty-print', action='store_true')
    ap.add_argument('-s', '--as-string', action='store_true',
                    help='return output as a string, not as a JSON object')
    ap.add_argument('-V', '--version', action='store_true')
    ap.add_argument('--class-name', default='Parser')
    ap.add_argument('--memoize', action='store_true', default=False,
                    help='memoize intermediate results (off by default)')
    ap.add_argument('--no-memoize', dest='memoize', action='store_false')
    ap.add_argument('--main', action='store_true', default=False,
                    help='generate a main() wrapper (off by default)')
    ap.add_argument('--no-main', dest='main', action='store_false')
    ap.add_argument('grammar', nargs='?')

    args = ap.parse_args(argv)

    usage = '''\
usage: glop [-achnpsV] [-e expr] [-i file] [-o file] [grammar]

    -a, --ast                  dump the ast of the parsed input
    -c, --compile              compile grammar instead of interpreting it
    -e, --expr EXPR            use the provided expression as a grammar
    -h, --help                 show this message and exit
    -i, --input FILE           file to read input from (use '-' for stdin)
    -n, --no-appended-newline  do not print a newline after output
    -o, --output FILE          file to write output to (use '-' for stdout)
    -p, --pretty-print         pretty-print grammar
    -s, --as-string            print output as a string, not a JSON object
    -V, --version              print current version (%s)

    --class-name CLASS_NAME    class name for the generated class when
                               compiling it (defaults to 'Parser')
    --[no-]memoize             memoize intermedate results (off by default)
    --[no-]main                generate a main() wrapper (off by default)
''' % VERSION

    if args.version:
        host.print_(VERSION)
        return None, 0

    if args.help:
        host.print_(usage)
        return None, 0

    if ap.status is not None:
        host.print_(usage)
        host.print_('Error: %s' % ap.message, stream=host.stderr)
        return None, ap.status

    if not args.expr and not args.grammar:
        host.print_(usage)
        return None, 2

    if not args.output:
        if args.compile:
            args.output = host.splitext(host.basename(args.grammar))[0] + '.py'
        else:
            args.output = '-'

    return args, None


def _read_grammar(host, args):
    if args.expr:
        parser = Parser(args.expr, '<expr>')
    else:
        if not host.exists(args.grammar):
            host.print_('Error: no such file: "%s"' % args.grammar,
                        stream=host.stderr)
            return None, 1

        grammar_txt = host.read_text_file(args.grammar)

        parser = Parser(grammar_txt, args.grammar)

    ast, err, _ = parser.parse()
    if err:
        host.print_(err, stream=host.stderr)
        return None, 1

    return Grammar(ast), 0


def _pretty_print_grammar(host, args, grammar):
    contents = Printer(grammar).dumps()
    _write(host, args.output, contents)
    return 0


def _interpret_grammar(host, args, grammar):
    if args.input == '-':
        path, contents = ('<stdin>', host.stdin.read())
    else:
        path, contents = (args.input, host.read_text_file(args.input))

    out, err, _ = Interpreter(grammar, args.memoize).interpret(contents,
                                                                    path)
    if err:
        host.print_(err, stream=host.stderr)
        return 1

    if out is None:
        out = ''

    if args.as_string:
        out = _as_string(out)
    else:
        out = json.dumps(out, indent=2, sort_keys=True)

    if args.no_appended_newline:
        eol = ''
    else:
        eol = '\n'
    if args.as_string:
        _write(host, args.output, out + eol)
    else:
        _write(host, args.output, out + eol)
    return 0


def _as_string(obj):
    if isinstance(obj, list):
        return ''.join(_as_string(el) for el in obj)
    return str(obj)


def _write(host, path, contents):
    if path == '-':
        host.print_(contents, end='')
    else:
        host.write_text_file(path, contents)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
