grammar = sp*

sp      = '\x20' | '\x09' | eol | comment

comment     = '//' (~eol anything)* 
            | '/*' (~'*/' anything)* '*/'

eol     = '\x0D\x0A' | '\x0D' | '\x0A'

