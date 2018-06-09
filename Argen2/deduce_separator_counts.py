# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools


def count_separators(text, separator):
    if not separator:
        return 0, 0
    if not text:
        return 0, None
    positions = parser_tools.find_all(text, separator)
    if not positions:
        return 0, None
    final_token_pos = positions[-1] + len(separator)
    if parser_tools.is_ellipsis(text[final_token_pos:]):
        return len(positions), None
    return len(positions), len(positions)


def deduce_separator_counts(arguments):
    affected = []
    for arg in arguments:
        if arg.separator and not arg.separator_count and arg.arguments:
            if arg.arguments and arg.arguments[0] != "...":
                arg.separator_count = count_separators(arg.arguments[0][1:-1],
                                                       arg.separator)
                affected.append(arg)
    return affected
