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
        self.arguments = []
        self.given_properties = properties
        try:
            self.count = parser_tools.get_int_range(properties.get("count"))
        except ValueError:
            raise HelpFileError("Invalid count: %s, the value must be an integer or a range of integers (from..[to])"
                                % properties["count"])
        self.default_value = properties.get("default_value")
        self.member_action = properties.get("member_action")
        self.member_callback = properties.get("member_callback")
        self.member_type = properties.get("member_type")
        if "member_type" in properties:
            self.member_type = DeducedType(explicit=properties["member_type"])
        else:
            self.member_type = None
        if "value_type" in properties:
            self.value_type = DeducedType(explicit=properties["value_type"])
        else:
            self.value_type = None

    def __str__(self):
        values = self.__dict__
        keys = [k for k in values.keys() if k != "arguments"]
        keys.sort()
        kvs = ("%s: %s" % (k, values[k]) for k in keys if values[k] is not None)
        return "%s\n    %s" % (self.name, "\n    ".join(kvs))
