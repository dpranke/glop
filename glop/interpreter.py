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

class Interpreter(object):
    def __init__(self, compiled_text, class_name):
        scope = {}
        self.compiled_text = compiled_text
        self.class_name = class_name
        exec compiled_text in scope
        self.parser_cls = scope[class_name]

    def interpret(self, contents, path):
        parser = self.parser_cls(contents, path)
        return parser.parse()
