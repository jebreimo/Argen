# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-17.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools as pt


def tokenize_metavar(s):
    i = 0
    n = len(s)
    parts = []
    while i < n:
        if s[i] in "<>[]":
            parts.append(s[i])
            i += 1
        elif s[i] in " \t":
            j = pt.find_first_not_of(s, " \t", i + 1)
            parts.append(s[i:j])
            i = j
        else:
            j = pt.find_first_of(s, "<>[] \t", i + 1)
            k = pt.find_first_of(s, ".", i, j)
            while k < j:
                m = pt.find_first_not_of(s, ".", k + 1, j)
                if m - k >= 2:
                    if k != i:
                        parts.append(s[i:k])
                    parts.append(s[k:m])
                    i = m
                    break
                k = pt.find_first_of(s, ".", m + 1, j)
            else:
                parts.append(s[i:j])
                i = j
    return parts


class Parser:
    def __init__(self):
        self._current_entry = []
        self._result = []
        self._whitespace = None
        self._ellipsis = None
        self._scopes = []

    def _add_ellipsis(self, ignoreWhitespaceOnly=False):
        if self._ellipsis:
            if self._whitespace:
                if self._current_entry:
                    self._current_entry.append(self._whitespace)
                self._whitespace = None
            self._current_entry.append(self._ellipsis)
            self._ellipsis = None
        elif self._whitespace and not ignoreWhitespaceOnly:
            if self._current_entry:
                self._current_entry.append(self._whitespace)
            self._whitespace = None

    def process_space(self, token):
        self._add_ellipsis()
        self._whitespace = token

    def process_start_bracket(self, token):
        self._add_ellipsis()
        self._scopes.append(token)
        self._current_entry.append(token)

    def process_end_square(self, token):
        pop = self._scopes and self._scopes[-1] == "["
        if pop:
            self._scopes.pop()
        if pop and not self._scopes:
            self._current_entry.append(token)
            self._result.append("".join(self._current_entry))
            if self._ellipsis:
                self._result.append("...")
                self._ellipsis = None
            self._whitespace = None
            self._current_entry = []
        else:
            self._add_ellipsis()
            self._current_entry.append(token)

    def process_end_tag(self, token):
        pop = self._scopes and self._scopes[-1] == "<"
        if pop:
            self._scopes.pop()
        if pop and not self._scopes:
            self._add_ellipsis()
            self._current_entry.append(token)
            self._result.append("".join(self._current_entry))
            self._current_entry = []
        else:
            self._add_ellipsis()
            self._current_entry.append(token)

    def process_ellipsis(self, token):
        if not self._whitespace or len(self._scopes) > 1:
            self._current_entry.append(token)
        elif len(self._scopes) == 1:
            self._add_ellipsis(True)
            self._ellipsis = token
        else:
            if self._current_entry:
                self._result.append("".join(self._current_entry))
                self._current_entry = []
            self._result.append("...")
            self._whitespace = None

    def process_text(self, token):
        self._add_ellipsis()
        self._current_entry.append(token)

    def process_token(self, token):
        if token.isspace():
            self.process_space(token)
        elif token == "[" or token == "<":
            self.process_start_bracket(token)
        elif token == "]":
            self.process_end_square(token)
        elif token == ">":
            self.process_end_tag(token)
        elif pt.is_ellipsis(token):
            self.process_ellipsis(token)
        else:
            self.process_text(token)

    def get_result(self):
        self._add_ellipsis(True)
        if self._current_entry:
            self._result.append("".join(self._current_entry))
        result = self._result
        self._ellipsis = None
        self._whitespace = None
        self._result = []
        return result


def split_metavar(metavar):
    parser = Parser()
    tokens = tokenize_metavar(metavar)
    for token in tokens:
        parser.process_token(token)
    return parser.get_result()
