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
        if argument.operation == "assign" \
                and argument.value is None \
                and deducedtype.is_tuple(argument.value_type):
            if argument.separator is None:
                session.logger.error("Separator is unspecified.",
                                     argument=argument)
            elif argument.separator_count is None:
                session.logger.error("Can not determine the separator count.",
                                     argument=argument)
