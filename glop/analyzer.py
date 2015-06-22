# Copyright 2014 Google Inc. All rights reserved.
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
    def __init__(self, rules, start):
        self.rules = rules
        self.start = start


class Analyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def analyze(self):
        rules = OrderedDict()
        for n in self.ast:
            assert n[0] == 'rule'
            rules[n[1]] = n[2]

        return Grammar(rules, 'grammar'), None
