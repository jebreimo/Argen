# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_separator_counts as ds


def test():
    assert ds.count_separators("FILE:FILE:...", ":") == (0, None)
    assert ds.count_separators("FILE:FILE...", ":") == (0, None)
