# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-16.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import member
import properties


def get_arguments_by_member_name(arguments):
    member_arguments = {}
    for arg in arguments:
        if arg.member_name:
            if arg.member_name not in member_arguments:
                member_arguments[arg.member_name] = [arg]
            else:
                member_arguments[arg.member_name].append(arg)
    return member_arguments


def make_member(member_name, arguments, session):
    if len(arguments) == 0:
        return None

    # Collect member properties from the member's arguments.
    has_conflicts = False
    member_props = {}
    for prop_name in properties.MEMBER_PROPERTIES:
        prev_arg = None
        prev_value = None
        for arg in arguments:
            value = arg.given_properties.get(prop_name)
            if value is not None:
                if prev_arg and value != prev_value:
                    session.logger.error("Conflicting values for member"
                                         " property %s: %s and %s."
                                         % (prop_name, value, prev_value),
                                         argument=arg)
                    session.logger.info("...defined as %s here" % prev_value,
                                        argument=prev_arg)
                    has_conflicts = True
                else:
                    prev_arg, prev_value = arg, value
        if prev_value:
            member_props[prop_name] = prev_value

    if has_conflicts:
        return None
    mem = member.make_member(member_name, member_props, arguments, session)
    return mem


def make_members(session):
    member_arguments = get_arguments_by_member_name(session.arguments)
    members = []
    for member_name in member_arguments:
        arguments = member_arguments[member_name]
        mem = make_member(member_name, arguments, session)
        if mem:
            members.append(mem)
            for arg in arguments:
                arg.member = mem
    session.members = members
