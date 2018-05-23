# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-21.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_arguments as da


def test_normalize_argument_metavar():
    assert da.split_metavar("[abc ..]") == ["[abc]", "..."]
    assert da.split_metavar("[abc ...]") == ["[abc]", "..."]
    assert da.split_metavar("first ... last") == ["<first>", "...", "<last>"]
    assert da.split_metavar("file name[.jpg]") == ["<file name[.jpg]>"]
    assert da.split_metavar("first [second ...]") == ["<first>", "[second]", "..."]
    assert da.split_metavar("a first [a second] [a third]") == ["<a first>", "[a second]", "[a third]"]
    assert da.split_metavar("a first [a second] a third") == ["<a first>", "[a second]", "<a third>"]
    assert da.split_metavar("<a first> <a second> [a third]") == ["<a first>", "<a second>", "[a third]"]
    assert da.split_metavar("<a first> [a second] [a third]") == ["<a first>", "[a second]", "[a third]"]
    assert da.split_metavar("<abc ...>") == ["<abc ...>"]
    assert da.split_metavar("[1 ... 2 ...\n 3]") == ["[1 ... 2 ...\n 3]"]
