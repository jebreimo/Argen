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
    if not text and not separator:
        return 0, 0
    if not text:
        return 0, None
    if not separator:
        return 1, 1
    positions = parser_tools.find_all(text, separator)
    if not positions and parser_tools.is_ellipsis(text):
        return 0, None
    if not positions and text:
        return 1, None
    final_token_pos = positions[-1] + len(separator)
    if parser_tools.is_ellipsis(text[final_token_pos:]):
        return len(positions), None
    return len(positions) + 1, len(positions) + 1


def deduce_separator_counts(arguments):
    affected = []
    for arg in arguments:
        if arg.separator and not arg.separator_count and arg.arguments:
            if arg.arguments and arg.arguments[0] != "...":
                arg.separator_count = count_separators(arg.arguments[0][1:-1],
                                                       arg.separator)
                affected.append(arg)
    return affected
