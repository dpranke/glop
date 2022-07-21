# Copyright 2014 Dirk Pranke. All rights reserved.
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

import unicodedata


class Interpreter(object):
    def __init__(self, grammar, memoize):
        self.memoize = memoize
        self.grammar = grammar

        self.failed = False
        self.val = None
        self.pos = 0
        self.errstr = "Error: uninitialized"
        self.errpos  = 0
        self.msg = None
        self.fname = None
        self.end = -1
        self.scopes = []

    def interpret(self, msg, fname):
        self.msg = msg
        self.fname = fname

        self.pos = 0
        self.end = len(self.msg)
        self.errstr = None
        self.errpos = 0

        cur_node = None
        for node in self.grammar.rules:
            if node[0] == 'rule' and node[1] == self.grammar.starting_rule:
                cur_node = node

        if not cur_node:
            return None, ("Error: unknown starting rule '%s'" %
                          self.grammar.starting_rule), 0

        self._interpret(cur_node[2])
        if self.failed:
            return self._format_error()
        else:
            return self.val, "", 0

    def _interpret(self, node):
        node_handler = getattr(self, '_handle_' + node[0], None)
        if node_handler:
            node_handler(node)
            return

        self.failed = True
        self.val = None
        self.errstr = "Error: node type '%s' not implemented yet" % node[0]

    def _fail(self, errstr=None):
        self.failed = True
        self.val = None
        if self.pos >= self.errpos:
            self.errpos = self.pos
            self.errstr = errstr

    def _succeed(self, val=None, newpos=None):
        self.val = val
        self.failed = False
        self.errstr = None
        if newpos is not None:
            self.pos = newpos

    def _format_error(self):
        lineno = 1
        colno = 1
        for ch in self.msg[:self.errpos]:
            if ch == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        if not self.errstr:
            if self.errpos == len(self.msg):
                thing = 'end of input'
            else:
                thing = repr(self.msg[self.errpos]).replace("'", "\"")
                if thing[0] == 'u':
                    thing = thing[1:]
            self.errstr = 'Unexpected %s at column %d' % (thing, colno)

        msg = '%s:%d %s' % (self.fname, lineno, self.errstr)
        return None, msg, self.errpos

    def _handle_action(self, node):
        self._interpret(node[1])

    def _handle_apply(self, node):
        rule_name = node[1]
        if rule_name == 'end':
            self._handle_end()
            return

        if rule_name == 'anything':
            if self.pos != self.end:
                self._succeed(self.msg[self.pos], self.pos + 1)
                return

        for rule in self.grammar.rules:
            if rule_name == rule[1]:
                self._interpret(rule[2])
                return

        # TODO: figure out if/when this can actually be reached. Shouldn't
        # this be caught while validating the grammar?
        self._fail("Error: no rule named '%s'" % rule_name)

    def _handle_capture(self, node):
        start = self.pos
        self._interpret(node[1])
        end = self.pos
        self._succeed(self.msg[start:end])

    def _handle_choice(self, node):
        for rule in node[1]:
            p = self.pos
            self._interpret(rule)
            if not self.failed:
                return
        return

    def _handle_empty(self, node):
        self._succeed()

    def _handle_end(self):
        if self.pos != self.end:
            self._fail()
            return
        self._succeed()

    def _handle_eq(self, node):
        self._interpret(node[1])
        if self.msg[self.pos:].startswith(self.val):
            self._succeed(newpos=self.pos + len(self.val))
        else:
            self._fail()

    def _handle_label(self, node):
        self._interpret(node[1])
        self.scopes[-1][node[2]] = self.val
        self._succeed()

    def _handle_label_all(self, node):
        self._fail('_0 is not supported yet')

    def _handle_leftrec(self, node):
        self._fail('left recursion is not supported yet')

    def _handle_lit(self, node):
        i = 0
        succeeded = True
        lit = node[1]
        lit_len = len(lit)
        while succeeded and i < lit_len and self.pos < self.end:
            succeeded, offset = self._ch(self.msg[self.pos], lit, i, lit_len)
            if succeeded:
                self.pos += 1
                i += offset
        if succeeded and i == lit_len:
            self._succeed(self.msg[self.pos-1])
        else:
            self._fail()

    def _ch(self, ch, lit, i, lit_len):
        l1 = lit[i]
        if l1 != '\\':
            # This is the most common case (not an escape sequence),
            # so we handle this first.
            return (ch == l1, 1)

        if lit == '\\' and ch == '\\':
            return True, 1

        if l2 == 'b':
            return (ch == chr(0x08), 2)
        if l2 == 'f':
            return (ch == chr(0x0C), 2)
        if l2 == 'n':
            return (ch == chr(0x0A), 2)
        if l2 == 'r':
            return (ch == chr(0x0D), 2)
        if l2 == 't':
            return (ch == chr(0x09), 2)
        if l2 == 'u':
            if lit_len < (i + 6):
                return (False, 0)
            return (ch == chr(int(lit[i+1:i+4], base=16), 6))
        if l2 == 'U':
            if lit_len < (i + 10):
                return (False, 0)
            return (ch == chr(int(lit[i+1:i+8], base=16), 10))
        if l2 == 'v':
            return (ch == chr(0x0B), 2)
        if l2 == 'x':
            if lit_len < (i + 4):
                return (False, 0)
            return (ch == chr(int(lit[i+1:i+2], base=16), 4))
        if l2 == '\\':
            return (ch == chr(0x5C), 2)
        if l2 == '"':
            return (ch == '"', 2)

        # Unknown escape sequence.
        return False, 1

    def _handle_ll_arr(self, node):
        vals = []
        for subnode in node[1]:
            self._interpret(subnode)
            if self.failed:
                return
            vals.append(self.val)
        self._succeed(vals)
        return

    def _handle_ll_call(self, node):
        vals = []
        for subnode in node[1]:
            self._interpret(subnode)
            if self.failed:
                return
            vals.append(self.val)
        self._succeed(['ll_call', vals])

    def _handle_ll_dec(self, node):
        self._succeed(int(node[1]))

    def _handle_ll_getattr(self, node):
        self._interpret(node[1])
        if not self.failed:
          self._succeed(['ll_getattr', self.val])

    def _handle_ll_getitem(self, node):
        self._interpret(node[1])
        if not self.failed:
          self._succeed(['ll_getitem', self.val])

    def _handle_ll_hex(self, node):
        self._succeed(hex(self.val))

    def _handle_ll_paren(self, node):
        self._interpret(node[1])

    def _handle_ll_plus(self, node):
        self._interpret(node[1])
        v1 = self.val
        self._interpret(node[2])
        v2 = self.val
        self._succeed(v1 + v2)

    def _handle_ll_qual(self, node):
        self._interpret(node[1])
        if self.failed:
            return
        lhs = self.val
        self._interpret(node[2][0])
        if self.failed:
            return
        op, rhs = self.val
        if op == 'll_getitem':
            self.val = lhs[rhs]
        elif op == 'll_getattr':
            self.val = getattr(lhs, rhs)
        else:
            assert(op == 'll_call')
            fn = getattr(self, '_builtin_fn_' + lhs)
            self.val = fn(*rhs)

    def _handle_ll_str(self, node):
        self._succeed(node[1])

    def _handle_ll_var(self, node):
        v = getattr(self, '_builtin_fn_' + node[1], None)
        if v:
            self._succeed(node[1])
            return

        if node[1] == 'true':
            self._succeed(True)
            return
        elif node[1] == 'false':
            self._succeed(False)

        if self.scopes and (node[1] in self.scopes[-1]):
            self._succeed(self.scopes[-1][node[1]])
            return

        self._fail('unknown reference to "%s"' % node[1])

    def _handle_not(self, node):
        pos = self.pos
        val = self.val
        self._interpret(node[1])
        if self.failed:
            self._succeed(val, newpos=pos)
        else:
            self.pos = pos
            self._fail(val)

    def _handle_opt(self, node):
        pos = self.pos
        val = self.val
        self._interpret(node[1])
        if self.failed:
            self.failed = False
            self.val = val
            self.pos = pos

    def _handle_paren(self, node):
        self._interpret(node[1])

    def _handle_plus(self, node):
        self._interpret(node[1])
        if not self.failed:
            self._handle_star(node)

    def _handle_pos(self, node):
        self.val = self.pos

    def _handle_pred(self, node):
        self._interpret(node[1])
        if self.val is True:
            self._succeed(True)
        elif self.val is False:
            self.val = False
            self._fail()
        else:
            self._fail('Bad predicate value')

    def _handle_range(self, node):
        if node[1] <= self.pos <= node[2]:
            self._succeed(self.msg[self.pos], pos + 1)

    def _handle_seq(self, node):
        for node in node[1]:
            self._interpret(node)
            if self.failed:
                return

    def _handle_scope(self, node):
        self.scopes.append({})
        for node in node[1]:
            self._interpret(node)
            if self.failed:
                self.scopes.pop()
                return
        self.scopes.pop()
        return

    def _handle_star(self, node):
        vs = []
        while not self.failed and self.pos < self.end:
            p = self.pos
            self._interpret(node[1])
            if self.failed:
                self.pos = p
                break
            vs.append(self.val)
        if self.failed:
            self.pos = p
        self._succeed(vs)

    def _builtin_fn_cat(self, val):
        return ''.join(val)

    def _builtin_fn_itou(self, val):
        return chr(val)

    def _builtin_fn_is_unicat(self, var, cat):
        return unicodedata.category(var) == cat

    def _builtin_fn_join(self, s, vs):
        return s.join(vs)

    def _builtin_fn_pos(self):
        return self.pos

    def _builtin_fn_slice(self, x, y):
        return self.msg[x:y]

    def _builtin_fn_utoi(self, s):
        return int(s)

    def _builtin_fn_xtoi(self, val):
        self._succeed(int(val, base=16))

    def _builtin_fn_xtou(self, val):
        self._succeed(chr(int(val, base=16)))
