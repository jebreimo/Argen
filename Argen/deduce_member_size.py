# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-07.
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


def get_operations(arguments):
    return {a.operation for a in arguments if a.operation}


def deduce_member_count(session):
    for mem in session.members:
        if mem.member_size:
            continue
        count_sum = get_accumulated_count(mem.arguments)
        if count_sum:
            mem.member_size = count_sum
            args = [a for a in mem.arguments if a.count]
            session.logger.debug("Deduced member_size: %s" % str(mem.member_size),
                                 argument=args[0])
            for i in range(1, len(args)):
                session.logger.debug("... count is also defined here.",
                                     argument=args[i])
        else:
            operations = get_operations(mem.arguments)
            if len(operations) == 1:
                if "assign" in operations:
                    mem.member_size = (1, 1)
                elif "append" in operations:
                    mem.member_size = (0, None)
                elif "extend" in operations:
                    mem.member_size = (0, None)
