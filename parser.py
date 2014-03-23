class Parser(object):
    """Parses an .omp file and returns an AST ."""
    def __init__(self, msg, fname):
        self.msg = msg
        self.end = len(msg)
        self.fname = fname

    def parse(self, rule='grammar', start=0):
        v, p, err = self.apply_rule(rule, start)
        if err:
            lineno, colno = self._line_and_colno(p)
            return None, "%s:%d:%d expecting %s" % (
                self.fname, lineno, colno, err)
        return v, None

    def apply_rule(self, rule, p):
        rule_fn = getattr(self, '_' + rule + '_', None)
        if not rule_fn:
            return None, p, 'unknown rule "%s"' % rule
        return rule_fn(p)

    def _line_and_colno(self, p):
        lineno = 1
        colno = 1
        i = 0
        while i < p:
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
            i += 1
        return lineno, colno

    def _expect(self, p, expr):
        l = len(expr)
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            return expr, p + l, None
        return None, p, ("'%s'" % expr)

    def _anything_(self, p):
        if p < self.end:
            return self.msg[p], p + 1, None
        return None, p, "anything"

    def _end_(self, p):
        """ ~ anything """
        _, p, err = self._anything_(p)
        if err:
            return None, p, None
        return None, p, "the end"

    def _letter_(self, p):
        if p < self.end and self.msg[p].isalpha():
            return self.msg[p], p + 1, None
        return None, p, "a letter"

    def _digit_(self, p):
        if p < self.end and self.msg[p].isdigit():
            return self.msg[p], p + 1, None
        return None, p, "a digit"
