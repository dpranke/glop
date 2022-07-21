grammar = L '\n' end -> 'ok'
        |            -> 'not ok'

L       = P '.x'
        | 'x'

P       = P '(n)'
        | L
