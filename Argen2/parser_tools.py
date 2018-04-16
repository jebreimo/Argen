# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-31.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def find_unescaped_char(s, char, start_pos):
    escape = False
    for i in range(start_pos, len(s)):
        if escape:
            escape = False
        elif s[i] == '\\':
            escape = True
        elif s[i] == char:
            return i
    return -1


def find_char(s, char, start_pos):
    i = start_pos
    while i < len(s):
        if s[i] == char:
            return i
        if s[i] == "(":
            i = find_char(s, ")", i + 1)
        elif s[i] == "{":
            i = find_char(s, "}", i + 1)
        elif s[i] == '"':
            i = find_unescaped_char(s, '"', i + 1)
        elif s[i] == "'":
            if i + 2 < len(s) and s[i + 2] == "'":
                i += 2
            elif i + 3 < len(s) and s[i] == "\\":
                i = find_unescaped_char(s, "'", i + 1)
        if i == -1:
            break
        i += 1
    return -1


def matches_string(text, start_pos, string):
    if len(text) - start_pos < len(string):
        return False
    for i in range(len(string)):
        if text[start_pos + i] != string[i]:
            return False
    return True


def find_next_separator(text, start_pos, separator):
    while True:
        start_pos = find_char(text, separator[0], start_pos)
        if start_pos < 0:
            return -1
        if matches_string(text, start_pos, separator):
            if not matches_string(text, start_pos + len(separator), separator):
                return start_pos
            start_pos += 2 * len(separator)
        else:
            start_pos += 1


def split_text(text, separator):
    parts = []
    pos = 0
    while True:
        next_pos = find_next_separator(text, pos, separator)
        if next_pos < 0:
            parts.append(text[pos:])
            return parts
        parts.append(text[pos:next_pos])
        pos = next_pos + len(separator)


def split_and_unescape_text(text, separator):
    parts = split_text(text, separator)
    escaped_separator = separator + separator
    if text.find(escaped_separator):
        for i in range(len(parts)):
            parts[i] = parts[i].replace(escaped_separator, separator)
    return parts
