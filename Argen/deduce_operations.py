# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-10.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def get_member_operations(arguments):
    member_operations = {}
    for arg in arguments:
        if arg.operation:
            mem = arg.member
            if mem:
                if mem.name not in member_operations:
                    member_operations[mem.name] = {arg.operation}
                else:
                    member_operations[mem.name].add(arg.operation)
    return member_operations


def deduce_operation(argument, member_operations):
    if argument.operation:
        return argument.operation
    elif not argument.member:
        return "none"

    member_has_count = argument.member.size and argument.member.size[1] != 1
    argument_has_count = argument.separator_count \
        and argument.separator_count[1] != 0
    if argument.member and argument.member.name in member_operations:
        operations = member_operations[argument.member.name]
        if "extend" in operations:
            if not argument_has_count:
                return "append"
            else:
                return "extend"
        elif "append" in operations:
            return "append"
        elif "assign" in operations:
            if member_has_count and not argument_has_count:
                return "append"
            else:
                return "assign"
        else:
            return "none"
    elif not member_has_count:
        return "assign"
    else:
        return "append"


def deduce_operations(session):
    member_operations = get_member_operations(session.arguments)
    for arg in session.arguments:
        if not arg.post_operation:
            arg.post_operation = "none"
        if arg.operation:
            continue
        arg.operation = deduce_operation(arg, member_operations)
        session.logger.debug("Deduced operation: %s." % arg.operation,
                             argument=arg)
