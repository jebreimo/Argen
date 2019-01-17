# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools
import split_metavar


def get_first_and_last(str):
    return str[0] + str[-1]


def count_separators(metavar, separator):
    if not separator:
        return 0, 0
    if not metavar:
        return 0, None
    tokens = split_metavar.split_metavar(metavar)
    metavar = tokens[0]
    if get_first_and_last(metavar) in ("<>", "[]"):
        metavar = metavar[1:-1]
    positions = parser_tools.find_all(metavar, separator)
    if not positions:
        return 0, None
    if metavar.endswith(".."):
        return 0, None
    return len(positions), len(positions)


def deduce_separator_counts(session):
    for arg in session.arguments:
        if arg.separator and not arg.separator_count and arg.metavar:
            tokens = split_metavar.split_metavar(arg.metavar)
            metavar = tokens[0]
            arg.separator_count = count_separators(metavar, arg.separator)
            session.logger.debug("Deduced separator count: (%s, %s)"
                                 % arg.separator_count,
                                 argument=arg)
