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
        elif s[i] == "[":
            i = find_char(s, "]", i + 1)
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


def find_first_not_of(text, char, start=0):
    if not text:
        return -1
    for i in range(start, len(text)):
        if text[i] != char:
            return i
    return -1


def find_last_not_of(text, char):
    if not text:
        return -1
    for i in range(len(text) - 1, -1, -1):
        if text[i] != char:
            break
    else:
        i = -1
    return i


def find_next_ellipsis(text, start=0):
    if not text:
        return -1, -1
    while True:
        start = find_char(text, ".", start)
        if start == -1:
            return -1, -1
        end = find_first_not_of(text, ".", start + 1)
        if end == -1:
            end = len(text)
        if end - start >= 2:
            return start, end
        start = end


def is_ellipsis(text):
    return len(text) >= 2 and find_first_not_of(text, ".") == -1


def split_range(text):
    start, end = find_next_ellipsis(text)
    if start != -1:
        return text[:start], text[end:]
    else:
        return None


def get_int_range(text):
    if not text:
        return None
    parts = split_range(text)
    if parts:
        a, b = parts[0].strip(), parts[1].strip()
        if a or b:
            return (int(a, 0) if a else 0), (int(b, 0) if b else None)
        else:
            return 0, None
    else:
        a = int(text.strip(), 0)
        return a, a


def find_all(text, substr):
    result = []
    i = 0
    while True:
        i = text.find(substr, i)
        if i == -1:
            return result
        result.append(i)
        i = i + len(substr)


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
