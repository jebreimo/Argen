# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import tools


def get_operations(arguments):
    return {a.operation for a in arguments if a.operation}


def report_member_size(member, arguments, session):
    session.logger.debug("Deduced member_size: %s"
                         % str(member.member_size), argument=arguments[0])
    for i in range(1, len(arguments)):
        session.logger.debug("... count is also defined here.",
                             argument=arguments[i])


def deduce_member_size(session):
    for mem in session.members:
        if mem.member_size:
            continue
        count_sum = tools.get_accumulated_count(mem.arguments)
        if count_sum:
            mem.member_size = count_sum
            args = [a for a in mem.arguments if a.count]
            report_member_size(mem, args, session)
        else:
            operations = get_operations(mem.arguments)
            if len(operations) == 1:
                if "assign" in operations:
                    mem.member_size = (1, 1)
                elif "append" in operations:
                    mem.member_size = (0, None)
                elif "extend" in operations:
                    mem.member_size = (0, None)
                args = [a for a in mem.arguments if a.operation]
                report_member_size(mem, args, session)
