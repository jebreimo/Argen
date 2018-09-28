# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def find_first_unique_char_case_sensitive(str1, str2):
    max_index = min(len(str1), len(str2))
    for i in range(0, max_index):
        if str1[i] != str2[i]:
            return i + 1
    return max_index


def find_first_unique_char_case_insensitive(str1, str2):
    max_index = min(len(str1), len(str2))
    for i in range(0, max_index):
        if str1[i].upper() != str2[i].upper():
            return i + 1
    return max_index


def find_shortest_unique_prefixes(strings_and_data, case_insensitive=False):
    if case_insensitive:
        find_first_unique_char = find_first_unique_char_case_insensitive
    else:
        find_first_unique_char = find_first_unique_char_case_sensitive
    prefixes = []
    for string in strings_and_data:
        text = string[0]
        if not prefixes:
            index = 1
            prefixes.append((text[:index], text[index:], text))
        else:
            index = find_first_unique_char(prefixes[-1][0], text)
            if index == len(prefixes[-1][0]):
                prev_text = prefixes[-1][2]
                index = find_first_unique_char(prev_text, text)
                prefixes[-1] = prev_text[:index], prev_text[index:], prev_text
                if index == len(prev_text):
                    index += 1
            prefixes.append((text[:index], text[index:], text))
    return [(p[0], p[1], s[1]) for p, s in zip(prefixes, strings_and_data)]
