import argparse
import sys

from host import Host
from grammar_analyzer import GrammarAnalyzer
from grammar_interp import GrammarInterp
from omparser import OMParser


def main(host, argv=None):
    args = parse_args(argv)
    if not args.grammar_cmd and not args.grammar_file:
        host.print_err('must specify one of -c or -g')
        return 1

    try:
        grammar_txt, grammar_fname, err = grammar_from_args(host, args)
        if err:
            host.print_err(err)
            return 1

        input_txt, input_fname, err = input_from_args(host, args)
        if err:
            host.print_err(err)
            return 1

        out, err = parse(grammar_txt, input_txt, grammar_fname, input_fname)
        if err:
            host.print_err(err)
        if out:
            if args.output:
                host.write(args.output, out)
            else:
                host.print_out(out, end='')
        return 0

    except KeyboardInterrupt:
        host.print_err('Interrupted, exiting ..')
        return 130  # SIGINT


def parse_args(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', metavar='STR', dest='grammar_cmd',
                            help='inline grammar string')
    arg_parser.add_argument('-g', metavar='FILE', dest='grammar_file',
                            help='path to grammar file')
    arg_parser.add_argument('-i', metavar='STR', dest='input_cmd',
                            help='inline input string')
    arg_parser.add_argument('-o', metavar='FILE', dest='output',
                            help='path to write output to')
    arg_parser.add_argument('files', nargs='*', default=[],
                            help=argparse.SUPPRESS)
    return arg_parser.parse_args(argv)


def grammar_from_args(host, args):
    if args.grammar_cmd:
        grammar_fname = '<-c>'
        grammar_txt = args.grammar_cmd
    else:
        grammar_fname = args.grammar_file
        if not host.exists(grammar_fname):
            return None, None, 'grammar file "%s" not found' % grammar_fname
        grammar_txt = host.read(grammar_fname)
    return grammar_txt, grammar_fname, None


def input_from_args(host, args):
    if args.input_cmd:
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


def parse(grammar_txt, input_txt, grammar_fname='', input_fname=''):
    g_parser = OMParser(grammar_txt, grammar_fname)
    g_ast, err = g_parser.parse()
    if err:
        return None, err

    g = GrammarAnalyzer(g_ast).analyze()
    interp = GrammarInterp(g, input_txt, input_fname)
    return interp.parse()


if __name__ == '__main__':
    sys.exit(main(Host()))
