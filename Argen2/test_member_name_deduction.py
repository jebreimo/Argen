# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-29.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import member_name_deduction as mnd
import argument


def test_make_member_name():
    assert mnd.make_member_name("_test") == "_test"
    assert mnd.make_member_name("+test") == "test"
    assert mnd.make_member_name("test_") == "test_"
    assert mnd.make_member_name("test+=") == "test"
    assert mnd.make_member_name("123test") == "_123test"
    assert mnd.make_member_name("12+t-p_s**2") == "_12_t_p_s_2"
    assert mnd.make_member_name("t_$_t") == "t_t"
    assert mnd.make_member_name("foo faa") == "foo_faa"


def test_get_longest_flags():
    assert mnd.get_longest_flag("-a --=") == "-a"
    assert mnd.get_longest_flag("-z") == "-z"


def test_deduce_member_name():
    s = {"foo", "foo_1"}
    a = argument.Argument("", dict(flags="--foo"))
    assert mnd.deduce_member_name(a, s) == "foo_2"
    assert "foo_2" in s


def test_deduce_member_name_2():
    s = set()
    a = argument.Argument("", dict(flags="-f"))
    assert mnd.deduce_member_name(a, s) == "f"
    assert "f" in s


def test_deduce_member_name_3():
    s = set()
    a = argument.Argument("", dict(flags="-"))
    assert mnd.deduce_member_name(a, s) == "unnamed"
    assert "unnamed" in s
