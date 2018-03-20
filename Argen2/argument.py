# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


ARGUMENT_PROPERTIES = {"callback", "count", "flags", "index", "inline",
                       "member_name", "meta_variable", "operation",
                       "post_operation", "separator", "separator_count",
                       "text", "value", "values"}

MEMBER_PROPERTIES = {"default", "member_inline", "member_callback", "type"}

_REVERSE_PROPERTY_ALIASES = {
    "operation": ["op"],
    "argument": ["arg"],
    "argument_type": ["argtype", "arg_type", "argumenttype"],
    "callback": ["call"],
    "member_name": ["mem", "member", "membername"],
    "meta_variable": ["metavar", "metavariable"],
    "separator": ["sep"],
    "separator_count": ["sepcount", "sep_count", "separatorcount"],
    "value": ["val"],
    "member_inline": ["meminline", "mem_inline", "meminline", "mem_inline",
                      "memberinline"],
    "member_callback": ["memcall", "mem_call", "memcallback", "mem_callback",
                        "membercallback"],
    "values": ["vals"]
}

PROPERTY_ALIASES = {}
for key in _REVERSE_PROPERTY_ALIASES:
    for value in _REVERSE_PROPERTY_ALIASES[key]:
        PROPERTY_ALIASES[value] = key

LEGAL_PROPERTIES = set(ARGUMENT_PROPERTIES).union(MEMBER_PROPERTIES)

DEFAULT_METAVAR_TYPES = {
    "num": "int",
    "number": "int",
    "real": "double",
    "float": "double",
    "hex": "int",
    "ratio": "double"
}

LEGAL_OPERATIONS = {
    "none",
    "set_value",
    "add_value",
    "add_values",
    "set_constant",
    "add_constant"
}

LEGAL_POST_OPERATIONS = {
    "none",
    "stop",
    "final"
}


class Argument:
    argument_counter = 0
    option_counter = 0

    def __init__(self, raw_text, properties=None):
        self.line_number = -1
        self.file_name = ""
        self.raw_text = raw_text
        self.properties = properties if properties else {}
        self.text = self.properties.get("text", raw_text)
        self.given_properties = dict(self.properties)
        self.deduced_properties = {}
        self.separator = None

    def __str__(self):
        kvs = ("%s: %s" % (k, self.properties[k]) for k in self.properties)
        return "%s\n    %s" % (self.text, "\n    ".join(kvs))

    # def set_properties(self, properties, override=False):
    #     if (not self.separator or override) and "separator" in properties:
    #         self.separator = properties["separator"]


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


def parse_metavar(text, separator=None, metavar_types=DEFAULT_METAVAR_TYPES):
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

