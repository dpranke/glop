class GrammarInterp(object):
    def __init__(self, grammar, msg, fname):
        self.grm = grammar
        self.msg = msg
        self.fname = fname

    def parse(self):
        return self.msg, None
