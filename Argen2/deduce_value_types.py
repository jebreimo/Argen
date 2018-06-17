# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt


def deduce_type_from_values_part(ranges):
    value_types = []
    for lo, hi in ranges:
        if lo:
            value_types.append(dt.get_value_type(lo))
        if hi and lo != hi:
            value_types.append(dt.get_value_type(hi))
    if not value_types:
        return dt.DeducedType()
    result = value_types[0]
    for i in range(1, len(value_types)):
        result, error = dt.join_deduced_types(result, value_types[i])
        if not result:
            return None
    return result


def deduce_type_from_valid_values(values):
    types = []
    for ranges in values:
        part_type = deduce_type_from_values_part(ranges)
        if not part_type:
            return None
        types.append(part_type)
    if not types:
        return None
    if len(types) == 1:
        return types[0]
    else:
        return dt.DeducedType(dt.Category.COMPOSITE, subtypes=types)


def deduce_type_from_value(value, separator, max_separators):
    if separator:
        types = []
        maxsplit = -1 if max_separators is None else max_separators
        for part in value.split(separator, maxsplit):
            value_type = dt.get_value_type(part)
            if value_type:
                types.append(value_type)
            else:
                types.append(dt.DeducedType())
        return dt.DeducedType(dt.Category.COMPOSITE, subtypes=types)
    else:
        value_type = dt.get_value_type(value)
        if value_type:
            return value_type
        else:
            return dt.DeducedType()


def deduce_type_from_separator_count(count):
    if not count:
        return None, None
    if count[0] == count[1]:
        if count[0] == 0:
            return dt.DeducedType()
        return dt.DeducedType(dt.Category.COMPOSITE,
                              subtypes=[dt.DeducedType()] * (count[0] + 1))
    else:
        return dt.DeducedType(dt.Category.LIST, subtypes=[dt.DeducedType()])


def deduce_value_type(member):
    if member.value_type:
        return None, None
    deduced_types = [dt.DeducedType()]
    for argument in member.arguments:
        if argument.valid_values:
            typ = deduce_type_from_valid_values(argument.valid_values)
            if typ:
                typ.source = "valid_values"
                deduced_types.append(typ)
        if argument.value:
            if argument.separator_count:
                max_separators = argument.separator_count[1]
            else:
                max_separators = None
            typ = deduce_type_from_value(argument.value,
                                         argument.separator,
                                         max_separators)
            if typ:
                typ.source = "value"
                deduced_types.append(typ)
        if argument.separator_count:
            typ = deduce_type_from_separator_count(argument.separator_count)
            if typ:
                typ.source = "separator_count"
                deduced_types.append(typ)
    return dt.join_list_of_deduced_types(deduced_types)[0]


def deduce_value_types(session):
    for member in session.members:
        if not member.value_type:
            typ = deduce_value_type(member)
            if typ:
                member.value_type = typ
                session.logger.debug("Deduced value type for %s: %s."
                                     % (member.name, member.value_type),
                                     argument=member.arguments[0])
                for arg in member.arguments[1:]:
                    session.logger.debug("...also defined here.", argument=arg)
            else:
                session.logger.warn("Unable to deduce value type for %s."
                                    % member.name,
                                    argument=member.arguments[0])
                for arg in member.arguments[1:]:
                    session.logger.info("...also defined here.", argument=arg)
