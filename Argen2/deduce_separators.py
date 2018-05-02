# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


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


def deduce_separators(arguments):
    affected = []
    for arg in arguments:
        if arg.separator is not None or arg.separator_count == 0:
            continue
        if not arg.metavar:
            continue
        if arg.member and arg.member.type:
            continue
        if arg.operation and arg.operation not in ("set_value", "add_value", "add_values"):
            continue
        separator = find_metavar_separator(arg.metavar)
        if separator:
            arg.separator = separator
            affected.append(arg)
    return affected, None


def tokenize_metavar(text, separator):
    has_ellipsis = text.endswith("...")
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


# def parse_metavar(text,
#                   separator=None):
#     names, separator, has_ellipsis = tokenize_metavar(text, separator)
    # properties = {"type": determine_metavar_type(names, metavar_types),
    #               "meta_variable": text}
    # if separator:
    #     properties["separator"] = separator
    #     if has_ellipsis or len(names) == 1:
    #         properties["separator_count"] = "0..."
    #     else:
    #         properties["separator_count"] = str(len(names) - 1)
    # else:
    #     properties["separator_count"] = "0"
    # return properties


def deduce_separator_counts(arguments):
    for arg in arguments:
        if arg.separator_count is not None and arg.metavar and arg.separator:
            pass
