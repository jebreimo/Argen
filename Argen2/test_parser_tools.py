# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-31.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools as pt


def test_find_next_separator():
    assert pt.find_next_separator("aa || bb | c", 0, "|") == 9
    assert pt.find_next_separator('"a | b" | c', 0, "|") == 8


def test_split_text():
    assert pt.split_text("-t | inline: foo = a || b; | name: tool", "|") == ["-t ", " inline: foo = a || b; ", " name: tool"]


def test_split_and_unescape_text():
    assert pt.split_and_unescape_text("-t", "|") == ["-t"]
    assert pt.split_and_unescape_text("-t | inline: foo = a; ", "|") == ["-t ", " inline: foo = a; "]
    assert pt.split_and_unescape_text("-t | inline: foo = a || b; | name: tool", "|") == ["-t ", " inline: foo = a | b; ", " name: tool"]


def test_find_char():
    assert pt.find_char('"Abra \\"kadabra\\"", ', ",", 0) == 18
    assert pt.find_char("'A'", ",", 0) == -1
    assert pt.find_char("'\\u3FA1', 2", ",", 0) == 8
    assert pt.find_char('\n\t 123, ', ",", 0) == 6
    assert pt.find_char('Class(1, 2)("1,3"), 123', ",", 0) == 18
    assert pt.find_char("1, 2, 34, 5", ",", 5) == 8
    assert pt.find_char("It's lovely '-' - p", '-', 0) == 16


def test_find_last_not_of():
    assert pt.find_last_not_of("ABC...", ".") == 2
    assert pt.find_last_not_of("...", ".") == -1
    assert pt.find_last_not_of("", ".") == -1
    assert pt.find_last_not_of(None, ".") == -1
    assert pt.find_last_not_of("ABC", ".") == 2
