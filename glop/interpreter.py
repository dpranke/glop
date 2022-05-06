# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from glop.compiler import Compiler


class Interpreter(object):
    def __init__(self, grammar, memoize):
        self.memoize = memoize
        self.grammar = grammar
        self.parser_cls = None

    def interpret(self, contents, path):
        if not self.parser_cls:
            scope = {}
            comp = Compiler(self.grammar, 'Parser', main_wanted=False,
                            memoize=self.memoize)
            compiled_text, err = comp.compile()
            if err:
                return None, err, _
            exec(compiled_text, scope)
            self.parser_cls = scope['Parser']

        parser = self.parser_cls(contents, path)
        return parser.parse()
