# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-29.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def get_accumulated_count(arguments):
    min_count = max_count = 0
    for arg in arguments:
        count = arg.count
        if not count:
            continue
        if count[0]:
            min_count += count[0]
        if count[1] is None:
            max_count = None
        elif max_count is not None:
            max_count += count[1]
    if min_count != 0 or max_count != 0:
        return min_count, max_count
    else:
        return None
