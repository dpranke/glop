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

import argparse
import json
import os
import sys

d = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if not d in sys.path:
    sys.path.append(d)

from glop.analyzer import Analyzer
from glop.compiler import Compiler
from glop.grammar_printer import GrammarPrinter
from glop.hand_rolled_grammar_parser import HandRolledGrammarParser
from glop.compiled_grammar_parser import CompiledGrammarParser
from glop.host import Host
from glop.interpreter import Interpreter
from glop.version import VERSION


def main(host=None, argv=None):
    host = host or Host()
    args = parse_args(argv)
    if args.version:
        host.print_out(VERSION)
        return 0
    try:
        grammar_txt, grammar_fname, err = grammar_from_args(host, args)
        if err:
            host.print_err(err)
            return 1

        if args.pretty_print:
            out, err = print_grammar(grammar_txt, grammar_fname)
            if err:
                host.print_err(err)
                return 1
            if args.output:
                host.write(args.output, out)
            else:
                host.print_out(out, end='')
            return 0

        if args.interpret:
            out = ''
            input_txt, input_fname, err = input_from_args(host, args)
            if not err:
                out, err = parse(grammar_txt, input_txt, grammar_fname,
                                 input_fname, args.use_compiled_grammar_parser)
            if err:
                host.print_err(err)
                return 1
            if out:
                if args.output:
                    host.write(args.output, out)
                else:
                    host.print_out(out, end='')
            return 0

        if args.show_ast:
            out, err = show_ast(grammar_txt, grammar_fname,
                                args.use_compiled_grammar_parser)
        else:
            compiled_parser_base = host.read(host.dirname(__file__),
                                             'compiled_parser_base.py')

            out, err = compile_grammar(grammar_txt, grammar_fname,
                                       args.class_name,
                                       compiled_parser_base,
                                       args.use_compiled_grammar_parser)

        if err:
            host.print_err(err)
            return 1

        if out:
            if args.output:
                fname = args.output
            elif grammar_fname.startswith('<'):
                fname = 'parser.py'
            else:
                base = host.splitext(host.basename(grammar_fname))[0]
                fname = '%s_parser.py' % base
            host.write(fname, str(out))
        return 0

    except KeyboardInterrupt:
        host.print_err('Interrupted, exiting ..')
        return 130  # SIGINT


def parse_args(argv):
    arg_parser = argparse.ArgumentParser(prog='glop')
    arg_parser.add_argument('-c', '--compile', action='store_true',
                            help='compile to a module only (no main)')
    arg_parser.add_argument('-e', metavar='STR', dest='grammar_string',
                            help='inline program string')
    arg_parser.add_argument('-i', '--interpret', action='store_true',
                            help='interpret the grammar (no compiling)')
    arg_parser.add_argument('-N', '--class-name', default='Parser')
    arg_parser.add_argument('-o', metavar='FILE', dest='output',
                            help='path to write output to ('
                                 'defaults to (basename of grammar).py.')
    arg_parser.add_argument('-p', dest='pretty_print', action='store_true',
                            help='pretty-print grammar')
    arg_parser.add_argument('-V', '--version', action='store_true',
                            help='print glop version ("%s")' % VERSION)
    arg_parser.add_argument('--show-ast', action='store_true')
    arg_parser.add_argument('--use-compiled-grammar-parser',
                            action='store_true')
    arg_parser.add_argument('files', nargs='*', default=[],
                            help=argparse.SUPPRESS)
    return arg_parser.parse_args(argv)


def grammar_from_args(host, args):
    if args.grammar_string is None and not args.files:
        return None, None, 'Must specify a grammar file or a string with -e.'

    if args.grammar_string is not None:
        return args.grammar_string, '-e', None

    grammar_fname = args.files[0]
    args.files = args.files[1:]
    if not host.exists(grammar_fname):
        return None, None, 'grammar file "%s" not found' % grammar_fname

    return host.read(grammar_fname), grammar_fname, None


def input_from_args(host, args):
    if args.files:
        input_fname = args.files[0]
        if not host.exists(input_fname):
            return None, None, 'input file "%s" not found' % input_fname
        input_txt = host.read(input_fname)
    else:
        input_fname = '<stdin>'
        input_txt = host.stdin.read()
    return input_txt, input_fname, None


def parse(grammar_txt, input_txt, grammar_fname='', input_fname='',
          use_compiled_grammar_parser=False):
    if use_compiled_grammar_parser:
        g_parser = CompiledGrammarParser(grammar_txt, grammar_fname)
    else:
        g_parser = HandRolledGrammarParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    if err:
        return None, err

    g, _ = Analyzer(g_ast).analyze()
    interp = Interpreter(g, input_txt, input_fname)
    return interp.parse()


def print_grammar(grammar_txt, grammar_fname):
    g_parser = HandRolledGrammarParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    if err:
        return None, err

    g, _ = Analyzer(g_ast).analyze()
    printer = GrammarPrinter(g)
    return printer.parse()


def show_ast(grammar_txt, grammar_fname, use_compiled_grammar_parser):
    if use_compiled_grammar_parser:
        g_parser = CompiledGrammarParser(grammar_txt, grammar_fname)
    else:
        g_parser = HandRolledGrammarParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    out = json.dumps(g_ast, indent=2) + '\n'
    return out, err

def compile_grammar(grammar_txt, grammar_fname, class_name,
                    compiled_parser_base, use_compiled_grammar_parser):
    if use_compiled_grammar_parser:
        g_parser = CompiledGrammarParser(grammar_txt, grammar_fname)
    else:
        g_parser = HandRolledGrammarParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    if err:
        return None, err

    g, _ = Analyzer(g_ast).analyze()
    compiler = Compiler(g, class_name, 'CompiledParserBase')
    out, err = compiler.walk()
    return compiled_parser_base + '\n\n' + out, err


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
