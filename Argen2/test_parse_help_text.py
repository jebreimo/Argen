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
import session


def test_parse_argument():
    s = session.Session()
    txt, props = pht.parse_argument("-t --test | Value: 3 | Count: 2..", s)
    assert txt == "-t --test "
    assert props["value"] == "3"
    assert props["count"] == "2.."


def test_parse_argument_quotes():
    s = session.Session()
    txt, props = pht.parse_argument('-t --test | Value: "3 | 4" | Count: 2..',
                                    s)
    assert txt == "-t --test "
    assert props["value"] == '"3 | 4"'
    assert props["count"] == "2.."


def test_parse_complex():
    s = session.Session()
    txt, props = pht.parse_argument("-t --test "
                                    "| Value: {Foo(a | b), Bar(c | d)} "
                                    "| Count: 2..", s)
    assert txt == "-t --test "
    assert props["value"] == "{Foo(a | b), Bar(c | d)}"
    assert props["count"] == "2.."


def test_find_tokens():
    syntax = helpfilesyntax.HelpFileSyntax()
    it = pht.find_tokens("..{{-t | Default: {1, {2, 3}} }} g\nh", syntax)
    assert next(it) == (pht.TEXT_TOKEN, 0, 2)
    assert next(it) == (pht.ARGUMENT_TOKEN, 2, 32)
    assert next(it) == (pht.TEXT_TOKEN, 32, 35)
    assert next(it) == (pht.TEXT_TOKEN, 35, 36)
