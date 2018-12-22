# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-01-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools
import deducedtype


class Member:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.arguments = None
        self.default_value = None
        self.member_type = None
        self.size = None

    def __str__(self):
        values = self.__dict__
        keys = [k for k in values.keys() if k != "arguments"]
        keys.sort()
        kvs = ("%s: %s" % (k, values[k]) for k in keys if values[k] is not None)
        return "%s\n    %s" % (self.name, "\n    ".join(kvs))

    def is_option(self):
        for arg in self.arguments:
            if arg.flags:
                return True


def get_accumulated_size(arguments):
    min_size = max_size = 0
    for arg in arguments:
        count = arg.count
        if not count:
            if not arg.flags:
                count = (1, 1)
            else:
                continue
        if count[0]:
            min_size += count[0]
        if count[1] is None:
            max_size = None
        elif max_size is not None:
            max_size += count[1]
    if min_size != 0 or max_size != 0:
        return min_size, max_size
    else:
        return None


def foo(member, name, session):
    try:
        return parser_tools.get_int_range(member.properties.get(name))
    except ValueError:
        for argument in member.arguments:
            if name in argument.properties:
                break
        else:
            argument = None
        session.logger.error(
            "Invalid %s: %s. The value must be an integer "
            "or a range of integers (from..to, from.. or ..to)"
            % (name, member.properties[name]), argument=argument)


def make_member(name, properties, arguments, session):
    mem = Member(name, properties)
    mem.arguments = arguments
    mem.properties = properties
    mem.size = foo(mem, "size", session)
    if not mem.size:
        mem.size = get_accumulated_size(arguments)

    mem.default_value = properties.get("default_value")
    if "member_type" in properties:
        mem.member_type = deducedtype.parse_type(properties["member_type"])
    return mem
