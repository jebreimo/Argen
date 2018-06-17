# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-18.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argument as a
import deduce_indices as di
import session


def test_ordering():
    args = [a.Argument("a"),
            a.Argument("b"),
            a.Argument("c"),
            a.Argument("d")]
    args[0].index = 2
    args[3].index = 0
    s = session.Session()
    s.arguments = args
    di.deduce_indices(s)
    assert args[0].index == 2
    assert args[1].index == 1
    assert args[2].index == 3
    assert args[3].index == 0
