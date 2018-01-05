# -*- coding: UTF-8 -*-
# ============================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ============================================================================


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
        properties = {}
    else:
        properties = parse_flags(argument.text)
    return properties


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
