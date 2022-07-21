# Copyright 2017 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
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


def unquote(obj, val):
    if isinstance(obj, list):
        if obj[0] == 'if':
            assert obj[1][0] == '.'
            if obj[1] == '.':
                flg = val
            else:
                flg = val[obj[1][1:]]
            if flg:
                return [unquote(obj[2], val)]
            elif len(obj) == 4:
                return [unquote(obj[3], val)]
            else:
                return []
        elif obj[0] == 'for':
            r = []
            for v in val[obj[1]]:
                r.append(unquote(obj[2], v))
            return r
        elif obj[0] == 'var':
            assert obj[1][0] == '.'
            if obj[1] == '.':
                return val
            else:
                return val[obj[1][1:]]
        else:
            r = []
            for el in obj:
                if isinstance(el, list) and el:
                    if el[0] in ('if', 'for'):
                        r.extend(unquote(el, val))
                    else:
                        r.append(unquote(el, val))
                else:
                    r.append(unquote(el, val))
            return r 
    else:
        return obj


def format(box):
    return '\n'.join(l.rstrip() for l in _Box().format(box).splitlines())


class _Box(object):
    def __init__(self, indent=4, width=80):
        self.indent = indent
        self.istr = ' ' * self.indent
        self.ivstr = '\n' + self.istr
        self.width = width

    def format(self, box):
        if isinstance(box, list):
            meth = getattr(self, 'op_' + box[0])
            return meth(box)
        else:
            return str(box)

    def op_h(self, box):
        r = ''
        cur_line = ''
        for b in box[1:]:
            b_lines = self.format(b).splitlines()
            if len(b_lines) > 1:
                r += cur_line + b_lines[0]
                if len(b_lines) > 2:
                    r += '\n' + self.format(['v'] +
                                            [['h', ['w', cur_line], b_line]
                                             for b_line in b_lines[1:-1]])
                r += '\n'
                cur_line = self.format(['h', ['w', cur_line], b_lines[-1]])
            else:
                cur_line += b_lines[0]
        return r + cur_line

    def op_i(self, box):
        return self.istr + self.ivstr.join(self.format(box[1]).splitlines())

    def op_iv(self, box):
        return self.istr + self.ivstr.join(self.op_v(box).splitlines())

    def op_v(self, box):
        return '\n'.join(self.format(b) for b in box[1:])

    def op_w(self, box):
        return ' ' * len(box[1])
