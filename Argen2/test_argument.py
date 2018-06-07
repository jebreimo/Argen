# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argument as a
import pytest


# def test_determine_metavar_type():
#     f = lambda s: a.determine_metavar_type(
#                     s.split(),
#                     p.DEFAULT_METAVAR_TYPES)
#     assert f("FLOAT") == "double"
#     assert f("NUM1 NUM2") == "int"
#     assert f("HEX1 HEX2") == "int"
#     assert f("NUMBER FILE") == "std::string"
#
#
# def test_parse_metavar_numbers_and_ellipsis():
#     props = a.parse_metavar("NUM1:NUM2...")
#     assert props["separator"] == ":"
#     assert props["type"] == "int"
#     assert props["separator_count"] == "0..."
#     assert props["meta_variable"] == "NUM1:NUM2..."
#
#
# def test_parse_metavar_three_files():
#     props = a.parse_metavar("FILE1+FILE2+FILE3")
#     assert props["separator"] == "+"
#     assert props["type"] == "std::string"
#     assert props["separator_count"] == "2"
#     assert props["meta_variable"] == "FILE1+FILE2+FILE3"


def test_get_int_range():
    assert a.get_int_range("1") == (1, 1)
    assert a.get_int_range("..1") == (0, 1)
    assert a.get_int_range("34..") == (34, None)
    assert a.get_int_range("3..8") == (3, 8)
    assert a.get_int_range("3...8") == (3, 8)
    assert a.get_int_range("-3..8") == (-3, 8)
    assert a.get_int_range("13..8") == (13, 8)
    assert a.get_int_range("..") == (0, None)
    assert a.get_int_range("0x1a") == (0x1A, 0x1A)
    with pytest.raises(ValueError):
        a.get_int_range("1e")


def test_parse_valid_values():
    vals = a.parse_valid_values('1..10:A::B():"A,B", "A::B"')
    assert len(vals) == 3
    assert vals[0] == [("1", "10")]
    assert vals[1] == [("A::B()", "A::B()")]
    assert vals[2] == [('"A,B"', '"A,B"'), ('"A::B"', '"A::B"')]
