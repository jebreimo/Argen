# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-11-11.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype


def validate_arguments(session):
    for argument in session.arguments:
        if argument.operation in ("assign", "append") \
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
        if not argument.flags and argument.value:
            session.logger.error("Only options can have a constant assigned"
                                 " to them.", argument=argument)
        if argument.separator_count and not argument.separator:
            session.logger.error("Separator is unspecified.",
                                 argument=argument)
        elif not argument.separator_count and argument.separator:
            session.logger.error("Can not determine the separator count.",
                                 argument=argument)
    if session.settings.immediate_callbacks:
        args = [a for a in session.arguments if not a.flags]
        if len(args) > 1 and any(a for a in args if a.callback):
            session.logger.error("There can only be one argument defined when"
                                 " ImmediateCallbacks is True.")
