# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import properties


def get_int_property(dict, key):
    if key in dict:
        return int(dict.get(key))
    else:
        return None


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
        # self.deduced_properties = {}

        self.callback = properties.get("callback")
        self.count = None
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
        self.separator_count = get_int_property(properties, "separator_count")
        self.text = properties.get("text", raw_text)

        self.member = None

    def __str__(self):
        vals = self.__dict__
        keys = list(vals.keys())
        keys.sort()
        kvs = ("%s: %s" % (k, vals[k]) for k in keys if vals[k] is not None)
        return "%s\n    %s" % (self.raw_text, "\n    ".join(kvs))

    def is_option(self):
        return len(self.flags) != 0


def find_metavar_separator(text):
    candidates = {}
    for i, ch in enumerate(text if not text.endswith("...") else text[:-3]):
        if ch == "x" or not ch.isalnum():
            if ch in candidates:
                candidates[ch].append(i)
            else:
                candidates[ch] = [i]
    for c in candidates:
        if c == "x":
            def check_text(s):
                return s.isalnum() and s.isupper()
        else:
            def check_text(s):
                return s.isalnum()
        m = 0
        for n in candidates[c]:
            if m == n or not check_text(text[m:n]) or n == len(text) - 1:
                break
            m = n + 1
        else:
            return c
    return None


def tokenize_metavar(text, separator):
    has_ellipsis = text.endswith("...")
    if separator is None:
        separator = find_metavar_separator(text)
    if separator:
        names = text.split(separator)
    else:
        names = [text]
    if has_ellipsis:
        if names[-1] == "...":
            del names[-1]
        else:
            names[-1] = names[-1][:-3]
    return names, separator, has_ellipsis


def determine_metavar_type(names, metavar_types):
    types = set()
    for name in names:
        if name in metavar_types:
            types.add(metavar_types[name])
        else:
            name = name.strip("0123456789").lower()
            types.add(metavar_types.get(name, "std::string"))
    if len(types) == 1:
        return types.pop()
    else:
        return "std::string"


def parse_metavar(text,
                  separator=None,
                  metavar_types=properties.DEFAULT_METAVAR_TYPES):
    names, separator, has_ellipsis = tokenize_metavar(text, separator)
    properties = {"type": determine_metavar_type(names, metavar_types),
                  "meta_variable": text}
    if separator:
        properties["separator"] = separator
        if has_ellipsis or len(names) == 1:
            properties["separator_count"] = "0..."
        else:
            properties["separator_count"] = str(len(names) - 1)
    else:
        properties["separator_count"] = "0"
    return properties


# def compare_metavar_properties(aprops, bprops):
#     akeys = list(aprops.keys())
#     bkeys = list(bprops.keys())
#     if sorted(akeys) != sorted(bkeys):
#         return False
#     for key in akeys:
#         if key != "metavar" and aprops[key] != bprops[key]:
#             return False
#     return True
