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
    if text.endswith(".."):
        return 0, None
    return len(positions), len(positions)


def get_first_and_last(str):
    return str[0] + str[-1]


def deduce_separator_counts(session):
    for arg in session.arguments:
        if arg.separator and not arg.separator_count and arg.metavar:
            metavar = arg.metavar
            if get_first_and_last(arg.metavar) in ("<>", "[]"):
                metavar = arg.metavar[1:-1]
            arg.separator_count = count_separators(metavar,
                                                   arg.separator)
            session.logger.debug("Deduced separator count: (%s, %s)"
                                 % arg.separator_count,
                                 argument=arg)
