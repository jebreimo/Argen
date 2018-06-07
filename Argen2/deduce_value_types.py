# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt
import parser_tools


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
    deduced_types = []
    for argument in member.arguments:
        if argument.valid_values:
            typ = deduce_type_from_valid_values(argument.valid_values)
            if typ:
                typ.source = "valid_values"
                deduced_types.append(typ)
        if argument.value:
            typ = dt.get_value_type(argument.value)
            if typ:
                typ.source = "value"
                deduced_types.append(typ)
        if argument.separator_count:
            typ = deduce_type_from_separator_count(argument.separator_count)
            if typ:
                typ.source = "separator_count"
                deduced_types.append(typ)
    return dt.join_list_of_deduced_types(deduced_types)[0]


def deduce_value_types(members):
    affected = []
    conflicts = []
    for member in members:
        if not member.value_type:
            typ = deduce_value_type(member)
            if typ:
                member.value_type = typ
                affected.append(member)
            else:
                conflicts.append(dict(message="Unable to determine value_type for member.",
                                      arguments=[member]))
    return affected, conflicts
