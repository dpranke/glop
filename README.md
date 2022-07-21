GLOP
====

GLOP - Generalized Lpeg and OMeta-inspired Parsing and printing framework.

Introduction
------------

GLOP is an exploration of parsing expression grammars, mostly influenced
by Lua's [LPEG](http://www.inf.puc-rio.br/~roberto/lpeg) module and
Alessandro Warth's [OMeta](http://github.com/alexwarth/ometa-js/)
and [Ohm](https://ohmlang.github.io/) projects.

It is, of course, also heavily influenced by grep and friends as well.

It is intended to provide several different things:

1.  A tool with a friendly command line interface for searching for
    things a la grep, and transforming them a la sed, awk, perl -e and
    so forth.
2.  Libraries in several languages to match the functionality of that
    tool.
3.  A tool for generating parsers in multiple languages for a given
    grammar.
4.  Libraries for the above as well.
5.  A study in implementing a non-trivial problem in multiple languages.

What works:
-----------

At the moment, GLOP can accept grammars and execute them using a *very*
simple language for executing actions on the parsed text.

The code is only implemented in Python.

Things that still need to be implemented:
-----------------------------------------

-   Grammar features:
    -   Left-recursion.
    -   Operator precedence and associativity.
    -   Whitespace-insensitive rules.
    -   Handling of indentation-sensitive grammars.
    -   Support for inheritance and external rules.
    -   Safe context sensitivity (i.e., support for saving values safely
        in the parse context and being able to use them during the parse).
    -   Support for error recovery and warnings.
-   Input formats and specifications:
    -   A different format for the grammars that is more JSON5-y.
    -   Specifying the ASTs (aka "walkers" or "semantics (a la Ohm) in a
        separate definition block.
    -   Support for specifying type declarations in the walkers.
    -   Specifying multiple walkers.
    -   Concrete syntax trees and preserving comments when pretty-printing
        grammars (and more consistency for handling `->` for ASTs).
-   General engineering:
    -   Documentation.
    -   Better templating (?).
    -   More testing.
    -   More error checking and handling:
        - Unused or illegal positional vars
        - Unused named vars
        - Unused rules
        - Unused return values
        - Left recursion
        - Rules that will never match
        - Type checking of return values
    -   An interpreter that doesn't rely on eval'ing the compiled code.
    -   Lots of performance tuning.
    -   LPEG-style bytecode?
    -   Generators for languages other than Python. Priority: Go, TypeScript,
        JavaScript, C, C++, Java, others.
    -   Implementations for languages other than Python (same priority).
    -   Grep-like matching (i.e., LPEG-style pattern matching and
        substitution) on the command-line and in APIs.

Open issues
-----------

Basically, everything is still open.

One of the distinctive aspects of LPEG is its focus on matching
patterns, rather than entire grammars. Focusing on patterns leads one to
a syntax more tuned for patterns, as terminals are more common than
non-terminals.
