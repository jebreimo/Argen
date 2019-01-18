# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-29.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import split_metavar


def get_first_and_last(str):
    return str[0] + str[-1]


def count_arguments(metavar):
    min_count = 0
    max_count = 0
    for part in split_metavar.split_metavar(metavar):
        if part == "...":
            max_count = None
        elif part[0] == "[" and part[-1] == "]" and max_count is not None:
            max_count += 1
        else:
            min_count += 1
            if max_count is not None:
                max_count += 1
    return min_count, max_count


def deduce_count_from_metavar(session):
    for arg in session.arguments:
        if not arg.count and not arg.flags and not arg.operation:
            arg.count = count_arguments(arg.metavar)
            session.logger.debug("Deduced count for %s: %s"
                                 % (arg, str(arg.count)), argument=arg)


def deduce_count_from_operation(session):
    for arg in session.arguments:
        if not arg.count and not arg.flags:
            if arg.operation == "assign":
                arg.count = 1, 1
            elif arg.operation in ("append", "extend"):
                arg.count = 1, None
            if arg.count:
                session.logger.debug("Deduced count for %s: %s"
                                     % (arg, str(arg.count)), argument=arg)
