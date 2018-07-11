# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-29.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import name_tools
import argument


def test_make_member_name():
    assert name_tools.make_name("_test") == "_test"
    assert name_tools.make_name("+test") == "test"
    assert name_tools.make_name("test_") == "test_"
    assert name_tools.make_name("test+=") == "test"
    assert name_tools.make_name("123test") == "_123test"
    assert name_tools.make_name("12+t-p_s**2") == "_12_t_p_s_2"
    assert name_tools.make_name("t_$_t") == "t_t"
    assert name_tools.make_name("foo faa") == "foo_faa"
    assert name_tools.make_name("--") == "_"


def test_get_longest_flags():
    assert name_tools.get_longest_flag(["-a", "--="]) == "-a"
    assert name_tools.get_longest_flag(["-z"]) == "-z"


# def test_deduce_member_name():
#     s = {"foo", "foo_1"}
#     a = argument.Argument("", dict(flags="--foo"))
#     assert mnd.deduce_member_name(a, s) == "foo"
#
#
# def test_deduce_member_name_2():
#     s = set()
#     a = argument.Argument("", dict(flags="-f"))
#     assert mnd.deduce_member_name(a, s) == "f"
#     assert "f" in s
#
#
# def test_deduce_member_name_3():
#     s = set()
#     a = argument.Argument("", dict(flags="-"))
#     assert mnd.deduce_member_name(a, s) == "unnamed"
#     assert "unnamed" in s
#
#
# def test_deduce_member_name_4():
#     s = {"foo", "foo_1"}
#     a = argument.Argument("", dict(meta_variable="foo"))
#     assert mnd.deduce_member_name(a, s) == "foo_2"
#     assert "foo_2" in s
