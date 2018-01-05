# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


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
        elif (c == "_" and not chars) or (chars and chars[-1] != "_"):
            chars.append("_")
    if len(chars) > 1 and chars[-1] == "_" and raw_name[-1] != "_":
        chars.pop()
    return "".join(chars)


# TODO look for duplicate flags

def find_first_identifier_char(s):
    for i, c in enumerate(s):
        if c.isalnum() or c == "_":
            return i
    return -1


def get_longest_flag(flags):
    maxLength = 0
    longest = ""
    for flag in flags.split():
        n = find_first_identifier_char(flag)
        length = len(flag) - n if n != -1 else 0
        if length > maxLength or not longest:
            maxLength = length
            longest = flag
    return longest


def deduce_member_name(arg, generated_names):
    """
    :param arg: Argument
    :param generated_names: set
    :return: string
    """
    assert isinstance(generated_names, type(set()))
    if "member_name" in arg.given_properties:
        return arg.properties["member_name"]
    if arg.properties.get("flags"):
        name = make_member_name(get_longest_flag(arg.properties["flags"]))
    elif arg.properties.get("meta_variable"):
        name = make_member_name(arg.properties["meta_variable"])
    else:
        name = None
    if not name:
        name = "unnamed"
    if name in generated_names:
        i = 1
        nname = "%s_%d" % (name, i)
        while nname in generated_names:
            i += 1
            nname = "%s_%d" % (name, i)
        name = nname
    generated_names.add(name)
    return name
