from parser_base import ParserBase


class GrammarPrinter(ParserBase):
    def __init__(self, grammar):
        super(GrammarPrinter, self).__init__('', '', grammar.start)
        self.grammar = grammar

    def _proc(self, node):
        fn = getattr(self, '_' + node[0] + '_')
        return fn(node)

    def parse(self, rule=None, start=0):
        rules = []
        for rule, node in self.grammar.rules.items():
            rules.append("%s = %s" % (rule, self._proc(node)))
        return '\n'.join(rules), None

    def _choice_(self, node):
        return ' | '.join(self._proc(e) for e in node[1])

    def _seq_(self, node):
        return ' '.join(self._proc(e) for e in node[1])

    def _label_(self, node):
        return '%s:%s' % (self._proc(node[1]), node[2])

    def _post_(self, node):
        return '%s%s' % (self._proc(node[1]), node[2])

    def _apply_(self, node):
        return node[1]

    def _action_(self, node):
        return '-> %s' % self._proc(node[1])

    def _not_(self, node):
        return '~%s' % self._proc(node[1])

    def _pred_(self, node):
        return '?(%s)' % self._proc(node[1])

    def _lit_(self, node):
        return "'%s'" % node[1]

    def _py_plus_(self, node):
        return '%s + %s' % (self._proc(node[1]), self._proc(node[2]))

    def _py_qual_(self, node):
        _, e, ops = node
        v = self._proc(e)
        os = []
        for op in ops:
            if op[0] == 'py_getitem':
                os.append('[%s]' % self._proc(op[1]))
            if op[0] == 'py_call':
                os.append('(%s)' % (', '.join(self._proc(a) for a in op[1])))
            if op[0] == 'py_getattr':
                os.append('.%s' % op[1])
        return '%s%s' % (v, ''.join(os))

    def _py_lit_(self, node):
        return "'%s'" % node[1]

    def _py_var_(self, node):
        return node[1]

    def _py_num_(self, node):
        return str(node[1])

    def _py_arr_(self, node):
        return '[%s]' % ', '.join(self._proc(e) for e in node[1])
