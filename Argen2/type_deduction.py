# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-04.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools


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


TYPE_CATEGORIES = {("number", "real"): "real",
                   ("number", "integer"): "integer",}


class DeducedType:
    EXPLICIT = 0
    SPECIFIC = 1
    CATEGORY = 2
    COMPOSITE = 3

    def __init__(self, confidence, type_name=None, subtypes=None):
        self.confidence = confidence
        self.type_name = type_name
        self.subtypes = subtypes
        self.source = None

    def __eq__(self, other):
        if not isinstance(other, DeducedType):
            return NotImplemented
        return self.confidence == other.confidence \
            and self.type_name == other.type_name \
            and self.subtypes == other.subtypes \
            and self.source == other.source

    def __lt__(self, other):
        if not isinstance(other, DeducedType):
            return NotImplemented
        if self.confidence != other.confidence:
            return self.confidence < other.confidence
        if self.type_name != other.type_name:
            return self.type_name < other.type_name
        if self.subtypes != other.subtypes:
            return self.subtypes < other.subtypes
        return self.source < other.source


def most_specific_type_category(category1, category2):
    if category1 == category2:
        return category1
    if category1 == "any":
        return category2
    if category2 == "any":
        return category1
    if category2 == "number":
        category1, category2 = category2, category1
    if category1 == "number" and category2 == "integer" or category2 == "real":
        return category2
    return None


def join_deduced_types(deduced_type1, deduced_type2):
    if deduced_type1 == deduced_type2:
        return deduced_type1
    if deduced_type1.confidence != deduced_type2.confidence:
        return min(deduced_type1, deduced_type2)
    if deduced_type1.confidence == DeducedType.CATEGORY:
        category = most_specific_type_category(deduced_type1.type_name,
                                               deduced_type2.type_name)
        if not category:
            return None
        return DeducedType(DeducedType.CATEGORY, category)
    if deduced_type1.confidence != DeducedType.COMPOSITE:
        return None
    if len(deduced_type1.subtypes) != len(deduced_type2.subtypes):
        return None
    type_name = most_specific_type_category(deduced_type1.type_name,
                                            deduced_type2.type_name)
    subtypes = []
    for subtype1, subtype2 in zip(deduced_type1.subtypes, deduced_type2.subtypes):
        subtype = join_deduced_types(subtype1, subtype2)
        if not subtype:
            return None
        subtypes.append(subtype)
    return DeducedType(DeducedType.COMPOSITE, type_name, subtypes)


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
            return DeducedType(DeducedType.CATEGORY, category)
        category = "integer"
        if s[i] in "xXbB":
            i += 1
    elif not s[i].isdigit():
        return None
    while i != n and s[i] in LEGAL_INT_CHARS:
        i += 1
    if i == n:
        return DeducedType(DeducedType.CATEGORY, category)
    suffix = s[i:].lower()
    if suffix in INT_SUFFIXES:
        return DeducedType(DeducedType.SPECIFIC, INT_SUFFIXES[suffix])
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
            return DeducedType(DeducedType.CATEGORY, "real")
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
            return DeducedType(DeducedType.CATEGORY, "real")
    suffix = s[i:].lower()
    if suffix in FLOAT_SUFFIXES:
        return DeducedType(DeducedType.SPECIFIC, FLOAT_SUFFIXES[suffix])
    return None


def looks_like_type_name(s):
    for c in s:
        if not (c.isidentifier() or c in " *&<>:"):
            return False
    return True


def get_class_name_parenthesis(s):
    pos = s.find("(")
    if pos == -1 or 0 <= s.find("{") < pos:
        return None
    if pos == 0:
        end_pos = s.find(")")
        if end_pos not in (-1, len(s) - 1) and looks_like_type_name(s[pos+1:end_pos]):
            return DeducedType(DeducedType.EXPLICIT, s[pos+1:end_pos].strip())
        else:
            return None
    return DeducedType(DeducedType.EXPLICIT, s[:pos].strip())


def get_class_name_braces(s):
    pos = s.find("{")
    if pos <= 0 or 0 <= s.find("(") < pos:
        return None
    return DeducedType(DeducedType.EXPLICIT, s[:pos].strip())


def find_end_of_whitespace(s, start_pos):
    for i in range(start_pos, len(s)):
        if not s[i].isspace():
            return i
    return -1


def get_tuple_parts(s):
    if not s or s[0] != "{" or s[-1] != "}":
        return None
    s = s[1:-1].strip()
    parts = []
    start_pos = 0
    while True:
        end_pos = parser_tools.find_char(s, ",", start_pos)
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


def has_common_type(deduced_types):
    if not deduced_types:
        return False
    common_type = deduced_types[0]
    for i in range(1, len(deduced_types)):
        common_type = join_deduced_types(common_type, deduced_types[i])
        if not common_type:
            return False
    return common_type is not None


def get_value_type(s):
    if not s:
        return None
    if s in ("true", "false"):
        return DeducedType(DeducedType.SPECIFIC, "bool")
    elif len(s) > 1 and s[0] == '"' and s[-1] == '"':
        return DeducedType(DeducedType.CATEGORY, "string")
    elif len(s) > 1 and s[0] == "'" and s[-1] == "'":
        return DeducedType(DeducedType.SPECIFIC, "char")
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
        value_type = DeducedType(DeducedType.SPECIFIC, MINMAX_CONSTANTS.get(s[:-4]))
        if value_type:
            return value_type
    tuple_parts = get_tuple_parts(s)
    if tuple_parts is not None:
        types = [get_value_type(part) for part in tuple_parts]
        if None not in types:
            if has_common_type(types):
                return DeducedType(DeducedType.COMPOSITE, "any", types)
            else:
                return DeducedType(DeducedType.COMPOSITE, "tuple", types)
    return None


def deduce_type_from_values_part(text, syntax):
    values = []
    for part in [t.strip() for t in parser_tools.split_text(text, syntax.value_separator)]:
        values.extend(t for t in (t.strip() for t in part.split(syntax.range_separator)) if t)
    value_types = []
    for value in values:
        value_type = get_value_type(value)
        if value_type:
            value_types.append(value_type)
    if not value_types:
        return None
    result = value_types[0]
    for i in range(1, len(value_types)):
        result = join_deduced_types(result, value_types[i])
        if not result:
            return None
    return result


def deduce_type_from_values(text, syntax):
    parts = parser_tools.split_and_unescape_text(text, syntax.values_entry_separator)
    types = []
    for part in parts:
        part_type = deduce_type_from_values_part(part, syntax)
        if not part_type:
            return None
        types.append(part_type)
    if not types:
        return None
    if has_common_type(types):
        return DeducedType(DeducedType.COMPOSITE, "any", types)
    return DeducedType(DeducedType.COMPOSITE, "tuple", types)


OPERATION_DEDUCED_TYPES = {
    "set_value": DeducedType(DeducedType.CATEGORY, "any"),
    "add_value": DeducedType(DeducedType.COMPOSITE, "list",
                             DeducedType(DeducedType.CATEGORY, "any")),
    "add_values": DeducedType(DeducedType.COMPOSITE, "list",
                              DeducedType(DeducedType.CATEGORY, "any")),
    "set_constant": DeducedType(DeducedType.CATEGORY, "any"),
    "add_constant": DeducedType(DeducedType.COMPOSITE, "list",
                                DeducedType(DeducedType.CATEGORY, "any"))
}

def deduce_type(member, syntax):
    if member.properties.get("type"):
        member.type = member.properties["type"]
        return member.type
    deduced_types = []
    default_type = get_value_type(member.properties.get("default"))
    if default_type:
        default_type.source = "default"
        deduced_types.append(default_type)
    for argument in member.arguments:
        if "values" in argument.given_properties:
            typ = deduce_type_from_values(argument.given_properties["values"],
                                          syntax)
            if typ:
                typ.source = "values"
                deduced_types.append(typ)
        if "value" in argument.given_properties:
            typ = get_value_type(argument.given_properties["value"], syntax)
            if typ:
                typ.source = "value"
                deduced_types.append(typ)
        if "operation" in argument.given_properties:
            op = argument.given_properties["operation"]
            if op in OPERATION_DEDUCED_TYPES:
                deduced_types.append(typ)
        if "count" in argument.given_properties:
            pass
        if "separator_count" in argument.given_properties:
            pass
    # Legal values
    # Metavar
    # Operation
    return None


def deduce_types(members):
    for member in members:
        deduce_type(member)
