# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def _make_name(raw_name):
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


def _get_longest_flag(flags):
    max_length = 0
    longest = ""
    for flag in flags:
        n = _find_first_identifier_char(flag)
        length = len(flag) - n if n != -1 else 0
        if length > max_length or not longest:
            max_length = length
            longest = flag
    return longest


def _make_unique_name(name, taken_names):
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


def make_member_name_from_flags(flags, taken_names):
    longest_flag = _get_longest_flag(flags)
    name = _make_name(longest_flag)
    prev_arg = taken_names.get(name)
    if prev_arg and (not prev_arg.flags or name == "_"):
        name = _make_unique_name(name, taken_names)
    return name


def make_member_name_from_metavar(metavar, taken_names):
    return _make_unique_name(_make_name(metavar), taken_names)


def deduce_member_names(session):
    unnamed = []
    taken_names = {}
    for arg in session.arguments:
        if arg.member_name:
            prev_arg = taken_names.get(arg.member_name)
            if not prev_arg:
                taken_names[arg.member_name] = arg
            elif arg.is_option() != prev_arg.is_option():
                session.logger.error("Options and arguments cannot share the "
                                     "same member name (%s)." % arg.member_name,
                                     argument=arg)
                session.logger.info("The conflicting argument or option "
                                    "is defined here.", argument=prev_arg)
        elif arg.operation != "none":
            unnamed.append(arg)
    for arg in unnamed:
        if arg.flags:
            name = make_member_name_from_flags(arg.flags, taken_names)
        else:
            name = make_member_name_from_metavar(arg.metavar, taken_names)
        arg.member_name = name
        session.logger.debug("Deduced member name: " + name, argument=arg)
        if name not in taken_names:
            taken_names[name] = arg
