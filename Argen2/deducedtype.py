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
    VALUE = "value"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    REAL = "real"
    BOOL = "bool"


KNOWN_TYPE_CATEGORIES = {
    "std::string": Category.STRING,
    "int": Category.INTEGER,
    "long": Category.INTEGER,
    "double": Category.REAL,
    "bool": Category.BOOL
}


CATEGORY_TYPES = {
    Category.ANY: "std::string",
    Category.COMPOSITE: "std::tuple",
    Category.LIST: "std::vector",
    Category.VALUE: "std::string",
    Category.STRING: "std::string",
    Category.NUMBER: "int",
    Category.INTEGER: "int",
    Category.REAL: "double",
    Category.BOOL: "bool"
}


PARENT_CATEGORIES = {
    Category.ANY: None,
    Category.COMPOSITE: Category.ANY,
    Category.LIST: Category.COMPOSITE,
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


class DeducedType:
    def __init__(self, category=None, specific=None,
                 explicit=None, subtypes=None, source=None,
                 prototype=None):
        self.category = category
        self.specific = specific
        self.explicit = explicit
        self.subtypes = subtypes
        self.source = source
        if prototype:
            self.category = self.category or prototype.category
            self.specific = self.specific or prototype.specific
            self.explicit = self.explicit or prototype.explicit
            self.subtypes = self.subtypes or prototype.subtypes
            self.source = self.source or prototype.source
        if self.category is None:
            self.category = Category.ANY

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


def join_deduced_types(deduced_type1, deduced_type2, logger):
    if not deduced_type1 or not deduced_type2:
        logger.error("Deduced type cannot be None.")
        return None

    if deduced_type1 == deduced_type2:
        return DeducedType(prototype=deduced_type1)

    category = most_specific_category(deduced_type1.category,
                                      deduced_type2.category)
    if category is None:
        logger.warn("Incompatible types: %s and %s."
                       % (deduced_type1, deduced_type2))
        return None

    if deduced_type1.explicit != deduced_type2.explicit:
        if deduced_type1.explicit and not deduced_type2.explicit:
            return DeducedType(category, prototype=deduced_type1)
        elif not deduced_type1.explicit and deduced_type2.explicit:
            return DeducedType(category, prototype=deduced_type2)
        else:
            logger.warn("Conflicting types: %s and %s."
                        % (deduced_type1, deduced_type2))
            return None

    if deduced_type1.specific != deduced_type2.specific:
        if deduced_type1.specific and not deduced_type2.specific:
            return DeducedType(category, prototype=deduced_type1)
        elif not deduced_type1.specific and deduced_type2.specific:
            return DeducedType(category, prototype=deduced_type2)
        else:
            logger.warn("Conflicting types: %s and %s."
                        % (deduced_type1, deduced_type2))
            return None
    subtypes = None
    source = None
    if deduced_type1.subtypes and deduced_type2.subtypes:
        if len(deduced_type1.subtypes) == len(deduced_type2.subtypes):
            subtypes = []
            for st1, st2 in zip(deduced_type1.subtypes, deduced_type2.subtypes):
                st = join_deduced_types(st1, st2, logger)
                if not st:
                    return None
                if not source and st1.category != st2.category:
                    if st.category == st1.category:
                        source = deduced_type1.source
                    else:
                        source = deduced_type2.source
                subtypes.append(st)
        else:
            common_type1 = join_list_of_deduced_types(deduced_type1.subtypes, logger)
            common_type2 = join_list_of_deduced_types(deduced_type2.subtypes, logger)
            common_type = join_deduced_types(common_type1, common_type2, logger)
            if common_type:
                subtypes = [common_type]
                category = Category.LIST
                if not common_type2:
                    source = deduced_type1.source
                elif not common_type1:
                    source = deduced_type2.source
        if not subtypes:
            logger.warn("Conflicting lists of subtypes: %s and %s."
                        % (deduced_type1, deduced_type2))
            return None
    elif deduced_type1.subtypes:
        subtypes = deduced_type1.subtypes
        source = deduced_type1.source
    elif deduced_type2.subtypes:
        subtypes = deduced_type2.subtypes
        source = deduced_type2.source
    if not source:
        if category == deduced_type1.category:
            source = deduced_type1.source
        else:
            source = deduced_type2.source
    return DeducedType(category, subtypes=subtypes, source=source)


def join_list_of_deduced_types(deduced_types, logger):
    if not deduced_types:
        logger.error("Deduced_types cannot be None or empty.")
        return None
    common_type = deduced_types[0]
    for i in range(1, len(deduced_types)):
        common_type = join_deduced_types(common_type, deduced_types[i], logger)
        if not common_type:
            return None
    return common_type


def is_undetermined(deduced_type):
    if not deduced_type:
        return False
    if deduced_type.category != Category.ANY:
        return False
    if deduced_type.explicit or deduced_type.specific:
        return False
    return True


def is_list(deduced_type):
    if not deduced_type:
        return False
    if deduced_type.category == Category.LIST:
        return True
    if deduced_type.category == Category.COMPOSITE \
            and join_list_of_deduced_types(deduced_type.subtypes):
        return True
    if deduced_type.category == Category.ANY \
            and (deduced_type.explicit or deduced_type.specific):
        return True
    return False


def _get_int_type(s):
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


def _get_float_type(text):
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


def _looks_like_type_name(text):
    for c in text:
        if not (c.isidentifier() or c in " *&<>:"):
            return False
    return True


def _get_class_name_parenthesis(text):
    pos = text.find("(")
    if pos == -1 or 0 <= text.find("{") < pos:
        return None
    if pos == 0:
        end_pos = text.find(")")
        if end_pos not in (-1, len(text) - 1) and _looks_like_type_name(text[pos + 1:end_pos]):
            return DeducedType(explicit=text[pos+1:end_pos].strip())
        else:
            return None
    return DeducedType(explicit=text[:pos].strip())


def _get_class_name_braces(text):
    pos = text.find("{")
    if pos <= 0 or 0 <= text.find("(") < pos:
        return None
    return DeducedType(explicit=text[:pos].strip())


def _find_end_of_whitespace(text, start_pos):
    for i in range(start_pos, len(text)):
        if not text[i].isspace():
            return i
    return -1


def _get_tuple_parts(text):
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
    common_type, error = join_list_of_deduced_types(deduced_types)
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
    value_type = _get_int_type(text)
    if value_type:
        return value_type
    value_type = _get_float_type(text)
    if value_type:
        return value_type
    value_type = _get_class_name_parenthesis(text)
    if value_type:
        return value_type
    value_type = _get_class_name_braces(text)
    if value_type:
        return value_type
    if text.endswith("_MIN") or text.endswith("_MAX"):
        value_type = DeducedType(Category.NUMBER,
                                 specific=MINMAX_CONSTANTS.get(text[:-4]))
        if value_type:
            return value_type
    tuple_parts = _get_tuple_parts(text)
    if tuple_parts is not None:
        types = [get_value_type(part) for part in tuple_parts]
        if None not in types:
            return DeducedType(Category.COMPOSITE, subtypes=types)
    return None
