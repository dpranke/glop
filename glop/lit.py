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

def _enc(ch, esc_dquote):
    bslash = '\\'
    dquote = '"'
    if dquote < ch < bslash or bslash < ch < chr(128) or ch in ' !':
        return ch
    if ch == bslash:
        return bslash + bslash
    if ch == dquote:
        return (bslash + dquote) if esc_dquote else dquote
    if ch == '\b':
        return bslash + 'b'
    if ch == '\f':
        return bslash + 'f'
    if ch == '\n':
        return bslash + 'n'
    if ch == '\r':
        return bslash + 'r'
    if ch == '\t':
        return bslash + 't'
    if ch == '\v':
        return bslash + 'v'
    return '\\u%04x' % ord(ch)


def encode(s):
    squote = "'"
    dquote = '"'
    is_unicode = any(ord(ch) > 128 for ch in s) or '\\u' in s or '\\U' in s
    prefix = 'u' if is_unicode else ''
    has_squote = any(ch == "'" for ch in s)
    if has_squote:
        return (prefix + dquote +
                ''.join(_enc(ch, esc_dquote=True) for ch in s) + dquote)
    return (prefix + squote +
            ''.join(_enc(ch, esc_dquote=False) for ch in s) + squote)
