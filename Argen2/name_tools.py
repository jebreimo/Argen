# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def make_name(raw_name):
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
        elif (c == "_" and not chars) or (chars and chars[-1] != "_"):
            chars.append("_")
    if len(chars) > 1 and chars[-1] == "_" and raw_name[-1] != "_":
        chars.pop()
    if not chars:
        return "_"
    return "".join(chars)


def _find_first_identifier_char(s):
    for i, c in enumerate(s):
        if c.isalnum() or c == "_":
            return i
    return -1


def get_longest_flag(flags):
    max_length = 0
    longest = ""
    for flag in flags:
        n = _find_first_identifier_char(flag)
        length = len(flag) - n if n != -1 else 0
        if length > max_length or not longest:
            max_length = length
            longest = flag
    return longest


def make_unique_name(name, taken_names):
    if name not in taken_names:
        return name
    if name[-1] != "_":
        name += "_"
    i = 2
    while True:
        unique_name = "%s%d" % (name, i)
        if unique_name not in taken_names:
            return unique_name
        i += 1
