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
        self.member_count = None
        self.default_value = None
        self.member_type = None

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


def get_accumulated_count(arguments):
    min_count = max_count = 0
    for arg in arguments:
        count = arg.count
        if not count:
            continue
        if count[0]:
            min_count += count[0]
        if count[1] is None:
            max_count = None
        elif max_count is not None:
            max_count += count[1]
    if min_count != 0 or max_count != 0:
        return min_count, max_count
    else:
        return None


def make_member(name, properties, arguments, session):
    mem = Member(name, properties)
    mem.arguments = arguments
    mem.properties = properties
    mem.member_count = get_accumulated_count(arguments)
    mem.default_value = properties.get("default_value")
    if "member_type" in properties:
        mem.member_type = deducedtype.parse_type(properties["member_type"])
    return mem
