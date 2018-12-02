# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import name_tools


def make_option_name_from_flags(flags, taken_names):
    longest_flag = name_tools.get_longest_flag(flags)
    name = name_tools.make_name(longest_flag)
    if name == "_":
        return None
    if name in taken_names:
        name = name_tools.make_unique_name(name, taken_names)
    return name


def deduce_option_names(session):
    taken_names = {}
    unnamed = []
    for arg in session.arguments:
        if arg.flags:
            name = make_option_name_from_flags(arg.flags, taken_names)
            if name:
                arg.option_name = name
                session.logger.debug("Deduced option name: " + name,
                                     argument=arg)
                taken_names[name] = arg
            else:
                unnamed.append(arg)
    for arg in unnamed:
        name = name_tools.make_unique_name("symbols", taken_names)
        arg.option_name = name
        session.logger.debug("Deduced option name: " + name,
                             argument=arg)
        taken_names[name] = arg
