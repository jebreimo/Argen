# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-01.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools


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


def find_final_ellipsis(text):
    start = parser_tools.find_last_not_of(text, ".")
    if len(text) - start + 1 >= 2:
        return start + 1
    return -1


def tokenize_metavar(text, separator):
    final_char = find_final_ellipsis(text)
    if final_char == -1:
        end = len(text)
    elif final_char != 0 and text[final_char - 1] == separator:
        end = final_char - 1
    else:
        end = final_char
    tokens = parser_tools.split_text(text[:end], separator)
    if final_char != -1:
        tokens.append("...")
    return tokens


def find_end_of_argument_token(text, start):
    end = len(text)
    if start >= end:
        return end
    if text[start].isspace():
        i = start + 1
        while i < end and text[i].isspace():
            i += 1
        return i
    if text[start] in "<[]>":
        return start + 1
    i = start
    while i < end:
        if text[i].isspace() or text[i] in "<[]>":
            return i
        i += 1
    return i


def is_ellipsis(text):
    return len(text) >= 2 and parser_tools.find_first_not_of(text, ".") == -1


class NormalizeArgumentStateMachine:
    def __init__(self):
        self.state = ""
        self.tokens = []
        self.current_token = []
        self.space = ""
        self.ellipsis = None


    def _add_ellipsis(self):
        if self.ellipsis:
            self.current_token.extend(self.ellipsis)
            self.ellipsis = None

    def _add_space(self):
        self._add_ellipsis()
        if self.space:
            self.current_token.append(self.space)
            self.space = ""

    def _clear_space(self):
        self.ellipsis = None
        self.space = ""

    def _complete_current_token(self):
        self.tokens.append("".join(self.current_token))
        self.current_token = []
        self.state = ""

    def add_token(self, token):
        if token.isspace():
            if self.state:
                self.space = token
        elif token == "<":
            if not self.state:
                self.current_token.append(token)
                self.state = "<"
            else:
                self._add_space()
                self.current_token.append(token)
        elif token == ">":
            if self.state == "<":
                self._clear_space()
                self.current_token.append(token)
                self._complete_current_token()
            elif self.state:
                self._add_space()
                self.current_token.append(token)
            else:
                self.current_token.extend(("<", token))
                self.state = "t"
        elif token == "[":
            if not self.state:
                self.current_token.append(token)
                self.state = "["
            elif self.space and self.state == "t":
                self.current_token.append(">")
                self._complete_current_token()
                self._clear_space()
                self.current_token = [token]
                self.state = "["
            else:
                self._add_space()
                self.current_token.append(token)
        elif token == "]":
            if self.state == "[":
                self.current_token.append(token)
                self._complete_current_token()
                if self.ellipsis:
                    self.tokens.append("...")
                self._clear_space()
            elif self.state:
                self._add_space()
                self.current_token.append(token)
            else:
                self.current_token.extend(("<", token))
                self.state = "t"
        elif is_ellipsis(token):
            if self.state == "[":
                self._add_ellipsis()
                if self.space:
                    self.ellipsis = (self.space, token)
                else:
                    self.ellipsis = (token,)
            elif self.state == "<":
                self.current_token.append(token)
            elif self.state == "t":
                self._clear_space()
                self.current_token.append(">")
                self._complete_current_token()
                self.tokens.append("...")
                self.state = ""
            else:
                self.tokens.append("...")
        else:
            if not self.state:
                self.state = "t"
                self.current_token = ["<", token]
            else:
                self._add_space()
                self.current_token.append(token)

    def get_tokens(self):
        if self.state:
            if self.state in "<t" and self.current_token[-1] != ">":
                self.current_token.append(">")
            elif self.state == "[" and self.current_token[-1] != "]":
                self.current_token.append("]")
            self._complete_current_token()
            if self.ellipsis:
                self.tokens.append("...")
                self.ellipsis = None
        return self.tokens


def normalize_argument_metavar(text):
    if not text:
        return []
    sm = NormalizeArgumentStateMachine()
    i = 0
    while True:
        j = find_end_of_argument_token(text, i)
        if j == i:
            break
        sm.add_token(text[i:j])
        i = j
    return sm.get_tokens()


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
    affected = []
    for arg in arguments:
        if arg.separator_count is None and arg.metavar and arg.separator:
            pass
