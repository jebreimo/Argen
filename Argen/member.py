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
        self.member_size = None

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


def parse_size(member, name, session):
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
    mem.member_size = parse_size(mem, "size", session)
    mem.default_value = properties.get("default_value")
    if "member_type" in properties:
        mem.member_type = deducedtype.parse_type(properties["member_type"])
    return mem
