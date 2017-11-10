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

import sys


if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr


def _enc(ch, esc_dquote):
    bslash = '\\'
    dquote = '"'
    if dquote < ch < bslash or bslash < ch < chr(128) or ch in ' !':
        return ch
    elif ch == bslash:
        return bslash + bslash
    elif ch == dquote:
        return (bslash + dquote) if esc_dquote else dquote
    elif ch == '\b':
        return bslash + 'b'
    elif ch == '\f':
        return bslash + 'f'
    elif ch == '\n':
        return bslash + 'n'
    elif ch == '\r':
        return bslash + 'r'
    elif ch == '\t':
        return bslash + 't'
    elif ch == '\v':
        return bslash + 'v'
    elif ord(ch) < 256:
        return '\\x%02x' % ord(ch)
    else:
        return '\\u%04x' % ord(ch)


def encode(s):
    squote = "'"
    dquote = '"'
    is_unicode = any(ord(ch) > 256 for ch in s) or '\\u' in s or '\\U' in s
    prefix = 'u' if is_unicode else ''
    has_squote = any(ch == "'" for ch in s)
    if has_squote:
        return (prefix + dquote +
                ''.join(_enc(ch, esc_dquote=True) for ch in s) + dquote)
    else:
        return (prefix + squote +
                ''.join(_enc(ch, esc_dquote=False) for ch in s) + squote)
