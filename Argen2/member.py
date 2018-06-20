# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-01-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools
from deducedtype import DeducedType
from helpfileerror import HelpFileError


class Member:
    def __init__(self, name, properties):
        self.name = name
        self.given_properties = properties
        self.arguments = None
        self.count = None
        self.default_value = None
        self.member_action = None
        self.member_callback = None
        self.member_type = None
        self.member_type = None
        self.value_type = None

    def __str__(self):
        values = self.__dict__
        keys = [k for k in values.keys() if k != "arguments"]
        keys.sort()
        kvs = ("%s: %s" % (k, values[k]) for k in keys if values[k] is not None)
        return "%s\n    %s" % (self.name, "\n    ".join(kvs))


def make_member(name, properties, arguments, session):
    mem = Member(name, properties)
    mem.arguments = arguments
    mem.given_properties = properties
    try:
        mem.count = parser_tools.get_int_range(properties.get("count"))
    except ValueError:
        args = [a for a in arguments if "count" in a.given_properties] or [None]
        session.logger.error("Invalid count: %s. The value must be an integer "
                             "or a range of integers (from..[to])"
                             % properties["count"], argument=args[0])
    mem.default_value = properties.get("default_value")
    mem.member_action = properties.get("member_action")
    mem.member_callback = properties.get("member_callback")
    if "member_type" in properties:
        mem.member_type = DeducedType(explicit=properties["member_type"])
    if "value_type" in properties:
        mem.value_type = DeducedType(explicit=properties["value_type"])
    return mem
