# pylint: disable=too-many-lines


class Parser:
    def __init__(self, msg, fname):
        self.msg = msg
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0
        self._scopes = []

    def parse(self):
        self._r_grammar_0()
        if self.failed:
            return self._err()
        return self.val, None, self.pos

    def _err(self):
        lineno = 1
        colno = 1
        for ch in self.msg[: self.errpos]:
            if ch == "\n":
                lineno += 1
                colno = 1
            else:
                colno += 1
        if self.errpos == len(self.msg):
            thing = "end of input"
        else:
            thing = repr(self.msg[self.errpos]).replace("'", '"')
        err_str = "%s:%d Unexpected %s at column %d" % (
            self.fname,
            lineno,
            thing,
            colno,
        )
        return None, err_str, self.errpos

    def _r_bslash_0(self):
        self._h_ch("\\")

    def _r_choice_0(self):
        self._h_scope(
            [
                lambda: self._h_label(lambda: self._r_seq_0(), "_1"),
                lambda: self._h_label(
                    lambda: self._h_star(
                        lambda: self._h_paren(
                            lambda: self._h_seq(
                                [
                                    lambda: self._r_sp_0(),
                                    lambda: self._h_ch("|"),
                                    lambda: self._r_sp_0(),
                                    lambda: self._r_seq_0(),
                                ]
                            )
                        )
                    ),
                    "_2",
                ),
                lambda: self._h_succeed(
                    ["choice", [self._h_get("_1")] + self._h_get("_2")]
                ),
            ]
        )

    def _r_comment_0(self):
        self._h_choice(
            [
                lambda: self._h_seq(
                    [
                        lambda: self._h_str("//"),
                        lambda: self._h_star(
                            lambda: self._h_paren(
                                lambda: self._h_seq(
                                    [
                                        lambda: self._h_not(
                                            lambda: self._r_eol_0()
                                        ),
                                        lambda: self._r_anything_0(),
                                    ]
                                )
                            )
                        ),
                    ]
                ),
                lambda: self._h_seq(
                    [
                        lambda: self._h_str("/*"),
                        lambda: self._h_star(
                            lambda: self._h_paren(
                                lambda: self._h_seq(
                                    [
                                        lambda: self._h_not(
                                            lambda: self._h_str("*/")
                                        ),
                                        lambda: self._r_anything_0(),
                                    ]
                                )
                            )
                        ),
                        lambda: self._h_str("*/"),
                    ]
                ),
            ]
        )

    def _r_digit_0(self):
        self._h_range("0", "9")

    def _r_dqchar_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._r_bslash_0(),
                        lambda: self._h_label(
                            lambda: self._r_esc_char_0(), "_2"
                        ),
                        lambda: self._h_succeed(self._h_get("_2")),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_not(lambda: self._r_dquote_0()),
                        lambda: self._h_label(
                            lambda: self._r_anything_0(), "_2"
                        ),
                        lambda: self._h_succeed(self._h_get("_2")),
                    ]
                ),
            ]
        )

    def _r_dquote_0(self):
        self._h_ch('"')

    def _r_eol_0(self):
        self._h_choice(
            [
                lambda: self._h_str("\r\n"),
                lambda: self._h_ch("\r"),
                lambda: self._h_ch("\n"),
            ]
        )

    def _r_esc_char_0(self):
        self._h_choice(
            [
                lambda: self._h_seq(
                    [lambda: self._h_ch("b"), lambda: self._h_succeed("\b")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("d"), lambda: self._h_succeed("\\d")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("f"), lambda: self._h_succeed("\f")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("n"), lambda: self._h_succeed("\n")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("r"), lambda: self._h_succeed("\r")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("s"), lambda: self._h_succeed("\\s")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("t"), lambda: self._h_succeed("\t")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("v"), lambda: self._h_succeed("\v")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("w"), lambda: self._h_succeed("\\w")]
                ),
                lambda: self._h_seq(
                    [lambda: self._r_squote_0(), lambda: self._h_succeed("'")]
                ),
                lambda: self._h_seq(
                    [lambda: self._r_dquote_0(), lambda: self._h_succeed('"')]
                ),
                lambda: self._h_seq(
                    [lambda: self._r_bslash_0(), lambda: self._h_succeed("\\")]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_hex_esc_0(), "_1"
                        ),
                        lambda: self._h_succeed(self._h_get("_1")),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_unicode_esc_0(), "_1"
                        ),
                        lambda: self._h_succeed(self._h_get("_1")),
                    ]
                ),
            ]
        )

    def _r_expr_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_post_expr_0(), "_1"
                        ),
                        lambda: self._h_ch(":"),
                        lambda: self._h_label(lambda: self._r_ident_0(), "_3"),
                        lambda: self._h_succeed(
                            ["label", self._h_get("_1"), self._h_get("_3")]
                        ),
                    ]
                ),
                lambda: self._r_post_expr_0(),
            ]
        )

    def _r_grammar_0(self):
        self._h_scope(
            [
                lambda: self._h_label(
                    lambda: self._h_star(
                        lambda: self._h_paren(
                            lambda: self._h_seq(
                                [
                                    lambda: self._r_sp_0(),
                                    lambda: self._r_rule_0(),
                                ]
                            )
                        )
                    ),
                    "_1",
                ),
                lambda: self._r_sp_0(),
                lambda: self._r_end_0(),
                lambda: self._h_succeed(["rules", self._h_get("_1")]),
            ]
        )

    def _r_hex_0(self):
        self._h_choice(
            [
                lambda: self._r_digit_0(),
                lambda: self._h_range("a", "f"),
                lambda: self._h_range("A", "F"),
            ]
        )

    def _r_hex_esc_0(self):
        self._h_scope(
            [
                lambda: self._h_ch("x"),
                lambda: self._h_label(
                    lambda: self._h_capture(
                        lambda: self._h_seq(
                            [lambda: self._r_hex_0(), lambda: self._r_hex_0()]
                        )
                    ),
                    "_2",
                ),
                lambda: self._h_succeed(self._f_xtou(self._h_get("_2"))),
            ]
        )

    def _r_id_continue_0(self):
        self._h_choice(
            [lambda: self._r_id_start_0(), lambda: self._r_digit_0()]
        )

    def _r_id_start_0(self):
        self._h_choice(
            [
                lambda: self._h_range("a", "z"),
                lambda: self._h_range("A", "Z"),
                lambda: self._h_ch("_"),
            ]
        )

    def _r_ident_0(self):
        self._h_capture(
            lambda: self._h_seq(
                [
                    lambda: self._r_id_start_0(),
                    lambda: self._h_star(lambda: self._r_id_continue_0()),
                ]
            )
        )

    def _r_lit_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._r_squote_0(),
                        lambda: self._h_label(
                            lambda: self._h_star(lambda: self._r_sqchar_0()),
                            "_2",
                        ),
                        lambda: self._r_squote_0(),
                        lambda: self._h_succeed(
                            ["lit", self._f_cat(self._h_get("_2"))]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._r_dquote_0(),
                        lambda: self._h_label(
                            lambda: self._h_star(lambda: self._r_dqchar_0()),
                            "_2",
                        ),
                        lambda: self._r_dquote_0(),
                        lambda: self._h_succeed(
                            ["lit", self._f_cat(self._h_get("_2"))]
                        ),
                    ]
                ),
            ]
        )

    def _r_ll_expr_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_ll_qual_0(), "_1"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("+"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_5"
                        ),
                        lambda: self._h_succeed(
                            ["ll_plus", self._h_get("_1"), self._h_get("_5")]
                        ),
                    ]
                ),
                lambda: self._r_ll_qual_0(),
            ]
        )

    def _r_ll_exprs_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_1"
                        ),
                        lambda: self._h_label(
                            lambda: self._h_star(
                                lambda: self._h_paren(
                                    lambda: self._h_seq(
                                        [
                                            lambda: self._r_sp_0(),
                                            lambda: self._h_ch(","),
                                            lambda: self._r_sp_0(),
                                            lambda: self._r_ll_expr_0(),
                                        ]
                                    )
                                )
                            ),
                            "_2",
                        ),
                        lambda: self._h_succeed(
                            [self._h_get("_1")] + self._h_get("_2")
                        ),
                    ]
                ),
                lambda: self._h_succeed([]),
            ]
        )

    def _r_ll_post_op_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("["),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("]"),
                        lambda: self._h_succeed(
                            ["ll_getitem", self._h_get("_3")]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("("),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_exprs_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch(")"),
                        lambda: self._h_succeed(["ll_call", self._h_get("_3")]),
                    ]
                ),
            ]
        )

    def _r_ll_prim_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_ident_0(), "_1"),
                        lambda: self._h_succeed(["ll_var", self._h_get("_1")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_str("0x"),
                        lambda: self._h_label(
                            lambda: self._h_plus(lambda: self._r_hex_0()), "_2"
                        ),
                        lambda: self._h_succeed(
                            ["ll_hex", self._f_cat(self._h_get("_2"))]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._h_plus(lambda: self._r_digit_0()),
                            "_1",
                        ),
                        lambda: self._h_succeed(
                            ["ll_dec", self._f_cat(self._h_get("_1"))]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_lit_0(), "_1"),
                        lambda: self._h_succeed(
                            ["ll_str", self._h_get("_1")[1]]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("("),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch(")"),
                        lambda: self._h_succeed(
                            ["ll_paren", self._h_get("_3")]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("["),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_exprs_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("]"),
                        lambda: self._h_succeed(["ll_arr", self._h_get("_3")]),
                    ]
                ),
            ]
        )

    def _r_ll_qual_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_ll_prim_0(), "_1"
                        ),
                        lambda: self._h_label(
                            lambda: self._h_plus(
                                lambda: self._r_ll_post_op_0()
                            ),
                            "_2",
                        ),
                        lambda: self._h_succeed(
                            ["ll_qual", self._h_get("_1"), self._h_get("_2")]
                        ),
                    ]
                ),
                lambda: self._r_ll_prim_0(),
            ]
        )

    def _r_post_expr_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_prim_expr_0(), "_1"
                        ),
                        lambda: self._h_label(
                            lambda: self._r_post_op_0(), "_2"
                        ),
                        lambda: self._h_succeed(
                            [self._h_get("_2"), self._h_get("_1")]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(
                            lambda: self._r_prim_expr_0(), "_1"
                        ),
                        lambda: self._h_succeed(self._h_get("_1")),
                    ]
                ),
            ]
        )

    def _r_post_op_0(self):
        self._h_choice(
            [
                lambda: self._h_seq(
                    [lambda: self._h_ch("?"), lambda: self._h_succeed("opt")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("*"), lambda: self._h_succeed("star")]
                ),
                lambda: self._h_seq(
                    [lambda: self._h_ch("+"), lambda: self._h_succeed("plus")]
                ),
            ]
        )

    def _r_prim_expr_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_lit_0(), "_1"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_str(".."),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(lambda: self._r_lit_0(), "_5"),
                        lambda: self._h_succeed(
                            ["range", self._h_get("_1"), self._h_get("_5")]
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_lit_0(), "_1"),
                        lambda: self._h_succeed(self._h_get("_1")),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_ident_0(), "_1"),
                        lambda: self._h_not(
                            lambda: self._h_paren(
                                lambda: self._h_seq(
                                    [
                                        lambda: self._r_sp_0(),
                                        lambda: self._h_ch("="),
                                    ]
                                )
                            )
                        ),
                        lambda: self._h_succeed(["apply", self._h_get("_1")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("("),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(lambda: self._r_choice_0(), "_3"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch(")"),
                        lambda: self._h_succeed(["paren", self._h_get("_3")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("~"),
                        lambda: self._h_label(
                            lambda: self._r_prim_expr_0(), "_2"
                        ),
                        lambda: self._h_succeed(["not", self._h_get("_2")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_str("->"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_3"
                        ),
                        lambda: self._h_succeed(["action", self._h_get("_3")]),
                    ]
                ),
                lambda: self._h_seq(
                    [
                        lambda: self._h_str("{}"),
                        lambda: self._h_succeed(["pos"]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("{"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(lambda: self._r_choice_0(), "_3"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("}"),
                        lambda: self._h_succeed(["capture", self._h_get("_3")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_str("={"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("}"),
                        lambda: self._h_succeed(["eq", self._h_get("_3")]),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_str("?{"),
                        lambda: self._r_sp_0(),
                        lambda: self._h_label(
                            lambda: self._r_ll_expr_0(), "_3"
                        ),
                        lambda: self._r_sp_0(),
                        lambda: self._h_ch("}"),
                        lambda: self._h_succeed(["pred", self._h_get("_3")]),
                    ]
                ),
            ]
        )

    def _r_rule_0(self):
        self._h_scope(
            [
                lambda: self._h_label(lambda: self._r_ident_0(), "_1"),
                lambda: self._r_sp_0(),
                lambda: self._h_ch("="),
                lambda: self._r_sp_0(),
                lambda: self._h_label(lambda: self._r_choice_0(), "_5"),
                lambda: self._r_sp_0(),
                lambda: self._h_opt(lambda: self._h_ch(",")),
                lambda: self._h_succeed(
                    ["rule", self._h_get("_1"), self._h_get("_5")]
                ),
            ]
        )

    def _r_seq_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_label(lambda: self._r_expr_0(), "_1"),
                        lambda: self._h_label(
                            lambda: self._h_star(
                                lambda: self._h_paren(
                                    lambda: self._h_seq(
                                        [
                                            lambda: self._r_ws_0(),
                                            lambda: self._r_sp_0(),
                                            lambda: self._r_expr_0(),
                                        ]
                                    )
                                )
                            ),
                            "_2",
                        ),
                        lambda: self._h_succeed(
                            ["seq", [self._h_get("_1")] + self._h_get("_2")]
                        ),
                    ]
                ),
                lambda: self._h_succeed(["empty"]),
            ]
        )

    def _r_sp_0(self):
        self._h_star(lambda: self._r_ws_0())

    def _r_sqchar_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._r_bslash_0(),
                        lambda: self._h_label(
                            lambda: self._r_esc_char_0(), "_2"
                        ),
                        lambda: self._h_succeed(self._h_get("_2")),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_not(lambda: self._r_squote_0()),
                        lambda: self._h_label(
                            lambda: self._r_anything_0(), "_2"
                        ),
                        lambda: self._h_succeed(self._h_get("_2")),
                    ]
                ),
            ]
        )

    def _r_squote_0(self):
        self._h_ch("'")

    def _r_unicode_esc_0(self):
        self._h_choice(
            [
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("u"),
                        lambda: self._h_label(
                            lambda: self._h_capture(
                                lambda: self._h_seq(
                                    [
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                    ]
                                )
                            ),
                            "_2",
                        ),
                        lambda: self._h_succeed(
                            self._f_xtou(self._h_get("_2"))
                        ),
                    ]
                ),
                lambda: self._h_scope(
                    [
                        lambda: self._h_ch("U"),
                        lambda: self._h_label(
                            lambda: self._h_capture(
                                lambda: self._h_seq(
                                    [
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                        lambda: self._r_hex_0(),
                                    ]
                                )
                            ),
                            "_2",
                        ),
                        lambda: self._h_succeed(
                            self._f_xtou(self._h_get("_2"))
                        ),
                    ]
                ),
            ]
        )

    def _r_ws_0(self):
        self._h_choice(
            [
                lambda: self._h_ch(" "),
                lambda: self._h_ch("\t"),
                lambda: self._r_eol_0(),
                lambda: self._r_comment_0(),
            ]
        )

    def _f_cat(self, vals):  # pylint: disable=no-self-use
        return "".join(vals)

    def _f_xtou(self, s):  # pylint: disable=no-self-use
        return chr(int(s, base=16))

    def _h_capture(self, rule):
        start = self.pos
        rule()
        if not self.failed:
            self._h_succeed(self.msg[start : self.pos], self.pos)

    def _h_ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._h_succeed(ch, p + 1)
        else:
            self._h_fail()

    def _h_choice(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._h_rewind(p)
        rules[-1]()

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_get(self, var):
        return self._scopes[-1][var]

    def _h_label(self, rule, var):
        rule()
        if not self.failed:
            self._h_set(var, self.val)

    def _h_not(self, rule):
        p = self.pos
        errpos = self.errpos
        rule()
        if self.failed:
            self._h_succeed(None, p)
        else:
            self._h_rewind(p)
            self.errpos = errpos
            self._h_fail()

    def _h_opt(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._h_succeed([], p)
        else:
            self._h_succeed([self.val])

    def _h_paren(self, rule):  # pylint: disable=no-self-use
        rule()

    def _h_plus(self, rule):
        rule()
        if self.failed:
            return
        self._h_star(rule, [self.val])

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, rules):
        self._scopes.append({})
        for rule in rules:
            rule()
            if self.failed:
                self._scopes.pop()
                return
        self._scopes.pop()

    def _h_seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _h_set(self, var, val):
        self._scopes[-1][var] = val

    def _h_star(self, rule, vs=None):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._h_rewind(p)
                break
            vs.append(self.val)
        self._h_succeed(vs)

    def _h_str(self, s):
        i = 0
        while not self.failed and i < len(s):
            self._h_ch(s[i])
            i += 1

    def _h_succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos

    def _r_anything_0(self):
        if self.pos < self.end:
            self._h_succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._h_fail()

    def _r_end_0(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()
