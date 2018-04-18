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


def test_ordering():
    args = [a.Argument("a", {"index": "2"}),
            a.Argument("b"),
            a.Argument("c"),
            a.Argument("d", {"index": "0"})]
    assert di.deduce_indices(args) == ([args[1], args[2]], None)
    assert args[0].index == 2
    assert args[1].index == 1
    assert args[2].index == 3
    assert args[3].index == 0
