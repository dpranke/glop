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
        self._seeds = {}
        self._blocked = set()
        self._cache = {}

    def parse(self):
        self._r_grammar_0()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos


    def _r_bslash_0(self):
        self._h_str('\\')

    def _r_choice_0(self):
        self._h_scope('_r_choice_0', [
            self._r_choice_1,
            self._r_choice_2,
            self._r_choice_3
        ])

    def _r_choice_1(self):
        self._h_bind(self._r_seq_0, '_1')

    def _r_choice_2(self):
        self._h_bind(self._r_choice_4, '_2')

    def _r_choice_3(self):
        self._h_succeed(['choice', [self._h_get('_1')] + self._h_get('_2')])

    def _r_choice_4(self):
        return self._h_star(self._r_choice_5)

    def _r_choice_5(self):
        self._h_paren(self._r_choice_6)

    def _r_choice_6(self):
        self._h_seq([
            self._r_sp_0,
            lambda: self._h_str('|'),
            self._r_sp_0,
            self._r_seq_0
        ])

    def _r_comment_0(self):
        self._h_choice([self._r_comment_1, self._r_comment_2])

    def _r_comment_1(self):
        self._h_seq([
            lambda: self._h_str('//'),
            self._r_comment_3
        ])

    def _r_comment_2(self):
        self._h_seq([
            lambda: self._h_str('/*'),
            self._r_comment_4,
            lambda: self._h_str('*/')
        ])

    def _r_comment_3(self):
        return self._h_star(self._r_comment_5)

    def _r_comment_4(self):
        return self._h_star(self._r_comment_6)

    def _r_comment_5(self):
        self._h_paren(self._r_comment_7)

    def _r_comment_6(self):
        self._h_paren(self._r_comment_8)

    def _r_comment_7(self):
        self._h_seq([self._r_comment_9, self._r_anything_0])

    def _r_comment_8(self):
        self._h_seq([self._r_comment_10, self._r_anything_0])

    def _r_comment_9(self):
        self._h_not(self._r_comment_11)

    def _r_comment_10(self):
        self._h_not(self._r_comment_12)

    def _r_comment_11(self):
        self._r_eol_0()

    def _r_comment_12(self):
        self._h_str('*/')

    def _r_digit_0(self):
        self._h_range('0', '9')

    def _r_dqchar_0(self):
        self._h_choice([self._r_dqchar_1, self._r_dqchar_2])

    def _r_dqchar_1(self):
        self._h_scope('_r_dqchar_1', [
            self._r_bslash_0,
            self._r_dqchar_3,
            self._r_dqchar_4
        ])

    def _r_dqchar_2(self):
        self._h_scope('_r_dqchar_2', [
            self._r_dqchar_5,
            self._r_dqchar_6,
            self._r_dqchar_7
        ])

    def _r_dqchar_3(self):
        self._h_bind(self._r_esc_char_0, '_2')

    def _r_dqchar_4(self):
        self._h_succeed(self._h_get('_2'))

    def _r_dqchar_5(self):
        self._h_not(self._r_dqchar_8)

    def _r_dqchar_6(self):
        self._h_bind(self._r_anything_0, '_2')

    def _r_dqchar_7(self):
        self._h_succeed(self._h_get('_2'))

    def _r_dqchar_8(self):
        self._r_dquote_0()

    def _r_dquote_0(self):
        self._h_str('"')

    def _r_eol_0(self):
        self._h_choice([
            lambda: self._h_str('\r\n'),
            lambda: self._h_str('\r'),
            lambda: self._h_str('\n')
        ])

    def _r_esc_char_0(self):
        self._h_choice([
            self._r_esc_char_1,
            self._r_esc_char_2,
            self._r_esc_char_3,
            self._r_esc_char_4,
            self._r_esc_char_5,
            self._r_esc_char_6,
            self._r_esc_char_7,
            self._r_esc_char_8,
            self._r_esc_char_9,
            self._r_esc_char_10,
            self._r_esc_char_11,
            self._r_esc_char_12,
            self._r_esc_char_13,
            self._r_esc_char_14
        ])

    def _r_esc_char_1(self):
        self._h_seq([
            lambda: self._h_str('b'),
            self._r_esc_char_15
        ])

    def _r_esc_char_2(self):
        self._h_seq([
            lambda: self._h_str('d'),
            self._r_esc_char_16
        ])

    def _r_esc_char_3(self):
        self._h_seq([
            lambda: self._h_str('f'),
            self._r_esc_char_17
        ])

    def _r_esc_char_4(self):
        self._h_seq([
            lambda: self._h_str('n'),
            self._r_esc_char_18
        ])

    def _r_esc_char_5(self):
        self._h_seq([
            lambda: self._h_str('r'),
            self._r_esc_char_19
        ])

    def _r_esc_char_6(self):
        self._h_seq([
            lambda: self._h_str('s'),
            self._r_esc_char_20
        ])

    def _r_esc_char_7(self):
        self._h_seq([
            lambda: self._h_str('t'),
            self._r_esc_char_21
        ])

    def _r_esc_char_8(self):
        self._h_seq([
            lambda: self._h_str('v'),
            self._r_esc_char_22
        ])

    def _r_esc_char_9(self):
        self._h_seq([
            lambda: self._h_str('w'),
            self._r_esc_char_23
        ])

    def _r_esc_char_10(self):
        self._h_seq([self._r_squote_0, self._r_esc_char_24])

    def _r_esc_char_11(self):
        self._h_seq([self._r_dquote_0, self._r_esc_char_25])

    def _r_esc_char_12(self):
        self._h_seq([self._r_bslash_0, self._r_esc_char_26])

    def _r_esc_char_13(self):
        self._h_scope('_r_esc_char_13', [
            self._r_esc_char_27,
            self._r_esc_char_28
        ])

    def _r_esc_char_14(self):
        self._h_scope('_r_esc_char_14', [
            self._r_esc_char_29,
            self._r_esc_char_30
        ])

    def _r_esc_char_15(self):
        self._h_succeed('\b')

    def _r_esc_char_16(self):
        self._h_succeed('\\d')

    def _r_esc_char_17(self):
        self._h_succeed('\f')

    def _r_esc_char_18(self):
        self._h_succeed('\n')

    def _r_esc_char_19(self):
        self._h_succeed('\r')

    def _r_esc_char_20(self):
        self._h_succeed('\\s')

    def _r_esc_char_21(self):
        self._h_succeed('\t')

    def _r_esc_char_22(self):
        self._h_succeed('\v')

    def _r_esc_char_23(self):
        self._h_succeed('\\w')

    def _r_esc_char_24(self):
        self._h_succeed("'")

    def _r_esc_char_25(self):
        self._h_succeed('"')

    def _r_esc_char_26(self):
        self._h_succeed('\\')

    def _r_esc_char_27(self):
        self._h_bind(self._r_hex_esc_0, '_1')

    def _r_esc_char_28(self):
        self._h_succeed(self._h_get('_1'))

    def _r_esc_char_29(self):
        self._h_bind(self._r_unicode_esc_0, '_1')

    def _r_esc_char_30(self):
        self._h_succeed(self._h_get('_1'))

    def _r_expr_0(self):
        self._h_choice([self._r_expr_1, self._r_post_expr_0])

    def _r_expr_1(self):
        self._h_scope('_r_expr_1', [
            self._r_expr_2,
            lambda: self._h_str(':'),
            self._r_expr_3,
            self._r_expr_4
        ])

    def _r_expr_2(self):
        self._h_bind(self._r_post_expr_0, '_1')

    def _r_expr_3(self):
        self._h_bind(self._r_ident_0, '_3')

    def _r_expr_4(self):
        self._h_succeed(['label', self._h_get('_1'), self._h_get('_3')])

    def _r_grammar_0(self):
        self._h_scope('_r_grammar_0', [
            self._r_grammar_1,
            self._r_sp_0,
            self._r_end_0,
            self._r_grammar_2
        ])

    def _r_grammar_1(self):
        self._h_bind(self._r_grammar_3, '_1')

    def _r_grammar_2(self):
        self._h_succeed(['rules', self._h_get('_1')])

    def _r_grammar_3(self):
        return self._h_star(self._r_grammar_4)

    def _r_grammar_4(self):
        self._h_paren(self._r_grammar_5)

    def _r_grammar_5(self):
        self._h_seq([self._r_sp_0, self._r_rule_0])

    def _r_hex_0(self):
        self._h_choice([
            self._r_digit_0,
            self._r_hex_1,
            self._r_hex_2
        ])

    def _r_hex_1(self):
        self._h_range('a', 'f')

    def _r_hex_2(self):
        self._h_range('A', 'F')

    def _r_hex_esc_0(self):
        self._h_scope('_r_hex_esc_0', [
            lambda: self._h_str('x'),
            self._r_hex_esc_1,
            self._r_hex_esc_2
        ])

    def _r_hex_esc_1(self):
        self._h_bind(self._r_hex_esc_3, '_2')

    def _r_hex_esc_2(self):
        self._h_succeed(self._fn_xtou(self._h_get('_2')))

    def _r_hex_esc_3(self):
        self._h_capture(self._r_hex_esc_4)

    def _r_hex_esc_4(self):
        self._h_seq([self._r_hex_0, self._r_hex_0])

    def _r_id_continue_0(self):
        self._h_choice([self._r_id_start_0, self._r_digit_0])

    def _r_id_start_0(self):
        self._h_choice([
            self._r_id_start_1,
            self._r_id_start_2,
            lambda: self._h_str('_')
        ])

    def _r_id_start_1(self):
        self._h_range('a', 'z')

    def _r_id_start_2(self):
        self._h_range('A', 'Z')

    def _r_ident_0(self):
        self._h_capture(self._r_ident_1)

    def _r_ident_1(self):
        self._h_seq([self._r_id_start_0, self._r_ident_2])

    def _r_ident_2(self):
        return self._h_star(self._r_ident_3)

    def _r_ident_3(self):
        self._r_id_continue_0()

    def _r_lit_0(self):
        self._h_choice([self._r_lit_1, self._r_lit_2])

    def _r_lit_1(self):
        self._h_scope('_r_lit_1', [
            self._r_squote_0,
            self._r_lit_3,
            self._r_squote_0,
            self._r_lit_4
        ])

    def _r_lit_2(self):
        self._h_scope('_r_lit_2', [
            self._r_dquote_0,
            self._r_lit_5,
            self._r_dquote_0,
            self._r_lit_6
        ])

    def _r_lit_3(self):
        self._h_bind(self._r_lit_7, '_2')

    def _r_lit_4(self):
        self._h_succeed(['lit', self._fn_cat(self._h_get('_2'))])

    def _r_lit_5(self):
        self._h_bind(self._r_lit_8, '_2')

    def _r_lit_6(self):
        self._h_succeed(['lit', self._fn_cat(self._h_get('_2'))])

    def _r_lit_7(self):
        return self._h_star(self._r_lit_9)

    def _r_lit_8(self):
        return self._h_star(self._r_lit_10)

    def _r_lit_9(self):
        self._r_sqchar_0()

    def _r_lit_10(self):
        self._r_dqchar_0()

    def _r_ll_expr_0(self):
        self._h_choice([self._r_ll_expr_1, self._r_ll_qual_0])

    def _r_ll_expr_1(self):
        self._h_scope('_r_ll_expr_1', [
            self._r_ll_expr_2,
            self._r_sp_0,
            lambda: self._h_str('+'),
            self._r_sp_0,
            self._r_ll_expr_3,
            self._r_ll_expr_4
        ])

    def _r_ll_expr_2(self):
        self._h_bind(self._r_ll_qual_0, '_1')

    def _r_ll_expr_3(self):
        self._h_bind(self._r_ll_expr_0, '_5')

    def _r_ll_expr_4(self):
        self._h_succeed(['ll_plus', self._h_get('_1'), self._h_get('_5')])

    def _r_ll_exprs_0(self):
        self._h_choice([self._r_ll_exprs_1, self._r_ll_exprs_2])

    def _r_ll_exprs_1(self):
        self._h_scope('_r_ll_exprs_1', [
            self._r_ll_exprs_3,
            self._r_ll_exprs_4,
            self._r_ll_exprs_5
        ])

    def _r_ll_exprs_2(self):
        self._h_succeed([])

    def _r_ll_exprs_3(self):
        self._h_bind(self._r_ll_expr_0, '_1')

    def _r_ll_exprs_4(self):
        self._h_bind(self._r_ll_exprs_6, '_2')

    def _r_ll_exprs_5(self):
        self._h_succeed([self._h_get('_1')] + self._h_get('_2'))

    def _r_ll_exprs_6(self):
        return self._h_star(self._r_ll_exprs_7)

    def _r_ll_exprs_7(self):
        self._h_paren(self._r_ll_exprs_8)

    def _r_ll_exprs_8(self):
        self._h_seq([
            self._r_sp_0,
            lambda: self._h_str(','),
            self._r_sp_0,
            self._r_ll_expr_0
        ])

    def _r_ll_post_op_0(self):
        self._h_choice([
            self._r_ll_post_op_1,
            self._r_ll_post_op_2
        ])

    def _r_ll_post_op_1(self):
        self._h_scope('_r_ll_post_op_1', [
            lambda: self._h_str('['),
            self._r_sp_0,
            self._r_ll_post_op_3,
            self._r_sp_0,
            lambda: self._h_str(']'),
            self._r_ll_post_op_4
        ])

    def _r_ll_post_op_2(self):
        self._h_scope('_r_ll_post_op_2', [
            lambda: self._h_str('('),
            self._r_sp_0,
            self._r_ll_post_op_5,
            self._r_sp_0,
            lambda: self._h_str(')'),
            self._r_ll_post_op_6
        ])

    def _r_ll_post_op_3(self):
        self._h_bind(self._r_ll_expr_0, '_3')

    def _r_ll_post_op_4(self):
        self._h_succeed(['ll_getitem', self._h_get('_3')])

    def _r_ll_post_op_5(self):
        self._h_bind(self._r_ll_exprs_0, '_3')

    def _r_ll_post_op_6(self):
        self._h_succeed(['ll_call', self._h_get('_3')])

    def _r_ll_prim_0(self):
        self._h_choice([
            self._r_ll_prim_1,
            self._r_ll_prim_2,
            self._r_ll_prim_3,
            self._r_ll_prim_4,
            self._r_ll_prim_5,
            self._r_ll_prim_6
        ])

    def _r_ll_prim_1(self):
        self._h_scope('_r_ll_prim_1', [
            self._r_ll_prim_7,
            self._r_ll_prim_8
        ])

    def _r_ll_prim_2(self):
        self._h_scope('_r_ll_prim_2', [
            lambda: self._h_str('0x'),
            self._r_ll_prim_9,
            self._r_ll_prim_10
        ])

    def _r_ll_prim_3(self):
        self._h_scope('_r_ll_prim_3', [
            self._r_ll_prim_11,
            self._r_ll_prim_12
        ])

    def _r_ll_prim_4(self):
        self._h_scope('_r_ll_prim_4', [
            self._r_ll_prim_13,
            self._r_ll_prim_14
        ])

    def _r_ll_prim_5(self):
        self._h_scope('_r_ll_prim_5', [
            lambda: self._h_str('('),
            self._r_sp_0,
            self._r_ll_prim_15,
            self._r_sp_0,
            lambda: self._h_str(')'),
            self._r_ll_prim_16
        ])

    def _r_ll_prim_6(self):
        self._h_scope('_r_ll_prim_6', [
            lambda: self._h_str('['),
            self._r_sp_0,
            self._r_ll_prim_17,
            self._r_sp_0,
            lambda: self._h_str(']'),
            self._r_ll_prim_18
        ])

    def _r_ll_prim_7(self):
        self._h_bind(self._r_ident_0, '_1')

    def _r_ll_prim_8(self):
        self._h_succeed(['ll_var', self._h_get('_1')])

    def _r_ll_prim_9(self):
        self._h_bind(self._r_ll_prim_19, '_2')

    def _r_ll_prim_10(self):
        self._h_succeed(['ll_hex', self._fn_cat(self._h_get('_2'))])

    def _r_ll_prim_11(self):
        self._h_bind(self._r_ll_prim_20, '_1')

    def _r_ll_prim_12(self):
        self._h_succeed(['ll_dec', self._fn_cat(self._h_get('_1'))])

    def _r_ll_prim_13(self):
        self._h_bind(self._r_lit_0, '_1')

    def _r_ll_prim_14(self):
        self._h_succeed(['ll_str', self._h_get('_1')[1]])

    def _r_ll_prim_15(self):
        self._h_bind(self._r_ll_expr_0, '_3')

    def _r_ll_prim_16(self):
        self._h_succeed(['ll_paren', self._h_get('_3')])

    def _r_ll_prim_17(self):
        self._h_bind(self._r_ll_exprs_0, '_3')

    def _r_ll_prim_18(self):
        self._h_succeed(['ll_arr', self._h_get('_3')])

    def _r_ll_prim_19(self):
        return self._h_plus(self._r_ll_prim_21)

    def _r_ll_prim_20(self):
        return self._h_plus(self._r_ll_prim_22)

    def _r_ll_prim_21(self):
        self._r_hex_0()

    def _r_ll_prim_22(self):
        self._r_digit_0()

    def _r_ll_qual_0(self):
        self._h_choice([self._r_ll_qual_1, self._r_ll_prim_0])

    def _r_ll_qual_1(self):
        self._h_scope('_r_ll_qual_1', [
            self._r_ll_qual_2,
            self._r_ll_qual_3,
            self._r_ll_qual_4
        ])

    def _r_ll_qual_2(self):
        self._h_bind(self._r_ll_prim_0, '_1')

    def _r_ll_qual_3(self):
        self._h_bind(self._r_ll_qual_5, '_2')

    def _r_ll_qual_4(self):
        self._h_succeed(['ll_qual', self._h_get('_1'), self._h_get('_2')])

    def _r_ll_qual_5(self):
        return self._h_plus(self._r_ll_qual_6)

    def _r_ll_qual_6(self):
        self._r_ll_post_op_0()

    def _r_post_expr_0(self):
        self._h_choice([self._r_post_expr_1, self._r_post_expr_2])

    def _r_post_expr_1(self):
        self._h_scope('_r_post_expr_1', [
            self._r_post_expr_3,
            self._r_post_expr_4,
            self._r_post_expr_5
        ])

    def _r_post_expr_2(self):
        self._h_scope('_r_post_expr_2', [
            self._r_post_expr_6,
            self._r_post_expr_7
        ])

    def _r_post_expr_3(self):
        self._h_bind(self._r_prim_expr_0, '_1')

    def _r_post_expr_4(self):
        self._h_bind(self._r_post_op_0, '_2')

    def _r_post_expr_5(self):
        self._h_succeed([self._h_get('_2'), self._h_get('_1')])

    def _r_post_expr_6(self):
        self._h_bind(self._r_prim_expr_0, '_1')

    def _r_post_expr_7(self):
        self._h_succeed(self._h_get('_1'))

    def _r_post_op_0(self):
        self._h_choice([
            self._r_post_op_1,
            self._r_post_op_2,
            self._r_post_op_3
        ])

    def _r_post_op_1(self):
        self._h_seq([
            lambda: self._h_str('?'),
            self._r_post_op_4
        ])

    def _r_post_op_2(self):
        self._h_seq([
            lambda: self._h_str('*'),
            self._r_post_op_5
        ])

    def _r_post_op_3(self):
        self._h_seq([
            lambda: self._h_str('+'),
            self._r_post_op_6
        ])

    def _r_post_op_4(self):
        self._h_succeed('opt')

    def _r_post_op_5(self):
        self._h_succeed('star')

    def _r_post_op_6(self):
        self._h_succeed('plus')

    def _r_prim_expr_0(self):
        self._h_choice([
            self._r_prim_expr_1,
            self._r_prim_expr_2,
            self._r_prim_expr_3,
            self._r_prim_expr_4,
            self._r_prim_expr_5,
            self._r_prim_expr_6,
            self._r_prim_expr_7,
            self._r_prim_expr_8,
            self._r_prim_expr_9,
            self._r_prim_expr_10
        ])

    def _r_prim_expr_1(self):
        self._h_scope('_r_prim_expr_1', [
            self._r_prim_expr_11,
            self._r_sp_0,
            lambda: self._h_str('..'),
            self._r_sp_0,
            self._r_prim_expr_12,
            self._r_prim_expr_13
        ])

    def _r_prim_expr_2(self):
        self._h_scope('_r_prim_expr_2', [
            self._r_prim_expr_14,
            self._r_prim_expr_15
        ])

    def _r_prim_expr_3(self):
        self._h_scope('_r_prim_expr_3', [
            self._r_prim_expr_16,
            self._r_prim_expr_17,
            self._r_prim_expr_18
        ])

    def _r_prim_expr_4(self):
        self._h_scope('_r_prim_expr_4', [
            lambda: self._h_str('('),
            self._r_sp_0,
            self._r_prim_expr_19,
            self._r_sp_0,
            lambda: self._h_str(')'),
            self._r_prim_expr_20
        ])

    def _r_prim_expr_5(self):
        self._h_scope('_r_prim_expr_5', [
            lambda: self._h_str('~'),
            self._r_prim_expr_21,
            self._r_prim_expr_22
        ])

    def _r_prim_expr_6(self):
        self._h_scope('_r_prim_expr_6', [
            lambda: self._h_str('->'),
            self._r_sp_0,
            self._r_prim_expr_23,
            self._r_prim_expr_24
        ])

    def _r_prim_expr_7(self):
        self._h_seq([
            lambda: self._h_str('{}'),
            self._r_prim_expr_25
        ])

    def _r_prim_expr_8(self):
        self._h_scope('_r_prim_expr_8', [
            lambda: self._h_str('{'),
            self._r_sp_0,
            self._r_prim_expr_26,
            self._r_sp_0,
            lambda: self._h_str('}'),
            self._r_prim_expr_27
        ])

    def _r_prim_expr_9(self):
        self._h_scope('_r_prim_expr_9', [
            lambda: self._h_str('={'),
            self._r_sp_0,
            self._r_prim_expr_28,
            self._r_sp_0,
            lambda: self._h_str('}'),
            self._r_prim_expr_29
        ])

    def _r_prim_expr_10(self):
        self._h_scope('_r_prim_expr_10', [
            lambda: self._h_str('?{'),
            self._r_sp_0,
            self._r_prim_expr_30,
            self._r_sp_0,
            lambda: self._h_str('}'),
            self._r_prim_expr_31
        ])

    def _r_prim_expr_11(self):
        self._h_bind(self._r_lit_0, '_1')

    def _r_prim_expr_12(self):
        self._h_bind(self._r_lit_0, '_5')

    def _r_prim_expr_13(self):
        self._h_succeed(['range', self._h_get('_1'), self._h_get('_5')])

    def _r_prim_expr_14(self):
        self._h_bind(self._r_lit_0, '_1')

    def _r_prim_expr_15(self):
        self._h_succeed(self._h_get('_1'))

    def _r_prim_expr_16(self):
        self._h_bind(self._r_ident_0, '_1')

    def _r_prim_expr_17(self):
        self._h_not(self._r_prim_expr_32)

    def _r_prim_expr_18(self):
        self._h_succeed(['apply', self._h_get('_1')])

    def _r_prim_expr_19(self):
        self._h_bind(self._r_choice_0, '_3')

    def _r_prim_expr_20(self):
        self._h_succeed(['paren', self._h_get('_3')])

    def _r_prim_expr_21(self):
        self._h_bind(self._r_prim_expr_0, '_2')

    def _r_prim_expr_22(self):
        self._h_succeed(['not', self._h_get('_2')])

    def _r_prim_expr_23(self):
        self._h_bind(self._r_ll_expr_0, '_3')

    def _r_prim_expr_24(self):
        self._h_succeed(['action', self._h_get('_3')])

    def _r_prim_expr_25(self):
        self._h_succeed(['pos'])

    def _r_prim_expr_26(self):
        self._h_bind(self._r_choice_0, '_3')

    def _r_prim_expr_27(self):
        self._h_succeed(['capture', self._h_get('_3')])

    def _r_prim_expr_28(self):
        self._h_bind(self._r_ll_expr_0, '_3')

    def _r_prim_expr_29(self):
        self._h_succeed(['eq', self._h_get('_3')])

    def _r_prim_expr_30(self):
        self._h_bind(self._r_ll_expr_0, '_3')

    def _r_prim_expr_31(self):
        self._h_succeed(['pred', self._h_get('_3')])

    def _r_prim_expr_32(self):
        self._h_paren(self._r_prim_expr_33)

    def _r_prim_expr_33(self):
        self._h_seq([self._r_sp_0, lambda: self._h_str('=')])

    def _r_rule_0(self):
        self._h_scope('_r_rule_0', [
            self._r_rule_1,
            self._r_sp_0,
            lambda: self._h_str('='),
            self._r_sp_0,
            self._r_rule_2,
            self._r_sp_0,
            self._r_rule_3,
            self._r_rule_4
        ])

    def _r_rule_1(self):
        self._h_bind(self._r_ident_0, '_1')

    def _r_rule_2(self):
        self._h_bind(self._r_choice_0, '_5')

    def _r_rule_3(self):
        return self._h_opt(self._r_rule_5)

    def _r_rule_4(self):
        self._h_succeed(['rule', self._h_get('_1'), self._h_get('_5')])

    def _r_rule_5(self):
        self._h_str(',')

    def _r_seq_0(self):
        self._h_choice([self._r_seq_1, self._r_seq_2])

    def _r_seq_1(self):
        self._h_scope('_r_seq_1', [
            self._r_seq_3,
            self._r_seq_4,
            self._r_seq_5
        ])

    def _r_seq_2(self):
        self._h_succeed(['empty'])

    def _r_seq_3(self):
        self._h_bind(self._r_expr_0, '_1')

    def _r_seq_4(self):
        self._h_bind(self._r_seq_6, '_2')

    def _r_seq_5(self):
        self._h_succeed(['seq', [self._h_get('_1')] + self._h_get('_2')])

    def _r_seq_6(self):
        return self._h_star(self._r_seq_7)

    def _r_seq_7(self):
        self._h_paren(self._r_seq_8)

    def _r_seq_8(self):
        self._h_seq([
            self._r_ws_0,
            self._r_sp_0,
            self._r_expr_0
        ])

    def _r_sp_0(self):
        return self._h_star(self._r_sp_1)

    def _r_sp_1(self):
        self._r_ws_0()

    def _r_sqchar_0(self):
        self._h_choice([self._r_sqchar_1, self._r_sqchar_2])

    def _r_sqchar_1(self):
        self._h_scope('_r_sqchar_1', [
            self._r_bslash_0,
            self._r_sqchar_3,
            self._r_sqchar_4
        ])

    def _r_sqchar_2(self):
        self._h_scope('_r_sqchar_2', [
            self._r_sqchar_5,
            self._r_sqchar_6,
            self._r_sqchar_7
        ])

    def _r_sqchar_3(self):
        self._h_bind(self._r_esc_char_0, '_2')

    def _r_sqchar_4(self):
        self._h_succeed(self._h_get('_2'))

    def _r_sqchar_5(self):
        self._h_not(self._r_sqchar_8)

    def _r_sqchar_6(self):
        self._h_bind(self._r_anything_0, '_2')

    def _r_sqchar_7(self):
        self._h_succeed(self._h_get('_2'))

    def _r_sqchar_8(self):
        self._r_squote_0()

    def _r_squote_0(self):
        self._h_str("'")

    def _r_unicode_esc_0(self):
        self._h_choice([
            self._r_unicode_esc_1,
            self._r_unicode_esc_2
        ])

    def _r_unicode_esc_1(self):
        self._h_scope('_r_unicode_esc_1', [
            lambda: self._h_str('u'),
            self._r_unicode_esc_3,
            self._r_unicode_esc_4
        ])

    def _r_unicode_esc_2(self):
        self._h_scope('_r_unicode_esc_2', [
            lambda: self._h_str('U'),
            self._r_unicode_esc_5,
            self._r_unicode_esc_6
        ])

    def _r_unicode_esc_3(self):
        self._h_bind(self._r_unicode_esc_7, '_2')

    def _r_unicode_esc_4(self):
        self._h_succeed(self._fn_xtou(self._h_get('_2')))

    def _r_unicode_esc_5(self):
        self._h_bind(self._r_unicode_esc_8, '_2')

    def _r_unicode_esc_6(self):
        self._h_succeed(self._fn_xtou(self._h_get('_2')))

    def _r_unicode_esc_7(self):
        self._h_capture(self._r_unicode_esc_9)

    def _r_unicode_esc_8(self):
        self._h_capture(self._r_unicode_esc_10)

    def _r_unicode_esc_9(self):
        self._h_seq([
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0
        ])

    def _r_unicode_esc_10(self):
        self._h_seq([
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0,
            self._r_hex_0
        ])

    def _r_ws_0(self):
        self._h_choice([
            lambda: self._h_str(' '),
            lambda: self._h_str('\t'),
            self._r_eol_0,
            self._r_comment_0
        ])

    def _fn_cat(self, vals):
        return ''.join(vals)

    def _fn_is_unicat(self, var, cat):
        import unicodedata
        return unicodedata.category(var) == cat

    def _fn_itou(self, n):
        return chr(n)

    def _fn_join(self, var, val):
        return var.join(val)

    def _fn_number(self, var):
        return float(var) if ('.' in var or 'e' in var) else int(var)

    def _fn_xtoi(self, s):
        return int(s, base=16)

    def _fn_xtou(self, s):
        return chr(int(s, base=16))

    def _h_bind(self, rule, var):
        rule()
        if not self.failed:
            self._h_set(var, self.val)

    def _h_capture(self, rule):
        start = self.pos
        rule()
        if not self.failed:
            self._h_succeed(self.msg[start:self.pos], self.pos)

    def _h_ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._h_succeed(ch, p+1)
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

    def _h_eq(self, var):
        self._h_str(var)

    def _h_err(self):
        lineno = 1
        colno = 1
        for ch in self.msg[:self.errpos]:
            if ch == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = repr(self.msg[self.errpos]).replace(
               "'", "\"")
        err_str = '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)
        return None, err_str, self.errpos

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_get(self, var):
        return self._scopes[-1][1][var]

    def _h_leftrec(self, rule, rule_name):
        pos = self.pos
        key = (rule_name, pos)
        seed = self._seeds.get(key)
        if seed:
            self.val, self.failed, self.pos = seed
            return
        if rule_name in self._blocked:
            self._h_fail()
        current = (None, True, self.pos)
        self._seeds[key] = current
        self._blocked.add(rule_name)
        while True:
            rule()
            if self.pos > current[2]:
                current = (self.val, self.failed, self.pos)
                self._seeds[key] = current
                self.pos = pos
            else:
                del self._seeds[key]
                self._seeds.pop(rule_name, pos)
                if rule_name in self._blocked:
                    self._blocked.remove(rule_name)
                self.val, self.failed, self.pos = current
                return

    def _h_memo(self, rule, rule_name):
        r = self._cache.get((rule_name, self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        rule()
        self._cache[(rule_name, pos)] = (self.val, self.failed,
                                         self.pos)

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

    def _h_pos(self):
        self._h_succeed(self.pos)

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, name, rules):
        self._scopes.append([name, {}])
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
        self._scopes[-1][1][var] = val

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
