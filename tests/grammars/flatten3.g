grammar = ~bug id end

bug = 'Bug(' ('a'..'z')+ ')'

id  = (~(' ' | '\n' | '#') anything)+

