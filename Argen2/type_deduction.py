# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-04.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


LEGAL_INT_CHARS = {c: True for c in "0123456789ABCDEFabcdef'"}
INT_SUFFIXES = {"ull": "unsigned long long",
                "llu": "unsigned long long",
                "ll": "long long",
                "ul": "unsigned long",
                "lu": "unsigned long",
                "l": "long",
                "u": "unsigned"}
LEGAL_FLOAT_CHARS = {c: True for c in "0123456789'"}
FLOAT_SUFFIXES = {"f": "float",
                  "l": "long double"}
MINMAX_CONSTANTS = {"CHAR": "char",
                    "SCHAR": "signed char",
                    "SHRT": "short",
                    "INT": "int",
                    "LONG": "long",
                    "LLONG": "long long",
                    "UCHAR": "unsigned char",
                    "USHRT": "unsigned short",
                    "UINT": "unsigned int",
                    "ULONG": "unsigned long",
                    "ULLONG": "unsigned long long",
                    "SIZE": "size_t",
                    "INT8": "int8_t",
                    "INT16": "int16_t",
                    "INT32": "int32_t",
                    "INT64": "int64_t",
                    "UINT8": "uint8_t",
                    "UINT16": "uint16_t",
                    "UINT32": "uint32_t",
                    "UINT64": "uint64_t",
                    "FLT": "float",
                    "DBL": "double",
                    "LDBL": "long double",
                    "FLT_TRUE": "float",
                    "DBL_TRUE": "double",
                    "LDBL_TRUE": "long double"}


class DeducedType:
    def __init__(self):
        self.specific_type = None
        self.type_category = None
        self.subtypes = []
        self.source = None

    @staticmethod
    def specific(typ):
        dt = DeducedType()
        dt.specific_type = typ
        return dt

    @staticmethod
    def category(typ):
        dt = DeducedType()
        dt.type_category = typ
        return dt

    @staticmethod
    def subtypes(subtypes):
        dt = DeducedType()
        dt.subtypes = subtypes
        return dt


def get_int_type(s):
    if not s:
        return None
    n = len(s)
    i = 0
    if s[i] in "+-":
        i += 1
        if i == n:
            return None
    category = "number"
    if s[i] == '0':
        i += 1
        if i == n:
            return DeducedType.category(category)
        category = "integer"
        if s[i] in "xXbB":
            i += 1
    elif not s[i].isdigit():
        return None
    while i != n and s[i] in LEGAL_INT_CHARS:
        i += 1
    if i == n:
        return DeducedType.category(category)
    suffix = s[i:].lower()
    if suffix in INT_SUFFIXES:
        return DeducedType.specific(INT_SUFFIXES[suffix])
    return None


def get_float_type(s):
    if not s:
        return None
    n = len(s)
    i = 0
    # Integer part
    if s[i] in "+-":
        i += 1
        if i == n:
            return None
    if not s[i].isdigit():
        return None
    while i != n and s[i] in LEGAL_FLOAT_CHARS:
        i += 1
    if i == n or s[i] not in ".eE":
        return None
    # Fraction part
    if s[i] == ".":
        i += 1
        while i != n and s[i] in LEGAL_FLOAT_CHARS:
            i += 1
        if i == n:
            return DeducedType.category("real")
    # Exponent part
    if s[i] in "eE":
        i += 1
        if i == n:
            return None
        if s[i] in "+-":
            i += 1
            if i == n or not s[i].isdigit():
                return None
        while i != n and s[i] in LEGAL_FLOAT_CHARS:
            i += 1
        if i == n:
            return DeducedType.category("real")
    suffix = s[i:].lower()
    if suffix in FLOAT_SUFFIXES:
        return DeducedType.specific(FLOAT_SUFFIXES[suffix])
    return None


def get_class_name_parenthesis(s):
    pos = s.find("(")
    if pos == -1 or 0 <= s.find("{") < pos:
        return None
    if pos == 0:
        end_pos = s.find(")")
        if end_pos != -1:
            return DeducedType.specific(s[pos+1:end_pos].strip())
        else:
            return None
    return DeducedType.specific(s[:pos].strip())


def get_class_name_braces(s):
    pos = s.find("{")
    if pos < 1 or 0 <= s.find("{") < pos:
        return None
    return DeducedType.specific(s[:pos].strip())


def find_unescaped_char(s, chr, start_pos):
    escape = False
    for i in range(start_pos, len(s)):
        if escape:
            escape = False
        elif s[i] == '\\':
            escape = True
        elif s[i] == chr:
            return i
    return -1


def find_end_of_whitespace(s, start_pos):
    for i in range(start_pos, len(s)):
        if not s[i].isspace():
            return i
    return -1


def find_char(s, chr, start_pos):
    i = start_pos
    while i < len(s):
        if s[i] == chr:
            return i
        if s[i] == "(":
            i = find_char(s, ")", i + 1)
        elif s[i] == "{":
            i = find_char(s, "}", i + 1)
        elif s[i] in "\"'":
            i = find_unescaped_char(s, s[i], i + 1)
        if i == -1:
            break
        i += 1
    return -1


def get_tuple_parts(s):
    if not s or s[0] != "{" or s[-1] != "}":
        return None
    s = s[1:-1].strip()
    parts = []
    start_pos = 0
    while True:
        end_pos = find_char(s, ",", start_pos)
        if end_pos == -1:
            part = s[start_pos:].strip()
            if part:
                parts.append(part)
            break
        part = s[start_pos:end_pos].strip()
        if not part:
            return None
        parts.append(part)
        start_pos = end_pos + 1
    return parts


def get_value_type(s):
    if not s:
        return None
    if s in ("true", "false"):
        return DeducedType.specific("bool")
    elif len(s) > 1 and s[0] == '"' and s[-1] == '"':
        return DeducedType.category("string")
    elif len(s) > 1 and s[0] == "'" and s[-1] == "'":
        return DeducedType.specific("char")
    value_type = get_int_type(s)
    if value_type:
        return value_type
    value_type = get_float_type(s)
    if value_type:
        return value_type
    value_type = get_class_name_parenthesis(s)
    if value_type:
        return value_type
    value_type = get_class_name_braces(s)
    if value_type:
        return value_type
    if s.endswith("_MIN") or s.endswith("_MAX"):
        value_type = DeducedType.specific(MINMAX_CONSTANTS.get(s[:-4]))
        if value_type:
            return value_type
    tuple_parts = get_tuple_parts(s)
    if tuple_parts is not None:
        types = [get_value_type(part) for part in tuple_parts]
        if None not in types:
            return DeducedType.subtypes(types)
    return None


def deduce_type(member):
    if member.properties.get("type"):
        return member.properties["type"]
    deduced_types = []
    default = member.properties.get("default")
    default_type = get_value_type(default)
    if default_type:
        default_type.source = "default"
        deduced_types.append(default_type)
    # for
    return None


def deduce_types(members):
    for member in members:
        deduce_type(member)
