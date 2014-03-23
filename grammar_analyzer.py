from grammar import Grammar


class GrammarAnalyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def analyze(self):
        return Grammar(self.ast, 'grammar'), None
