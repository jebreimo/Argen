# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import name_tools


def make_member_name_from_flags(flags, taken_names):
    longest_flag = name_tools.get_longest_flag(flags)
    name = name_tools.make_name(longest_flag)
    prev_arg = taken_names.get(name)
    if prev_arg and (not prev_arg.flags or name == "_"):
        name = name_tools.make_unique_name(name, taken_names)
    return name


def make_member_name_from_metavar(metavar, taken_names):
    return name_tools.make_unique_name(name_tools.make_name(metavar),
                                       taken_names)


def deduce_member_names(session):
    unnamed = []
    taken_names = {}
    for arg in session.arguments:
        if arg.member_name:
            prev_arg = taken_names.get(arg.member_name)
            if not prev_arg:
                taken_names[arg.member_name] = arg
            elif arg.is_option() != prev_arg.is_option():
                session.logger.error("Options and arguments cannot share the "
                                     "same member name (%s)." % arg.member_name,
                                     argument=arg)
                session.logger.info("The conflicting argument or option "
                                    "is defined here.", argument=prev_arg)
        elif arg.member_name is None and arg.operation != "none":
            unnamed.append(arg)
    for arg in unnamed:
        if arg.flags:
            name = make_member_name_from_flags(arg.flags, taken_names)
        else:
            name = make_member_name_from_metavar(arg.metavar, taken_names)
        arg.member_name = name
        session.logger.debug("Deduced member name: " + name, argument=arg)
        if name not in taken_names:
            taken_names[name] = arg
