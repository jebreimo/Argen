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


# Categories:
# any
#   composite
#     list
#     tuple
#   value
#     string
#     number
#       integer
#       real
#     bool


class Category:
    ANY = "any"
    COMPOSITE = "composite"
    LIST = "list"
    TUPLE = "tuple"
    VALUE = "value"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    REAL = "real"
    BOOL = "bool"


CATEGORY_TYPES = {
    Category.ANY: "std::string",
    Category.LIST: "std::vector",
    Category.TUPLE: "std::tuple",
    Category.VALUE: "std::string",
    Category.STRING: "std::string",
    Category.NUMBER: "int",
    Category.INTEGER: "int",
    Category.REAL: "double",
    Category.BOOL: "bool"
}


class DeducedType:
    def __init__(self, category=Category.ANY, specific=None,
                 explicit=None, subtypes=None):
        self.category = category ## any composite list tuple value string integer real bool
        self.specific = specific
        self.explicit = explicit
        self.subtypes = subtypes
        self.source = None

    def __eq__(self, other):
        if not isinstance(other, DeducedType):
            return NotImplemented
        return self.explicit == other.explicit \
            and self.specific == other.specific \
            and self.category == other.category \
            and self.subtypes == other.subtypes

    def __lt__(self, other):
        if not isinstance(other, DeducedType):
            return NotImplemented
        if self.category != other.category:
            return self.category < other.category
        if self.specific != other.specific:
            return self.specific < other.specific
        if self.explicit != other.explicit:
            return self.explicit < other.explicit
        if self.subtypes != other.subtypes:
            return self.subtypes < other.subtypes

    def __str__(self):
        if self.explicit:
            return self.explicit
        if self.specific:
            return self.specific
        if not self.subtypes:
            return CATEGORY_TYPES[self.category]
        return "%s<%s>" % (CATEGORY_TYPES[self.category],
                           ", ".join(str(st) for st in self.subtypes))


PARENT_CATEGORIES = {
    Category.ANY: None,
    Category.COMPOSITE: Category.ANY,
    Category.LIST: Category.COMPOSITE,
    Category.TUPLE: Category.COMPOSITE,
    Category.VALUE: Category.ANY,
    Category.STRING: Category.VALUE,
    Category.NUMBER: Category.VALUE,
    Category.INTEGER: Category.NUMBER,
    Category.REAL: Category.NUMBER,
    Category.BOOL: Category.VALUE
}


def is_child_category(child, parent):
    while child:
        if child == parent:
            return True
        child = PARENT_CATEGORIES[child]
    return False


def most_specific_category(category1, category2):
    if category1 == category2:
        return category1
    if is_child_category(category1, category2):
        return category1
    elif is_child_category(category2, category1):
        return category2
    else:
        return None


def join_deduced_types(deduced_type1, deduced_type2):
    if deduced_type1 == deduced_type2:
        return deduced_type1, None

    category = most_specific_category(deduced_type1.category,
                                      deduced_type2.category)
    if category is None:
        return None, "Incompatible types: <%s> and <%s>." % \
               (deduced_type1.category, deduced_type2.category)

    if deduced_type1.explicit != deduced_type2.explicit:
        if deduced_type1.explicit and not deduced_type2.explicit:
            return deduced_type1, None
        elif not deduced_type1.explicit and deduced_type2.explicit:
            return deduced_type2, None
        else:
            return None, "Conflicting types: <%s> and <%s>." % \
                   (deduced_type1.explicit, deduced_type2.explicit)

    if deduced_type1.specific != deduced_type2.specific:
        if deduced_type1.specific and not deduced_type2.specific:
            return deduced_type1, None
        elif not deduced_type1.specific and deduced_type2.specific:
            return deduced_type2, None
        else:
            return None, "Conflicting types: <%s> and <%s>." % \
                   (deduced_type1.specific, deduced_type2.specific)

    subtypes = None
    if deduced_type1.subtypes and deduced_type2.subtypes:
        if len(deduced_type1.subtypes) != len(deduced_type2.subtypes):
            return None, "Conflicting number of sub-element types."
        subtypes = []
        for st1, st2 in zip(deduced_type1.subtypes, deduced_type2.subtypes):
            st, error = join_deduced_types(st1, st2)
            if error:
                return None, error
            subtypes.append(st)
    else:
        subtypes = deduced_type1.subtypes or deduced_type2.subtypes
    return DeducedType(category, subtypes=subtypes), None


def get_int_type(s):
    if not s:
        return None
    n = len(s)
    i = 0
    if s[i] in "+-":
        i += 1
        if i == n:
            return None
    category = Category.NUMBER
    if s[i] == '0':
        i += 1
        if i == n:
            return DeducedType(category)
        category = Category.INTEGER
        if s[i] in "xXbB":
            i += 1
    elif not s[i].isdigit():
        return None
    while i != n and s[i] in LEGAL_INT_CHARS:
        i += 1
    if i == n:
        return DeducedType(category)
    suffix = s[i:].lower()
    if suffix in INT_SUFFIXES:
        return DeducedType(Category.INTEGER, INT_SUFFIXES[suffix])
    return None


def get_float_type(text):
    if not text:
        return None
    n = len(text)
    i = 0
    # Integer part
    if text[i] in "+-":
        i += 1
        if i == n:
            return None
    if not text[i].isdigit():
        return None
    while i != n and text[i] in LEGAL_FLOAT_CHARS:
        i += 1
    if i == n or text[i] not in ".eE":
        return None
    # Fraction part
    if text[i] == ".":
        i += 1
        while i != n and text[i] in LEGAL_FLOAT_CHARS:
            i += 1
        if i == n:
            return DeducedType(Category.REAL)
    # Exponent part
    if text[i] in "eE":
        i += 1
        if i == n:
            return None
        if text[i] in "+-":
            i += 1
            if i == n or not text[i].isdigit():
                return None
        while i != n and text[i] in LEGAL_FLOAT_CHARS:
            i += 1
        if i == n:
            return DeducedType(Category.REAL)
    suffix = text[i:].lower()
    if suffix in FLOAT_SUFFIXES:
        return DeducedType(Category.REAL, FLOAT_SUFFIXES[suffix])
    return None


def looks_like_type_name(text):
    for c in text:
        if not (c.isidentifier() or c in " *&<>:"):
            return False
    return True


def get_class_name_parenthesis(text):
    pos = text.find("(")
    if pos == -1 or 0 <= text.find("{") < pos:
        return None
    if pos == 0:
        end_pos = text.find(")")
        if end_pos not in (-1, len(text) - 1) and looks_like_type_name(text[pos + 1:end_pos]):
            return DeducedType(Category.ANY,
                               explicit=text[pos+1:end_pos].strip())
        else:
            return None
    return DeducedType(Category.ANY, explicit=text[:pos].strip())


def get_class_name_braces(text):
    pos = text.find("{")
    if pos <= 0 or 0 <= text.find("(") < pos:
        return None
    return DeducedType(Category.ANY, explicit=text[:pos].strip())


def find_end_of_whitespace(text, start_pos):
    for i in range(start_pos, len(text)):
        if not text[i].isspace():
            return i
    return -1


def get_tuple_parts(text):
    if not text or text[0] != "{" or text[-1] != "}":
        return None
    text = text[1:-1].strip()
    parts = []
    start_pos = 0
    while True:
        end_pos = parser_tools.find_char(text, ",", start_pos)
        if end_pos == -1:
            part = text[start_pos:].strip()
            if part:
                parts.append(part)
            break
        part = text[start_pos:end_pos].strip()
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
        common_type = join_deduced_types(common_type, deduced_types[i])[0]
        if not common_type:
            return False
    return common_type is not None


def get_value_type(text):
    if not text:
        return None
    if text in ("true", "false"):
        return DeducedType(Category.BOOL, specific="bool")
    elif len(text) > 1 and text[0] == "'" and text[-1] == "'":
        return DeducedType(Category.INTEGER, specific="char")
    elif len(text) > 1 and text[-1] == '"' \
            and (text[0] == '"' or text[:3] == 'u8"'):
        return DeducedType(Category.STRING)
    value_type = get_int_type(text)
    if value_type:
        return value_type
    value_type = get_float_type(text)
    if value_type:
        return value_type
    value_type = get_class_name_parenthesis(text)
    if value_type:
        return value_type
    value_type = get_class_name_braces(text)
    if value_type:
        return value_type
    if text.endswith("_MIN") or text.endswith("_MAX"):
        value_type = DeducedType(Category.NUMBER,
                                 specific=MINMAX_CONSTANTS.get(text[:-4]))
        if value_type:
            return value_type
    tuple_parts = get_tuple_parts(text)
    if tuple_parts is not None:
        types = [get_value_type(part) for part in tuple_parts]
        if None not in types:
            if has_common_type(types):
                return DeducedType(Category.COMPOSITE, subtypes=types)
            else:
                return DeducedType(Category.TUPLE, subtypes=types)
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
        result, error = join_deduced_types(result, value_types[i])
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
        return DeducedType(Category.COMPOSITE, subtypes=types)
    return DeducedType(Category.TUPLE, subtypes=types)


OPERATION_DEDUCED_TYPES = {
    "assign": DeducedType(Category.ANY),
    "append": DeducedType(Category.LIST,
                          subtypes=[DeducedType(Category.ANY)]),
    "extend": DeducedType(Category.LIST, subtypes=[DeducedType(Category.ANY)])
}


def deduce_type(member, syntax):
    if member.type:
        return None
    deduced_types = []
    if member.default:
        default_type = get_value_type(member.default)
        if default_type:
            default_type.source = "default"
            deduced_types.append(default_type)
    # for argument in member.arguments:
    #     if argument.valid_values:
    #         typ = deduce_type_from_values(argument.valid_values,
    #                                       syntax)
    #         if typ:
    #             typ.source = "values"
    #             deduced_types.append(typ)
    #     if argument.value:
    #         typ = get_value_type(argument.value, syntax)
    #         if typ:
    #             typ.source = "value"
    #             deduced_types.append(typ)
    #     if argument.operation:
    #         op = argument.operation
    #         if op in OPERATION_DEDUCED_TYPES:
    #             deduced_types.append(typ)

        # if "count" in argument.given_properties:
        #     pass
        # if "separator_count" in argument.given_properties:
        #     pass
    # Legal values
    # Metavar
    # Operation
    return None


def deduce_types(members, syntax):
    for member in members:
        deduce_type(member, syntax)
