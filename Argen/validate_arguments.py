# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-11-11.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype


def find_problematic_argument_callbacks(arguments):
    problematic_arguments = []
    known_index = True
    for i, arg in enumerate(arguments):
        count = arg.member.count
        if arg.callback:
            if not known_index:
                problematic_arguments.append(arg)
            elif count and count[0] != count[1] and i + 1 != len(arguments):
                problematic_arguments.append(arg)
        if count and count[0] != count[1]:
            known_index = False
    return problematic_arguments


def validate_arguments(session):
    for argument in session.arguments:
        if argument.operation == "assign" \
                and argument.value is None \
                and deducedtype.is_tuple(argument.value_type):
            if argument.separator is None:
                session.logger.error("Separator is unspecified.",
                                     argument=argument)
            elif argument.separator_count is None:
                session.logger.error("Can not determine the separator count.",
                                     argument=argument)
        elif argument.operation == "none" \
                and argument.member_name \
                and not (argument.callback or argument.inline):
            session.logger.warn("No value is assigned to member '%s'."
                                % argument.member_name, argument=argument)

    if session.settings.immediate_callbacks:
        non_options = [a for a in session.arguments if not a.flags]

        problematic_args = find_problematic_argument_callbacks(non_options)
        for arg in problematic_args:
            count = arg.member.count
            is_are = "s are" if count[1] != 1 else " is"
            session.logger.warn("It is necessary to read all the arguments and"
                                " options to determine which argument%s %s."
                                " The callback for this argument will therefore"
                                " see the final state of the options, not"
                                " necessarily the state they have where the "
                                " argument appears on the command line."
                                % (is_are, arg.metavar))
    # for mem in session.members:
    #     if mem.count and mem.count == (1, 1) and len(mem.arguments) > 1:
    #         session.logger.warn("")
    # return option.member.count[0] > 0 and len(option.member.arguments) == 1
