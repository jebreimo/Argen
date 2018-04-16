# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-16.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
from member import Member
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


def make_member(member_name, arguments, conflicts):
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
                    conflicts.append(dict(property=prop_name,
                                          values=[value, prev_value],
                                          arguments=[arg, prev_arg]))
                    has_conflicts = True
                else:
                    prev_arg, prev_value = arg, value
        if prev_value:
            member_props[prop_name] = prev_value

    if has_conflicts:
        return None
    member = Member(member_name, member_props)
    member.arguments = arguments
    return member


def make_members(arguments):
    member_arguments = get_arguments_by_member_name(arguments)
    members = []
    conflicts = []
    for member_name in member_arguments:
        arguments = member_arguments[member_name]
        member = make_member(member_name, arguments, conflicts)
        if member:
            members.append(member)
            for arg in arguments:
                arg.member = member
    return members, conflicts
