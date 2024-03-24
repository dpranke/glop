grammar = sp bar (sp '|' bar)* sp end -> [ 'bars', [_1] + _2]

sp      = ' '

bar     = 'bar'

