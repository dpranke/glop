grammar = '"' (~'"' anything)*:as '"' '\n' end -> cat(as)
