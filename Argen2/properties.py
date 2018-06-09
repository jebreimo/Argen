# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-16.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================

ARGUMENT_PROPERTIES = {"callback", "flags", "index",
                       "inline", "member_name", "operation", "post_operation",
                       "separator", "separator_count", "text", "valid_values",
                       "value", "variable"}

MEMBER_PROPERTIES = {"count", "default_value", "member_callback", "member_inline",
                     "member_type", "value_type"}

_REVERSE_PROPERTY_ALIASES = {
    "callback": ["call"],
    "default_value": ["default"],
    "member_name": ["mem", "member", "membername"],
    "operation": ["op"],
    "separator": ["sep"],
    "separator_count": ["sepcount", "sep_count", "separatorcount"],
    "member_callback": ["memcall", "mem_call", "memcallback", "mem_callback",
                        "membercallback"],
    "member_inline": ["meminline", "mem_inline", "meminline", "mem_inline",
                      "memberinline"],
    "member_type": ["memtype", "mem_type", "memtype", "mem_type",
                    "membertype"],
    "valid_values": ["validvalues", "values"],
    "value_type": ["type", "valuetype"],
    "variable": ["var"]
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
    "assign",
    "append",
    "extend"
}

LEGAL_POST_OPERATIONS = {
    "none",
    "abort",
    "final"
}
