# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-23.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parse_help_text as pht
import helpfilesyntax


def test_parse_argument():
    syntax = helpfilesyntax.HelpFileSyntax()
    arg = pht.parse_argument("-t --test | Value: 3 | Count: 2...", syntax)
    assert arg.text == "-t --test "
    assert arg.given_properties["value"] == "3"
    assert arg.given_properties["count"] == "2..."


def test_parse_argument_quotes():
    syntax = helpfilesyntax.HelpFileSyntax()
    arg = pht.parse_argument("-t --test | Value: \"3 | 4\" | Count: 2...", syntax)
    assert arg.text == "-t --test "
    assert arg.given_properties["value"] == '"3 | 4"'
    assert arg.given_properties["count"] == "2..."


def test_parse_complex():
    syntax = helpfilesyntax.HelpFileSyntax()
    arg = pht.parse_argument("-t --test | Value: {Foo(a | b), Bar(c | d)} | Count: 2...", syntax)
    assert arg.text == "-t --test "
    assert arg.given_properties["value"] == "{Foo(a | b), Bar(c | d)}"
    assert arg.given_properties["count"] == "2..."


def test_find_argument():
    syntax = helpfilesyntax.HelpFileSyntax()
    assert pht.find_argument("..{{ abcd }}", 0, syntax) == (2, 12)
    assert pht.find_argument("..{{ abcd }} {{ efgh }}", 6, syntax) == (13, 23)
    assert pht.find_argument("..{{-t | Default: {1, {2, 3}} }} g h", 0, syntax) == (2, 32)
