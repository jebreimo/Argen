# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_separator_counts as ds


def test_tokenize_metavar():
    assert ds.tokenize_metavar("[FILE...]") == ["[", "FILE", "...", "]"]
    assert ds.tokenize_metavar("[FILE] ...") == ["[", "FILE", "]", " ", "..."]
    assert ds.tokenize_metavar("FILE .. FILE") \
           == ["FILE", " ", "..", " ", "FILE"]
    assert ds.tokenize_metavar("<file name[.png]>") \
           == ["<", "file", " ", "name", "[", ".png", "]", ">"]


def test_normalize_metavar():
    assert ds.normalize_metavar("[FILE ..]") == ["[FILE]", "..."]
    assert ds.normalize_metavar("[FILE:...:FILE ...]") \
           == ["[FILE:...:FILE]", "..."]
    assert ds.normalize_metavar("A file...") == ["A file..."]
    assert ds.normalize_metavar("[File name[.jpg]]") == ["[File name[.jpg]]"]
    assert ds.normalize_metavar("<File name[.jpg]>") == ["<File name[.jpg]>"]
    assert ds.normalize_metavar("First point ... Last point") \
           == ["First point", "...", "Last point"]
    assert ds.normalize_metavar("File name [.jpg]") == ["File name [.jpg]"]
    assert ds.normalize_metavar("[FILE ..>") == ["[FILE ..>"]
    assert ds.normalize_metavar("FILE:FILE:.. ... ") == ["FILE:FILE:..", "..."]


def test_count_separators():
    assert ds.count_separators("FILE:FILE:...", ":") == (0, None)
    assert ds.count_separators("FILE:FILE...", ":") == (0, None)
    assert ds.count_separators("[FILE:FILE...]", ":") == (0, None)
    assert ds.count_separators("<X,Y,Z> ...", ",") == (2, 2)
    assert ds.count_separators("<X,Y,Z ...", ",") == (0, None)
    assert ds.count_separators("X,Y,Z ...", ",") == (2, 2)
    assert ds.count_separators("[X,Y,Z ...]", ",") == (2, 2)
