# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-11-20.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype


def deduce_valid_values(session):
    for arg in session.arguments:
        valid_values = arg.valid_values
        if valid_values:
            value_type = arg.value_type
            if deducedtype.is_tuple(value_type):
                subtypes = value_type.subtypes
                if len(valid_values) > len(subtypes):
                    session.logger.error(
                        "Number of entries in valid_values is %d, expected %d."
                        % (len(valid_values), len(subtypes)),
                        argument=arg)
                elif len(valid_values) < len(subtypes):
                    session.logger.warn(
                        "Number of entries in valid_values is %d, expected %d."
                        % (len(valid_values), len(subtypes)),
                        argument=arg)
                    final_validated_type = subtypes[len(valid_values) - 1]
                    for i in range(len(subtypes) - len(valid_values)):
                        if subtypes[i] == final_validated_type:
                            session.logger.debug(
                                "Repeating the last entry in valid_values.",
                                argument=arg)
                            valid_values.append(valid_values[-1])
                        else:
                            valid_values.append(None)
