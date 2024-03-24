#!/usr/bin/env python3

import argparse
import json
import os
import sys

# pylint: disable=too-many-lines

class Parser:
    def __init__(self, msg, fname):
        self.msg = msg
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0

    def parse(self):
        self._r_grammar_0()
        if self.failed:
            return self._err()
        return self.val, None, self.pos

    def _err(self):
        lineno = 1
        colno = 1
        for ch in self.msg[:self.errpos]:
            if ch == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = repr(self.msg[self.errpos]).replace(
               "'", "\"")
        err_str = '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)
        return None, err_str, self.errpos

    def _r_foo_0(self):
        self._h_ch('a')

    def _r_grammar_0(self):
        self._h_choice([
            lambda: self._r_grammar_1(), lambda: self._r_grammar_2()
        ])

    def _r_grammar_1(self):
        self._h_seq([
            lambda: self._r_foo_0(), lambda: self._h_ch('b')
        ])

    def _r_grammar_2(self):
        self._h_seq([
            lambda: self._r_foo_0(), lambda: self._h_ch('c')
        ])

    def _h_ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._h_succeed(ch, p+1)
        else:
            self._h_fail()

    def _h_choice(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._h_rewind(p)
        rules[-1]()

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _h_set(self, var, val):
        self._scopes[-1][var] = val

    def _h_star(self, rule, vs=None):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._h_rewind(p)
                break
            vs.append(self.val)
        self._h_succeed(vs)

    def _h_succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos



def main(argv,
         stdin=sys.stdin,
         stdout=sys.stdout,
         stderr=sys.stderr,
         exists=os.path.exists,
         opener=open):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='?')
    args = arg_parser.parse_args(argv)

    if not args.file or args.file[0] == '-':
        fname = '<stdin>'
        fp = stdin
    elif not exists(args.file):
        print('Error: file "%s" not found.' % args.file,
              file=stderr)
        return 1
    else:
        fname = args.file
        fp = opener(fname)

    msg = fp.read()
    obj, err, _ = Parser(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1

    print(json.dumps(obj, ensure_ascii=False), file=stdout)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
