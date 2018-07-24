# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools


def get_int_property(dict, key):
    value = dict.get(key)
    if value:
        return int(value)
    else:
        return None


def parse_valid_values(text):
    if not text:
        return None
    result = []
    parts = parser_tools.split_text(text, ":")
    for part in parts:
        values = []
        subparts = parser_tools.split_text(part, ",")
        for subpart in (s.strip() for s in subparts):
            from_to = parser_tools.split_range(subpart)
            if from_to:
                values.append((from_to[0], from_to[1]))
            elif subpart:
                values.append((subpart, subpart))
            else:
                values.append((None, None))
        result.append(values)
    return result


class Argument:
    argument_counter = 1

    def __init__(self, raw_text, properties=None):
        self.auto_index = Argument.argument_counter
        Argument.argument_counter += 1
        self.line_number = None
        self.file_name = None
        self.raw_text = raw_text
        self.properties = properties
        self.callback = None
        self.flags = None
        self.index = None
        self.inline = None
        self.member_name = None
        self.metavar = None
        self.operation = None
        self.post_operation = None
        self.separator = None
        self.separator_count = None
        self.text = None
        self.valid_values = None
        self.value = None
        self.option_name = None
        self.member = None
        self.arguments = None

    def __str__(self):
        vals = self.__dict__
        keys = list(vals.keys())
        keys.sort()
        kvs = ("%s: %s" % (k, vals[k]) for k in keys if vals[k] is not None)
        return "%s\n    %s" % (self.raw_text, "\n    ".join(kvs))

    def is_option(self):
        return len(self.flags) != 0


def make_argument(raw_text, properties, session, file_name, line_number):
    arg = Argument(raw_text, dict(properties))
    arg.line_number = line_number
    arg.file_name = file_name
    arg.callback = properties.get("callback")
    if "flags" in properties:
        arg.flags = properties["flags"].split()
    arg.index = get_int_property(properties, "index")
    arg.inline = properties.get("inline")
    arg.member_name = properties.get("member_name")
    arg.metavar = properties.get("argument")
    arg.operation = properties.get("operation")
    arg.post_operation = properties.get("post_operation")
    arg.separator = properties.get("separator")
    if arg.separator is not None:
        if len(arg.separator) != 1:
            session.logger.error("Invalid separator: \"%s\". Separators must "
                                 "be a single non-space character."
                                 % arg.separator, argument=arg)
    try:
        arg.separator_count = parser_tools.get_int_range(
            properties.get("separator_count"))
    except ValueError:
        session.logger.error("Invalid separator_count: %s, the value must be "
                             "an integer or a range of integers (from..[to])"
                             % properties["separator_count"])
    arg.text = properties.get("text", raw_text)
    arg.valid_values = parse_valid_values(properties.get("valid_values"))
    arg.value = properties.get("value")
    return arg

# def compare_metavar_properties(aprops, bprops):
#     akeys = list(aprops.keys())
#     bkeys = list(bprops.keys())
#     if sorted(akeys) != sorted(bkeys):
#         return False
#     for key in akeys:
#         if key != "metavar" and aprops[key] != bprops[key]:
#             return False
#     return True
