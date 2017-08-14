#!/usr/bin/env python

# pylint: disable=line-too-long

from __future__ import print_function

import argparse
import json
import os
import sys


def main(argv=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout,
         stderr=sys.stderr, exists=os.path.exists, opener=open):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='?')
    args = arg_parser.parse_args(argv)

    if not args.file or args.file[1] == '-':
        fname = '<stdin>'
        fp = stdin
    elif not exists(args.file):
        print('Error: file "%s" not found.' % args.file, file=stderr)
        return 1
    else:
        fname = args.file
        fp = opener(fname)

    msg = fp.read()
    obj, err = Parser(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1
    print(json.dumps(obj), file=stdout)
    return 0


class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar'):
        self.msg = msg
        self.end = len(msg)
        self.fname = fname
        self.starting_rule = starting_rule
        self.val = None
        self.err = None
        self.pos = 0
        self.errpos = 0
        self.errset = set()
        self.scopes = []

    def parse(self):
        rule_fn = getattr(self, '_' + self.starting_rule + '_', None)
        if not rule_fn:
            return None, 'unknown rule "%s"' % self.starting_rule
        rule_fn()
        if self.err:
            return None, self._err_str()
        return self.val, None

    def _push(self, name):
        self.scopes.append((name, {}))

    def _pop(self, name):
        actual_name, _ = self.scopes.pop()
        assert name == actual_name

    def _get(self, var):
        return self.scopes[-1][1][var]

    def _set(self, var, val):
        self.scopes[-1][1][var] = val

    def _err_str(self):
        lineno, colno, _ = self._err_offsets()
        if isinstance(self.err, basestring):
            return '%s:%d %s' % (self.fname, lineno, self.err)
        exps = sorted(self.errset)
        if len(exps) > 2:
            expstr = "either %s, or '%s'" % (
                ', '.join("'%s'" % exp for exp in exps[:-1]), exps[-1])
        elif len(exps) == 2:
            expstr = "either '%s' or '%s'" % (exps[0], exps[1])
        elif len(exps) == 1:
            expstr = "a '%s'" % exps[0]
        else:
            expstr = '<EOF>'
        prefix = '%s:%d' % (self.fname, lineno)
        return "%s Expecting %s at column %d" % (prefix, expstr, colno)

    def _err_offsets(self):
        lineno = 1
        colno = 1
        i = 0
        begpos = 0
        while i < self.errpos:
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
                begpos = i
            else:
                colno += 1
            i += 1
        return lineno, colno, begpos

    def _esc(self, val):
        return str(val)

    def _expect(self, expr):
        p = self.pos
        l = len(expr)
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self.pos += l
            self.val = expr
            self.err = False
        else:
            self.val = None
            self.err = True
            if self.pos >= self.errpos:
                if self.pos > self.errpos:
                    self.errset = set()
                self.errset.add(self._esc(expr))
                self.errpos = self.pos
        return

    def _grammar_(self):
        self._push('grammar')
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._rule_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('vs', self.val)
        if self.err:
            self._pop('grammar')
            return
        self._sp_()
        if self.err:
            self._pop('grammar')
            return
        self._end_()
        if self.err:
            self._pop('grammar')
            return
        self.val = self._get('vs')
        self.err = None
        self._pop('grammar')

    def _sp_(self):
        vs = []
        while not self.err:
            p = self.pos
            self._ws_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None

    def _ws_(self):
        p = self.pos
        def choice_0():
            self._expect(' ')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\t')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._eol_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._comment_()
        choice_3()

    def _eol_(self):
        p = self.pos
        def choice_0():
            self._expect('\r')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\n')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('\r\n')
        choice_2()

    def _comment_(self):
        self._expect('//')
        if self.err:
            return
        vs = []
        while not self.err:
            p = self.pos
            def group():
                p = self.pos
                self._eol_()
                self.pos = p
                if not self.err:
                    self.err = "not"
                    self.val = None
                    return
                self.err = None
                if self.err:
                    return
                self._anything_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if self.err:
            return
        self._eol_()

    def _rule_(self):
        self._push('rule')
        self._ident_()
        if not self.err:
            self._set('i', self.val)
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        if self.err:
            self._pop('rule')
            return
        self._expect('=')
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        if self.err:
            self._pop('rule')
            return
        self._choice_()
        if not self.err:
            self._set('cs', self.val)
        if self.err:
            self._pop('rule')
            return
        self._sp_()
        if self.err:
            self._pop('rule')
            return
        p = self.pos
        self._expect(',')
        if self.err:
            self.val = []
            self.err = None
            self.pos = p
        else:
            self.val = [self.val]
        if self.err:
            self._pop('rule')
            return
        self.val = ['rule', self._get('i'), self._get('cs')]
        self.err = None
        self._pop('rule')

    def _ident_(self):
        self._push('ident')
        self._id_start_()
        if not self.err:
            self._set('hd', self.val)
        if self.err:
            self._pop('ident')
            return
        vs = []
        while not self.err:
            p = self.pos
            self._id_continue_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('tl', self.val)
        if self.err:
            self._pop('ident')
            return
        self.val = ''.join([self._get('hd')] + self._get('tl'))
        self.err = None
        self._pop('ident')

    def _id_start_(self):
        p = self.pos
        def choice_0():
            self._letter_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('_')
        choice_1()

    def _id_continue_(self):
        p = self.pos
        def choice_0():
            self._letter_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('_')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._digit_()
        choice_2()

    def _choice_(self):
        self._push('choice')
        self._seq_()
        if not self.err:
            self._set('s', self.val)
        if self.err:
            self._pop('choice')
            return
        vs = []
        while not self.err:
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._expect('|')
                if self.err:
                    return
                self._sp_()
                if self.err:
                    return
                self._seq_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('ss', self.val)
        if self.err:
            self._pop('choice')
            return
        self.val = ['choice', [self._get('s')] + self._get('ss')]
        self.err = None
        self._pop('choice')

    def _seq_(self):
        p = self.pos
        def choice_0():
            self._push('seq_0')
            self._expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('seq_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._ws_()
                    if self.err:
                        return
                    self._sp_()
                    if self.err:
                        return
                    self._expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('seq_0')
                return
            self.val = ['seq', [self._get('e')] + self._get('es')]
            self.err = None
            self._pop('seq_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = ['empty']
            self.err = None
        choice_1()

    def _expr_(self):
        p = self.pos
        def choice_0():
            self._push('expr_0')
            self._post_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('expr_0')
                return
            self._expect(':')
            if self.err:
                self._pop('expr_0')
                return
            self._ident_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('expr_0')
                return
            self.val = ['label', self._get('e'), self._get('l')]
            self.err = None
            self._pop('expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._post_expr_()
        choice_1()

    def _post_expr_(self):
        p = self.pos
        def choice_0():
            self._push('post_expr_0')
            self._prim_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('post_expr_0')
                return
            self._post_op_()
            if not self.err:
                self._set('op', self.val)
            if self.err:
                self._pop('post_expr_0')
                return
            self.val = ['post', self._get('e'), self._get('op')]
            self.err = None
            self._pop('post_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._prim_expr_()
        choice_1()

    def _post_op_(self):
        p = self.pos
        def choice_0():
            self._expect('?')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('*')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('+')
        choice_2()

    def _prim_expr_(self):
        p = self.pos
        def choice_0():
            self._push('prim_expr_0')
            self._lit_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('prim_expr_0')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_0')
                return
            self._expect('..')
            if self.err:
                self._pop('prim_expr_0')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_0')
                return
            self._lit_()
            if not self.err:
                self._set('j', self.val)
            if self.err:
                self._pop('prim_expr_0')
                return
            self.val = ['range', self._get('i'), self._get('j')]
            self.err = None
            self._pop('prim_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('prim_expr_1')
            self._lit_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('prim_expr_1')
                return
            self.val = self._get('l')
            self.err = None
            self._pop('prim_expr_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('prim_expr_2')
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('prim_expr_2')
                return
            p = self.pos
            def group():
                self._sp_()
                if self.err:
                    return
                self._expect('=')
            group()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('prim_expr_2')
                return
            self.err = None
            if self.err:
                self._pop('prim_expr_2')
                return
            self.val = ['apply', self._get('i')]
            self.err = None
            self._pop('prim_expr_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('prim_expr_3')
            self._expect('->')
            if self.err:
                self._pop('prim_expr_3')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_3')
                return
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_3')
                return
            self.val = ['action', self._get('e')]
            self.err = None
            self._pop('prim_expr_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('prim_expr_4')
            self._expect('~')
            if self.err:
                self._pop('prim_expr_4')
                return
            self._prim_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_4')
                return
            self.val = ['not', self._get('e')]
            self.err = None
            self._pop('prim_expr_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('prim_expr_5')
            self._expect('?(')
            if self.err:
                self._pop('prim_expr_5')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_5')
                return
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_5')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_5')
                return
            self._expect(')')
            if self.err:
                self._pop('prim_expr_5')
                return
            self.val = ['pred', self._get('e')]
            self.err = None
            self._pop('prim_expr_5')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._push('prim_expr_6')
            self._expect('(')
            if self.err:
                self._pop('prim_expr_6')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_6')
                return
            self._choice_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('prim_expr_6')
                return
            self._sp_()
            if self.err:
                self._pop('prim_expr_6')
                return
            self._expect(')')
            if self.err:
                self._pop('prim_expr_6')
                return
            self.val = ['paren', self._get('e')]
            self.err = None
            self._pop('prim_expr_6')
        choice_6()

    def _lit_(self):
        p = self.pos
        def choice_0():
            self._push('lit_0')
            self._squote_()
            if self.err:
                self._pop('lit_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._squote_()
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._sqchar_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('lit_0')
                return
            self._squote_()
            if self.err:
                self._pop('lit_0')
                return
            self.val = ['lit', self._join('', self._get('cs'))]
            self.err = None
            self._pop('lit_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('lit_1')
            self._dquote_()
            if self.err:
                self._pop('lit_1')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._dquote_()
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._dqchar_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('lit_1')
                return
            self._dquote_()
            if self.err:
                self._pop('lit_1')
                return
            self.val = ['lit', self._join('', self._get('cs'))]
            self.err = None
            self._pop('lit_1')
        choice_1()

    def _sqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._squote_()
            if self.err:
                return
            self.val = '\x5C\x27'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._bslash_()
            if self.err:
                return
            self.val = '\x5C\x5C'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._anything_()
        choice_2()

    def _dqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._dquote_()
            if self.err:
                return
            self.val = '\x5C\x22'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._bslash_()
            if self.err:
                return
            self.val = '\x5C\x5C'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._anything_()
        choice_2()

    def _bslash_(self):
        self._expect('\x5C')

    def _squote_(self):
        self._expect('\x27')

    def _dquote_(self):
        self._expect('\x22')

    def _ll_exprs_(self):
        p = self.pos
        def choice_0():
            self._push('ll_exprs_0')
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_exprs_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._sp_()
                    if self.err:
                        return
                    self._expect(',')
                    if self.err:
                        return
                    self._sp_()
                    if self.err:
                        return
                    self._ll_expr_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_exprs_0')
                return
            self.val = [self._get('e')] + self._get('es')
            self.err = None
            self._pop('ll_exprs_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self.val = []
            self.err = None
        choice_1()

    def _ll_expr_(self):
        p = self.pos
        def choice_0():
            self._push('ll_expr_0')
            self._ll_qual_()
            if not self.err:
                self._set('e1', self.val)
            if self.err:
                self._pop('ll_expr_0')
                return
            self._sp_()
            if self.err:
                self._pop('ll_expr_0')
                return
            self._expect('+')
            if self.err:
                self._pop('ll_expr_0')
                return
            self._sp_()
            if self.err:
                self._pop('ll_expr_0')
                return
            self._ll_expr_()
            if not self.err:
                self._set('e2', self.val)
            if self.err:
                self._pop('ll_expr_0')
                return
            self.val = ['ll_plus', self._get('e1'), self._get('e2')]
            self.err = None
            self._pop('ll_expr_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._ll_qual_()
        choice_1()

    def _ll_qual_(self):
        p = self.pos
        def choice_0():
            self._push('ll_qual_0')
            self._ll_prim_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_qual_0')
                return
            vs = []
            self._ll_post_op_()
            if self.err:
                self._pop('ll_qual_0')
                return
            vs.append(self.val)
            while not self.err:
                p = self.pos
                self._ll_post_op_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('ps', self.val)
            if self.err:
                self._pop('ll_qual_0')
                return
            self.val = ['ll_qual', self._get('e'), self._get('ps')]
            self.err = None
            self._pop('ll_qual_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._ll_prim_()
        choice_1()

    def _ll_post_op_(self):
        p = self.pos
        def choice_0():
            self._push('ll_post_op_0')
            self._expect('[')
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._sp_()
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._sp_()
            if self.err:
                self._pop('ll_post_op_0')
                return
            self._expect(']')
            if self.err:
                self._pop('ll_post_op_0')
                return
            self.val = ['ll_getitem', self._get('e')]
            self.err = None
            self._pop('ll_post_op_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('ll_post_op_1')
            self._expect('(')
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._sp_()
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._ll_exprs_()
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._sp_()
            if self.err:
                self._pop('ll_post_op_1')
                return
            self._expect(')')
            if self.err:
                self._pop('ll_post_op_1')
                return
            self.val = ['ll_call', self._get('es')]
            self.err = None
            self._pop('ll_post_op_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('ll_post_op_2')
            self._expect('.')
            if self.err:
                self._pop('ll_post_op_2')
                return
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('ll_post_op_2')
                return
            self.val = ['ll_getattr', self._get('i')]
            self.err = None
            self._pop('ll_post_op_2')
        choice_2()

    def _ll_prim_(self):
        p = self.pos
        def choice_0():
            self._push('ll_prim_0')
            self._ident_()
            if not self.err:
                self._set('i', self.val)
            if self.err:
                self._pop('ll_prim_0')
                return
            self.val = ['ll_var', self._get('i')]
            self.err = None
            self._pop('ll_prim_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('ll_prim_1')
            self._digits_()
            if not self.err:
                self._set('ds', self.val)
            if self.err:
                self._pop('ll_prim_1')
                return
            self.val = ['ll_num', self._get('ds')]
            self.err = None
            self._pop('ll_prim_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('ll_prim_2')
            self._expect('0x')
            if self.err:
                self._pop('ll_prim_2')
                return
            self._hexdigits_()
            if not self.err:
                self._set('hs', self.val)
            if self.err:
                self._pop('ll_prim_2')
                return
            self.val = ['ll_num', '0x' + self._get('hs')]
            self.err = None
            self._pop('ll_prim_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('ll_prim_3')
            self._lit_()
            if not self.err:
                self._set('l', self.val)
            if self.err:
                self._pop('ll_prim_3')
                return
            self.val = ['ll_lit', self._get('l')[1]]
            self.err = None
            self._pop('ll_prim_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('ll_prim_4')
            self._expect('(')
            if self.err:
                self._pop('ll_prim_4')
                return
            self._sp_()
            if self.err:
                self._pop('ll_prim_4')
                return
            self._ll_expr_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('ll_prim_4')
                return
            self._sp_()
            if self.err:
                self._pop('ll_prim_4')
                return
            self._expect(')')
            if self.err:
                self._pop('ll_prim_4')
                return
            self.val = ['ll_paren', self._get('e')]
            self.err = None
            self._pop('ll_prim_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('ll_prim_5')
            self._expect('[')
            if self.err:
                self._pop('ll_prim_5')
                return
            self._sp_()
            if self.err:
                self._pop('ll_prim_5')
                return
            self._ll_exprs_()
            if not self.err:
                self._set('es', self.val)
            if self.err:
                self._pop('ll_prim_5')
                return
            self._sp_()
            if self.err:
                self._pop('ll_prim_5')
                return
            self._expect(']')
            if self.err:
                self._pop('ll_prim_5')
                return
            self.val = ['ll_arr', self._get('es')]
            self.err = None
            self._pop('ll_prim_5')
        choice_5()

    def _digits_(self):
        self._push('digits')
        vs = []
        self._digit_()
        if self.err:
            self._pop('digits')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._digit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('ds', self.val)
        if self.err:
            self._pop('digits')
            return
        self.val = self._join('', self._get('ds'))
        self.err = None
        self._pop('digits')

    def _hexdigits_(self):
        self._push('hexdigits')
        vs = []
        self._hexdigit_()
        if self.err:
            self._pop('hexdigits')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._hexdigit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('hs', self.val)
        if self.err:
            self._pop('hexdigits')
            return
        self.val = self._join('', self._get('hs'))
        self.err = None
        self._pop('hexdigits')

    def _hexdigit_(self):
        p = self.pos
        def choice_0():
            self._digit_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            i = "['lit', u'a']"
            j = "['lit', u'f']"
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[p]
                self.err = False
                self.pos += 1
            return
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            i = "['lit', u'A']"
            j = "['lit', u'F']"
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[p]
                self.err = False
                self.pos += 1
            return
        choice_2()

    def _anything_(self):
        if self.pos < self.end:
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "anything"

    def _digit_(self):
        if self.pos < self.end and self.msg[self.pos].isdigit():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a digit"
        return

    def _end_(self):
        if self.pos == self.end:
            self.val = None
            self.err = None
        else:
            self.val = None
            self.err = "the end"
        return

    def _letter_(self):
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a letter"
        return

    def _join(self, s, vs):
        return s.join(vs)


if __name__ == '__main__':
    sys.exit(main())
