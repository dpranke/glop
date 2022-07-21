grammar = L '\n' end -> 'ok'
        | 'not ok'

L = 'x' S*

S = '(n)'* '.x'
