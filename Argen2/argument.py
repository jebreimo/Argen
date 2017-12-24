# -*- coding: UTF-8 -*-
#############################################################################
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
#############################################################################
from helpfileerror import HelpFileError


ARGUMENT_PROPERTIES = {"action", "argument_type", "callback", "count", "flags",
                       "index", "member_name", "meta_variable", "separator",
                       "separator_count", "text", "value"}

MEMBER_PROPERTIES = {"default", "member_action", "member_callback", "values",
                     "type"}

_REVERSE_PROPERTY_ALIASES = {
    "action": ["act"],
    "argument": ["arg"],
    "argument_type": ["argtype", "arg_type", "argumenttype"],
    "callback": ["call"],
    "member_name": ["mem", "member", "membername"],
    "meta_variable": ["metavar", "metavariable"],
    "separator": ["sep"],
    "separator_count": ["sepcount", "sep_count", "separatorcount"],
    "value": ["val"],
    "member_action": ["memact", "mem_act", "memaction", "mem_action",
                      "memberaction"],
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


LEGAL_ARGUMENT_TYPES = {
    "final",
    "help",
    "info",
    "list",
    "multivalue",
    "multivaluelist"
    "value",
    "callback"
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


def find_commas(text):
    commas = []
    pos = 0
    while True:
        pos = text.find(",", pos)
        if pos == -1:
            break
        if pos == len(text) - 1 or text[pos + 1] in " \t-/":
            commas.append(pos)
        pos += 1
    return commas


def split_on_commas(text):
    pos = 0
    parts = []
    for commaPos in find_commas(text):
        if pos != commaPos:
            parts.append(text[pos:commaPos])
        pos = commaPos + 1
    if pos != len(text):
        parts.append(text[pos:])
    return parts


def split_on_equal(text):
    if text.startswith("--"):
        prefix_len = 2
    elif text.startswith("/"):
        prefix_len = 1
    else:
        prefix_len = 0
    if prefix_len:
        pos = text.find("=")
        if pos not in (-1, prefix_len, len(text) - 1):
            return [text[:pos], text[pos + 1:]]
    return [text]


def split_arguments(text):
    result = []
    parts = [t.strip() for t in split_on_commas(text)]
    if len(parts) != 1:
        for part in parts:
            subparts = part.split(None, 1)
            if len(subparts) == 1:
                subparts = split_on_equal(part)
            result.append((subparts[0],
                           subparts[1] if len(subparts) == 2 else None))
    else:
        flag = None
        for part in text.split():
            if not flag:
                subparts = split_on_equal(part)
                if len(subparts) == 2:
                    result.append(tuple(subparts))
                else:
                    flag = part
            elif part[0] in "-/":
                result.append((flag, None))
                flag = part
            else:
                result.append((flag, part))
                flag = None
        if flag:
            result.append((flag, None))
    return result


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

def parse_flags(text):
    flags = []
    properties = {}
    for flag, metavar in split_arguments(text):
        flags.append(flag)
        if metavar and len(metavar) > len(properties.get("meta_variable", "")):
            properties["meta_variable"] = metavar
    if not properties:
        properties = {}
    properties["flags"] = " ".join(flags)
    return properties


def deduce_flag_properties(argument):
    if "flags" in argument.given_properties:
        if "meta_variable" in argument.given_properties:
            properties = parse_metavar(argument.given_properties)
        else:
            properties = {}
    else:
        properties = parse_flags(argument.text)
    return properties


def make_member_name(raw_name):
    if not raw_name:
        return "_"
    chars = []
    if raw_name[0].isdigit():
        chars.append("_")
    for c in raw_name:
        if c.isdigit():
            chars.append(c)
        elif c.isalpha():
            if len(chars) != 1 or chars[0] != "_" or raw_name[0] == "_":
                chars.append(c)
            else:
                chars[0] = c
        elif not chars or chars[-1] != "_":
            chars.append("_")
    if len(chars) > 1 and chars[-1] == "_" and raw_name[-1] != "_":
        chars.pop()
    return "".join(chars)


def get_argument_metavar_and_count(text):
    min_count = "1"
    max_count = ""
    if text[0] in "<[" and text.endswith("..."):
        max_count = "..."
        text = text[:-3].strip()
    if text[0] == "[" and text[-1] == "]":
        text = text[1:-1]
        min_count = "0"
    elif text[0] == "<" and text[-1] == ">":
        text = text[1:-1]
    parts = text.split()
    if len(parts) > 1:
        if parts[-1] == "...":
            del parts[-1]
            max_count = "..."
        elif parts[-1].endswith("..."):
            max_count = "..."
    count = min_count + max_count
    if len(parts) == 1:
        return parts[0], count
    else:
        return "", count


def parse_argument(text):
    if not text:
        return {"flags": ""}
    metavar, count = get_argument_metavar_and_count(text)
    properties = {"flags": "", "count": count}
    if metavar:
        properties["meta_variable"] = metavar
    return properties


def deduce_argument_properties(argument):
    return parse_argument(argument.text)


def looks_like_flags(text):
    return text and ((text[0] in "-/") or ("=" in text))


def parse_argument_text(argument):
    if argument.given_properties.get("flags", ".") \
            or looks_like_flags(argument.text):
        return deduce_flag_properties(argument)
    else:
        return deduce_argument_properties(argument)
