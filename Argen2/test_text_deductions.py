# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argument
import text_deductions as td


def test_find_commas():
    assert td.find_commas("-a M,N, -b") == [6]
    assert td.find_commas("-a M,N,-b") == [6]


def test_split_argument_text():
    assert td.split_arguments("-a N, --abra N") == [("-a", "N"), ("--abra", "N")]
    assert td.split_arguments("-a N, --abra=N") == [("-a", "N"), ("--abra", "N")]
    assert td.split_arguments("-a, --abra N") == [("-a", None), ("--abra", "N")]
    assert td.split_arguments("-a N --abra=N") == [("-a", "N"), ("--abra", "N")]
    assert td.split_arguments("-a N --abra N") == [("-a", "N"), ("--abra", "N")]
    assert td.split_arguments("-a --abra N") == [("-a", None), ("--abra", "N")]
    assert td.split_arguments("-a X,Y,Z --abra=X,Y,Z") == [("-a", "X,Y,Z"), ("--abra", "X,Y,Z")]
    assert td.split_arguments("/a X,Y,Z,/abra=X,Y,Z") == [("/a", "X,Y,Z"), ("/abra", "X,Y,Z")]
    assert td.split_arguments("-=, --=N") == [("-=", None), ("--=N", None)]
    assert td.split_arguments("-=, --foo= B") == [("-=", None), ("--foo=", "B")]


def test_parse_flags():
    props = td.parse_flags("-r MIN-MAX --range=MIN-MAX")
    assert props["flags"] == "-r --range"
    assert props["meta_variable"] == "MIN-MAX"


def test_get_argument_metavar_and_count():
    f = td.get_argument_metavar_and_count
    assert f("<file>") == ("file", "1")
    assert f("[file]") == ("file", "0")
    assert f("[file ...]") == ("file", "0...")
    assert f("[file]...") == ("file", "0...")
    assert f("<file> ...") == ("file", "1...")
    assert f("file ...") == ("file", "1...")
    assert f("Xx,Yy,Z...") == ("Xx,Yy,Z...", "1")


def test_parse_argument_text():
    arg = argument.Argument("-")
    props = td.parse_argument_text(arg)
    assert props["flags"] == "-"
