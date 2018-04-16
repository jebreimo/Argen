# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argument as a


def test_find_metavar_separator():
    assert a.find_metavar_separator("nxn") is None
    assert a.find_metavar_separator("ABC") is None
    assert a.find_metavar_separator("NxN") == "x"
    assert a.find_metavar_separator("Ax:Bx:Cx") == ":"
    assert a.find_metavar_separator("AB+") is None
    assert a.find_metavar_separator("AB+CD") == "+"
    assert a.find_metavar_separator("AB+CD...") == "+"
    assert a.find_metavar_separator("AB+CD+...") == "+"
    assert a.find_metavar_separator("AB+...") == "+"


def test_determine_metavar_type():
    f = lambda s: a.determine_metavar_type(
                    s.split(),
                    a.DEFAULT_METAVAR_TYPES)
    assert f("FLOAT") == "double"
    assert f("NUM1 NUM2") == "int"
    assert f("HEX1 HEX2") == "int"
    assert f("NUMBER FILE") == "std::string"


def test_parse_metavar_numbers_and_ellipsis():
    props = a.parse_metavar("NUM1:NUM2...")
    assert props["separator"] == ":"
    assert props["type"] == "int"
    assert props["separator_count"] == "0..."
    assert props["meta_variable"] == "NUM1:NUM2..."


def test_parse_metavar_three_files():
    props = a.parse_metavar("FILE1+FILE2+FILE3")
    assert props["separator"] == "+"
    assert props["type"] == "std::string"
    assert props["separator_count"] == "2"
    assert props["meta_variable"] == "FILE1+FILE2+FILE3"
