# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-16.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================

ARGUMENT_PROPERTIES = {"argument", "callback", "count", "flags", "index",
                       "inline", "member_name", "operation", "post_operation",
                       "separator", "separator_count", "text", "value",
                       "values"}

MEMBER_PROPERTIES = {"default", "member_inline", "member_callback", "type"}

_REVERSE_PROPERTY_ALIASES = {
    "operation": ["op"],
    "argument": ["arg"],
    "callback": ["call"],
    "member_name": ["mem", "member", "membername"],
    "separator": ["sep"],
    "separator_count": ["sepcount", "sep_count", "separatorcount"],
    "member_inline": ["meminline", "mem_inline", "meminline", "mem_inline",
                      "memberinline"],
    "member_callback": ["memcall", "mem_call", "memcallback", "mem_callback",
                        "membercallback"]
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
    "abort",
    "final"
}
