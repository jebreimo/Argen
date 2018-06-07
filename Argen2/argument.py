# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools
from helpfileerror import HelpFileError


def get_int_property(dict, key):
    value = dict.get(key)
    if value:
        return int(value)
    else:
        return None


def get_int_range(text):
    if not text:
        return None
    parts = parser_tools.split_range(text)
    if parts:
        a, b = parts[0].strip(), parts[1].strip()
        if a or b:
            return (int(a, 0) if a else 0), (int(b, 0) if b else None)
        else:
            return 0, None
    else:
        a = int(text.strip(), 0)
        return a, a


def get_int_range_property(dict, key):
    return get_int_range(dict.get(key))


def parse_valid_values(text):
    if not text:
        return None
    result = []
    parts = parser_tools.split_text(text, ":")
    for part in parts:
        values = []
        subparts = parser_tools.split_text(part, ",")
        for subpart in subparts:
            from_to = parser_tools.split_text(subpart, "..")
            if len(from_to) == 2:
                values.append((from_to[0].strip(), from_to[1].strip()))
            else:
                subpart = subpart.strip()
                values.append((subpart, subpart))
        result.append(values)
    return result


class Argument:
    argument_counter = 1

    def __init__(self, raw_text, properties=None):
        if properties is None:
            properties = {}

        self.auto_index = Argument.argument_counter
        Argument.argument_counter += 1

        self.line_number = -1
        self.file_name = ""
        self.raw_text = raw_text
        # self.properties = properties if properties else {}
        self.given_properties = dict(properties)

        self.callback = properties.get("callback")
        try:
            self.count = get_int_range_property(properties, "count")
        except ValueError:
            raise HelpFileError("Invalid count: %s, the value must be an integer or a range of integers (from..[to])"
                                % properties["count"])
        if "flags" in properties:
            self.flags = properties["flags"].split()
        else:
            self.flags = None
        self.index = get_int_property(properties, "index")
        self.inline = properties.get("inline")
        self.member_name = properties.get("member_name")
        self.metavar = properties.get("argument")
        self.operation = properties.get("operation")
        self.post_operation = properties.get("post_operation")
        self.separator = properties.get("separator")
        try:
            self.separator_count = get_int_range_property(properties,
                                                          "separator_count")
        except ValueError:
            raise HelpFileError("Invalid separator_count: %s, the value must be an integer or a range of integers (from..[to])"
                                % properties["separator_count"])

        self.text = properties.get("text", raw_text)
        self.valid_values = parse_valid_values(properties.get("valid_values"))
        self.value = properties.get("value")

        self.arguments = None
        self.member = None

    def __str__(self):
        vals = self.__dict__
        keys = list(vals.keys())
        keys.sort()
        kvs = ("%s: %s" % (k, vals[k]) for k in keys if vals[k] is not None)
        return "%s\n    %s" % (self.raw_text, "\n    ".join(kvs))

    def is_option(self):
        return len(self.flags) != 0


# def compare_metavar_properties(aprops, bprops):
#     akeys = list(aprops.keys())
#     bkeys = list(bprops.keys())
#     if sorted(akeys) != sorted(bkeys):
#         return False
#     for key in akeys:
#         if key != "metavar" and aprops[key] != bprops[key]:
#             return False
#     return True
