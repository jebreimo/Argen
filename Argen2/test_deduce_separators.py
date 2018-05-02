# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_separators as ds


def test_find_metavar_separator():
    assert ds.find_metavar_separator("nxn") is None
    assert ds.find_metavar_separator("ABC") is None
    assert ds.find_metavar_separator("NxN") == "x"
    assert ds.find_metavar_separator("Ax:Bx:Cx") == ":"
    assert ds.find_metavar_separator("AB+") is None
    assert ds.find_metavar_separator("AB+CD") == "+"
    assert ds.find_metavar_separator("AB+CD...") == "+"
    assert ds.find_metavar_separator("AB+CD+...") == "+"
    assert ds.find_metavar_separator("AB+...") == "+"
