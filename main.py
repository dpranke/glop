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
import sys

from analyzer import Analyzer
from compiler import Compiler
from grammar_printer import GrammarPrinter
from hand_rolled_grammar_parser import HandRolledGrammarParser
from compiled_grammar_parser import CompiledGrammarParser
from host import Host
from interpreter import Interpreter


VERSION = '0.1'


def main(host, argv=None):
    args = parse_args(argv)
    if args.version:
        host.print_out(VERSION)
        return 0
    if args.grammar_cmd is None and args.grammar_file is None:
        host.print_err('must specify one of -c or -g')
        return 1

    try:
        grammar_txt, grammar_fname, err = grammar_from_args(host, args)
        if err:
            host.print_err(err)
            return 1

        if args.pretty_print or args.compile_grammar:
            if args.pretty_print:
                out, err = print_grammar(grammar_txt, grammar_fname)
            else:
                if args.inline_compiled_parser_base:
                    base = (host.read(host.dirname(__file__),
                                      'compiled_parser_base.py'))
                else:
                    base = None
                out, err = compile_grammar(grammar_txt, grammar_fname,
                                           args.compiled_parser_class_name,
                                           args.compiled_parser_package_name,
                                           base)

            if err:
                host.print_err(err)
                return 1
            if args.output:
                host.write(args.output, out)
            else:
                host.print_out(out, end='')
            return 0

        input_txt, input_fname, err = input_from_args(host, args)
        if err:
            host.print_err(err)
            return 1

        out, err = parse(grammar_txt, input_txt, grammar_fname, input_fname,
                         args.use_compiled_grammar_parser)
        if err:
            host.print_err(err)
        if out:
            if args.output:
                host.write(args.output, str(out))
            else:
                host.print_out(str(out), end='')
        return 0 if err is None else 1

    except KeyboardInterrupt:
        host.print_err('Interrupted, exiting ..')
        return 130  # SIGINT


def parse_args(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', metavar='STR', dest='grammar_cmd',
                            help='inline grammar string')
    arg_parser.add_argument('-C', dest='compile_grammar', action='store_true',
                            help='compile the grammar')
    arg_parser.add_argument('-g', metavar='FILE', dest='grammar_file',
                            help='path to grammar file')
    arg_parser.add_argument('-i', metavar='STR', dest='input_cmd',
                            help='inline input string')
    arg_parser.add_argument('-o', metavar='FILE', dest='output',
                            help='path to write output to')
    arg_parser.add_argument('-p', dest='pretty_print', action='store_true',
                            help='pretty-print grammar')
    arg_parser.add_argument('-v', '--version', action='store_true',
                            help='print glop version ("%s")' % VERSION)
    arg_parser.add_argument('-P', '--compiled-parser-package-name')
    arg_parser.add_argument('--inline-compiled-parser-base',
                            action='store_true')
    arg_parser.add_argument('--use-compiled-grammar-parser',
                            action='store_true')
    arg_parser.add_argument('-N', '--compiled-parser-class-name',
                            default='Parser')
    arg_parser.add_argument('files', nargs='*', default=[],
                            help=argparse.SUPPRESS)
    return arg_parser.parse_args(argv)


def grammar_from_args(host, args):
    if args.grammar_cmd is not None:
        grammar_fname = '<-c>'
        grammar_txt = args.grammar_cmd
    else:
        grammar_fname = args.grammar_file
        if not host.exists(grammar_fname):
            return None, None, 'grammar file "%s" not found' % grammar_fname
        grammar_txt = host.read(grammar_fname)
    return grammar_txt, grammar_fname, None


def input_from_args(host, args):
    if args.input_cmd is not None:
        input_fname = '<cmd>'
        input_txt = args.input_cmd
    elif args.files:
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


def compile_grammar(grammar_txt, grammar_fname, compiled_parser_class_name,
                    package, inline_base):
    g_parser = HandRolledGrammarParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    if err:
        return None, err

    g, _ = Analyzer(g_ast).analyze()
    compiler = Compiler(g, compiled_parser_class_name, package, inline_base)
    return compiler.walk()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(Host()))
