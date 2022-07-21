// This file contains definitions of the various Unicode character classes
// as defined in the Unicode Character Database, version 9.0.0
// (see http://www.unicode.org/reports/tr44/tr44-18.html and
// http://www.unicode.org/Public/9.0.0/ucd/PropertyValueAliases.txt).

C                     = Cc | Cf | Cn | Co | Cs
Cc                    = anything:x ?{is_unicat(x, 'Cc')} -> x
Cf                    = anything:x ?{is_unicat(x, 'Cf')} -> x
Cn                    = anything:x ?{is_unicat(x, 'Cn')} -> x
Co                    = anything:x ?{is_unicat(x, 'Co')} -> x
Cs                    = anything:x ?{is_unicat(x, 'Cs')} -> x

L                     = Ll | Lm | Lo | Lt | Lu
Ll                    = anything:x ?{is_unicat(x, 'Ll')} -> x
Lm                    = anything:x ?{is_unicat(x, 'Lm')} -> x
Lo                    = anything:x ?{is_unicat(x, 'Lo')} -> x
Lt                    = anything:x ?{is_unicat(x, 'Lt')} -> x
Lu                    = anything:x ?{is_unicat(x, 'Lu')} -> x

M                     = Mc | Me | Mn
Mc                    = anything:x ?{is_unicat(x, 'Mc')} -> x
Me                    = anything:x ?{is_unicat(x, 'Me')} -> x
Mn                    = anything:x ?{is_unicat(x, 'Mn')) -> x

N                     = Nd | Nl | No
Nd                    = anything:x ?{is_unicat(x, 'Nd')} -> x
Nl                    = anything:x ?{is_unicat(x, 'Nl')} -> x
No                    = anything:x ?{is_unicat(x, 'No')} -> x

P                     = Pc | Pd | Pe | Pf | Pi | Po | Ps
Pc                    = anything:x ?{is_unicat(x, 'Pc')} -> x
Pd                    = anything:x ?{is_unicat(x, 'Pd')} -> x
Pe                    = anything:x ?{is_unicat(x, 'Pe')} -> x
Pf                    = anything:x ?{is_unicat(x, 'Pf')} -> x
Pi                    = anything:x ?{is_unicat(x, 'Pi')} -> x
Po                    = anything:x ?{is_unicat(x, 'Po')} -> x
Ps                    = anything:x ?{is_unicat(x, 'Ps')} -> x

S                     = Sc | Sk | Sm | So
Sc                    = anything:x ?{is_unicat(x, 'Sc')} -> x
Sm                    = anything:x ?{is_unicat(x, 'Sm')} -> x
Sk                    = anything:x ?{is_unicat(x, 'Sk')} -> x
So                    = anything:x ?{is_unicat(x, 'So')) -> x

Z                     = Zl | Zp | Zs
Zl                    = anything:x ?{is_unicat(x, 'Zl')} -> x
Zp                    = anything:x ?{is_unicat(x, 'Zp')} -> x
Zs                    = anything:x ?{is_unicat(x, 'Zs')} -> x

// These are the readable aliases for the above categories, given in
// http://www.unicode.org/Public/9.0.0/ucd/PropertyValueAliases.txt
// (in the general category)

Other                 = C
Control               = Cc
Format                = Cf
Unassigned            = Cn
Private_Use           = Co
Surrogate             = Cs

Letter                = L
Uppercase_Letter      = Lu
Lowercase_Letter      = Ll
TitleCase_Letter      = Lt
Modifier_Letter       = Lm
Other_Letter          = Lo

Mark                  = M
Nonspacing_Mark       = Mn
Spacing_Mark          = Mc
Enclosing_Mark        = Me

Number                = N
Decimal_Number        = Nd
Letter_Number         = Nl
Other_Number          = No

Punctuation           = P
Connector_Punctuation = Pc
Dash_Punctuation      = Pd
Close_Punctuation     = Pe
Final_Punctuation     = Pf
Initial_Punctuation   = Pi
Other_Punctuation     = Po
Open_Punctuation      = Ps

Symbol                = S
Current_Symbol        = Sc
Modifier_Symbol       = Sk
Math_Symbol           = Sm
Other_Symbol          = So

Separator             = Z
Line_Separator        = Zl
Paragraph_Separator   = Zp
Space_Separator       = Zs

// ID_Start and ID_Continue are defined in Unicode Standard Annex #31,
// Unicode Identifier and Pattern Syntax. See
// http://www.unicode.org/reports/tr31/tr31-25.html and
// http://www.unicode.org/Public/9.0.0/ucd/PropList.txt
//
// The zero-width characters are also used in that annex.

ID_Start              = L | Nl | Other_ID_Start

ID_Continue           = ID_Start | Mn | Mc | Nd | Pc | Other_ID_Continue

ZWJ                   = '\u200C'
ZWNJ                  = '\u200D'

Zero_Width_Joiner     = ZWJ
Zero_Width_Nonjoiner  = ZWNJ

Other_ID_Start        = '\u1885' | '\u1886' | '\u2118'
                      | '\u212E' | '\u309B' | '\u309C'

Other_ID_Continue     = '\u00B7'
                      | '\u0387'
                      | '\u1369'..'\u1371'
                      | '\u19DA'

Pattern_White_Space   = '\u0009'..'\u000D'
                      | '\u0020'
                      | '\u0085'            
                      | '\u200E'
                      | '\u200F'
                      | '\u2028'
                      | '\u2029'

Pattern_Syntax        = '\u0021'..'\u002F'
                      | '\u003A'..'\u0040'
                      | '\u005B'..'\u005E'
                      | '\u0060'
                      | '\u007B'..'\u007E'
                      | '\u00A1'..'\u00A7'
                      | '\u00A9'
                      | '\u00AB'..'\u00AC'
                      | '\u00AE'
                      | '\u00B0'..'\u00B1'
                      | '\u00B6'
                      | '\u00BB'
                      | '\u00BF'
                      | '\u00D7'
                      | '\u00F7'
                      | '\u2010'..'\u2027'
                      | '\u2030'..'\u203E'
                      | '\u2041'..'\u2053'
                      | '\u2055'..'\u205E'
                      | '\u2190'..'\u245F'
                      | '\u2500'..'\u2775'
                      | '\u2794'..'\u2BFF'
                      | '\u2E00'..'\u2E7F'
                      | '\u3001'..'\u3003'
                      | '\u3008'..'\u3020'
                      | '\u3030'
                      | '\uFD3E'..'\uFD3F'
                      | '\uFE45'..'\uFE46'
