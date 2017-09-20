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

from collections import OrderedDict


class Grammar(object):
    def __init__(self, ast):
        self.ast = ast
        self.starting_rule = ast[0][1]
        self.rules = dict((n[1], n[2]) for n in ast)


class Analyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def analyze(self):
        ok = self.check_ast_is_a_list_of_rules()
        if not ok:
            return None, 'malformed ast'
        return Grammar(self.ast), None

    def check_ast_is_a_list_of_rules(self):
        return all(n[0] == 'rule' for n in self.ast)
