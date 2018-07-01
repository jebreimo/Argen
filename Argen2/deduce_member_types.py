# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-09.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt


def deduce_member_type_fom_operation(member):
    operations = {a.operation for a in member.arguments if a.operation}
    if "extend" in operations:
        if not member.value_type:
            typ = dt.DeducedType(dt.Category.LIST,
                                 subtypes=[dt.DeducedType()])
        elif dt.is_list(member.value_type):
            typ = dt.DeducedType(prototype=member.value_type)
        else:
            typ = dt.DeducedType(dt.Category.LIST, subtypes=[member.value_type])
    elif "append" in operations:
        subtypes = [member.value_type or dt.DeducedType()]
        typ = dt.DeducedType(dt.Category.LIST, subtypes=subtypes)
    elif "assign" in operations:
        typ = dt.DeducedType(prototype=member.value_type)
    else:
        typ = None
    if typ:
        typ.source = "operation"
    return typ


def _get_separator(arguments):
    separators = set()
    max_count = 0
    for arg in arguments:
        if arg.separator:
            separators.add(arg.separator)
        if arg.separator_count:
            if arg.separator_count[1] is None:
                max_count = None
            elif max_count is not None:
                max_count = max(max_count, arg.separator_count[1])
    if len(separators) != 1:
        return None, 0
    return separators.pop(), max_count


def deduce_member_type_from_default_value(member):
    if not member.default_value:
        return None
    typ = dt.get_value_type(member.default_value)
    if typ:
        typ.source = "default_value"
    return typ


def deduce_member_type(member, logger):
    if member.member_type:
        return None
    logger.attribute = member.arguments[0]
    types = [dt.DeducedType()]
    if member.default_value:
        typ = deduce_member_type_from_default_value(member)
        if typ:
            types.append(typ)
    if member.count:
        if member.count[1] != 1:
            subtypes = [member.value_type or dt.DeducedType()]
            types.append(dt.DeducedType(dt.Category.LIST, subtypes=subtypes,
                                        source="count"))
    typ = deduce_member_type_fom_operation(member)
    if typ:
        types.append(typ)
    result = dt.join_list_of_deduced_types(types, logger)
    logger.argument = None
    return result


def deduce_member_types(session):
    for member in session.members:
        if not member.member_type:
            typ = deduce_member_type(member, session.logger)
            if typ:
                member.member_type = typ
                session.logger.debug("Deduced member type for %s from %s: %s."
                                     % (member.name, typ.source,
                                        member.member_type),
                                     argument=member.arguments[0])
                for arg in member.arguments[1:]:
                    session.logger.debug("...also defined here.", argument=arg)
            else:
                session.logger.error("Unable to deduce member type for %s."
                                     % member.name,
                                     argument=member.arguments[0])
                for arg in member.arguments[1:]:
                    session.logger.info("...also defined here.", argument=arg)
