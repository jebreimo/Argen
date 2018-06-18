# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-15.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def find_end_of_flag(text, start):
    for i in range(start, len(text)):
        if text[i] in "\x09 ,":
            return i
        if text[i] == "=" and i - start >= 2 and text[i - 1] != "-":
            return i
    return len(text)


def is_flag(text, start):
    n = len(text) - start
    return (n >= 2 and text[start] in "-/"
            and (n != 2 or text[start + 1] not in "\x09 ,")) \
        or text == "-"


def find_end_of_separator(text, start):
    if start != len(text) and text[start] == "=":
        return start + 1
    for i in range(start, len(text)):
        if text[i] not in "\x09 ,":
            return i
    return len(text)


def find_next_separator(text, start):
    for i in range(start, len(text)):
        if text[i] in "\x09 ,":
            return i
    return len(text)


def find_end_of_argument(text, start):
    i = start
    n = len(text)
    while i < n:
        end = i
        i = find_end_of_separator(text, i)
        if is_flag(text, i):
            return end
        i = find_next_separator(text, i)
    return len(text)


def get_flags_and_arguments(text):
    text = text.strip()
    flags = []
    if not is_flag(text, 0):
        return flags, text
    argument = None
    i = 0
    n = len(text)
    while i < n:
        if is_flag(text, i):
            j = find_end_of_flag(text, i)
            flags.append(text[i:j])
        else:
            j = find_end_of_argument(text, i)
            if argument is None:
                argument = text[i:j]
        i = find_end_of_separator(text, j)
    return flags, argument


def deduce_flags_and_metavars(session):
    undetermined = []
    for arg in session.arguments:
        if arg.metavar == "":
            arg.metavar = None
        if arg.flags is None and arg.metavar is None:
            arg.flags, arg.metavar = get_flags_and_arguments(arg.text)
            if arg.flags or arg.metavar:
                session.logger.debug("Deduced flags: %s and variable: %s"
                                     % (arg.flags, arg.metavar), argument=arg)
            else:
                session.logger.warn("Unable to determine flags or variable"
                                    " for argument.", argument=arg)
                undetermined.append(arg)
    if undetermined:
        taken_metavars = {a.metavar for a in session.arguments if a.metavar}
        i = 0
        for arg in undetermined:
            metavar = "<unnamed>" if i == 0 else "<unnamed_%d>" % i
            i += 1
            while metavar in taken_metavars:
                metavar = "<unnamed_%d>" % i
                i += 1
            arg.metavar = metavar
            taken_metavars.add(metavar)
            session.logger.debug("Deduced variable: %s" % arg.metavar,
                                 argument=arg)
