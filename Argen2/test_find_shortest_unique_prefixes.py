# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-09-28.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
from find_shortest_unique_prefixes import find_shortest_unique_prefixes


def t(s):
    return s, s


def test_case_sensitive():
    strings = [t("-foo"), t("-fuu")]
    prefixes = find_shortest_unique_prefixes(strings)
    assert len(prefixes) == 2
    assert prefixes[0] == ("-fo", "o", "-foo")
    assert prefixes[1] == ("-fu", "u", "-fuu")


def test_more():
    strings = [t("-foo"), t("--fuu"), t("/pop")]
    prefixes = find_shortest_unique_prefixes(strings)
    assert len(prefixes) == 3
    assert prefixes[0] == ("-f", "oo", "-foo")
    assert prefixes[1] == ("--", "fuu", "--fuu")
    assert prefixes[2] == ("/", "pop", "/pop")


def test_single_string():
    strings = [t("-foo")]
    prefixes = find_shortest_unique_prefixes(strings)
    assert len(prefixes) == 1
    assert prefixes[0] == ("-", "foo", "-foo")


def test_case_insensitive():
    strings = [t("-foo"), t("-FUU")]
    prefixes = find_shortest_unique_prefixes(strings, True)
    assert len(prefixes) == 2
    assert prefixes[0] == ("-fo", "o", "-foo")
    assert prefixes[1] == ("-FU", "U", "-FUU")
