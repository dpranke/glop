GLOP
====

GLOP - the Generalized Lpeg and Ometa-inspired Parsing and printing framework.

Introduction
------------

GLOP is an exploration of parsing expression grammars, mostly influenced by
Lua's LPEG_ module and Alessandro Warth's OMeta_ project. It is of course
also heavily influenced by grep and friends.

It is intended to provide several different things:

1. A tool and with a friendly command line interface for searching for things
   a la grep, and transforming them a la sed, awk, perl -e and so forth.

2. Libraries in several languages to match the functionality of that tool.

3. A tool for generating parsers in multiple languages for a given grammar.

4. Libraries for the above as well.

5. A study in implementing a non-trivial problem in multiple languages.

What works
----------

At the moment, GLOP can accept grammars and execute them using a *very* 
simple language for executing actions on the parsed text.

The code is only implemented in Python.

Things that still need to be implemented
----------------------------------------

* parser generators.

* a generated parser that matches the hand-rolled one (glop needs to be 
  able to bootstrap itself up).

Open issues
-----------

Basically, everything is still open. 

One of the distinctive aspects of LPEG is its focus on matching patterns,
rather than entire grammars. Focusing on patterns leads one to a syntax
more tuned for patterns, as terminals are more common than non-terminals.

.. _LPEG: http://www.inf.puc-rio.br/~roberto/lpeg
.. _OMeta: http://github.com/alexwarth/ometa-js/
