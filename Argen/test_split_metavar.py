# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-17.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import split_metavar as sm


def test_tokenize_metavar():
    assert sm.tokenize_metavar("[FILE...]") == ["[", "FILE", "...", "]"]
    assert sm.tokenize_metavar("[FILE] ...") == ["[", "FILE", "]", " ", "..."]
    assert sm.tokenize_metavar("FILE .. FILE") \
           == ["FILE", " ", "..", " ", "FILE"]
    assert sm.tokenize_metavar("<file name[.png]>") \
           == ["<", "file", " ", "name", "[", ".png", "]", ">"]


def test_normalize_metavar():
    assert sm.split_metavar("[FILE ..]") == ["[FILE]", "..."]
    assert sm.split_metavar("[FILE:...:FILE ...]") == ["[FILE:...:FILE]", "..."]
    assert sm.split_metavar("A file...") == ["A file..."]
    assert sm.split_metavar("[File name[.jpg]]") == ["[File name[.jpg]]"]
    assert sm.split_metavar("<File name[.jpg]>") == ["<File name[.jpg]>"]
    assert sm.split_metavar("First point ... Last point") \
           == ["First point", "...", "Last point"]
    assert sm.split_metavar("File name [.jpg]") == ["File name [.jpg]"]
    assert sm.split_metavar("[FILE ..>") == ["[FILE ..>"]
    assert sm.split_metavar("FILE:FILE:.. ... ") == ["FILE:FILE:..", "..."]
    assert sm.split_metavar("<x,y> ... <x,y>") == ["<x,y>", "...", "<x,y>"]
