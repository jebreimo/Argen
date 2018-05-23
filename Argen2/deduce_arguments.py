# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-05-21.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parser_tools


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


class ArgumentPartAssembler:
    def __init__(self):
        self.state = ""
        self.parts = []
        self.current_part = []
        self.space = ""
        self.ellipsis = None

    def _add_ellipsis(self):
        if self.ellipsis:
            self.current_part.extend(self.ellipsis)
            self.ellipsis = None

    def _add_space(self):
        self._add_ellipsis()
        if self.space:
            self.current_part.append(self.space)
            self.space = ""

    def _append_token(self, subtoken):
        self._add_space()
        self.current_part.append(subtoken)

    def _end_part(self):
        if self.state in "<t" and self.current_part[-1] != ">":
            self.current_part.append(">")
        elif self.state == "[" and self.current_part[-1] != "]":
            self.current_part.append("]")
        self.parts.append("".join(self.current_part))
        if self.ellipsis:
            self.parts.append("...")
            self.ellipsis = None
        self.space = ""
        self.current_part = []
        self.state = ""

    def _begin_part(self, state, token):
        self.state = state
        self.current_part = [token] if state != "t" else ["<", token]

    def add_token(self, token):
        if token.isspace():
            if self.state:
                self.space = token
        elif token == "<":
            if not self.state:
                self._begin_part("<", token)
            else:
                self._append_token(token)
        elif token == ">":
            if self.state == "<":
                self._end_part()
            elif self.state:
                self._append_token(token)
            else:
                self._begin_part("t", token)
        elif token == "[":
            if not self.state:
                self._begin_part("[", token)
            elif self.space and self.state == "t":
                self._end_part()
                self._begin_part("[", token)
            else:
                self._append_token(token)
        elif token == "]":
            if self.state == "[":
                self._end_part()
            elif self.state:
                self._append_token(token)
            else:
                self._begin_part("t", token)
        elif parser_tools.is_ellipsis(token):
            if self.state == "[":
                self._add_ellipsis()
                if self.space:
                    self.ellipsis = (self.space, token)
                else:
                    self.ellipsis = (token,)
            elif self.state == "<":
                self._append_token(token)
            elif self.state == "t":
                self._end_part()
                self.parts.append("...")
            else:
                self.parts.append("...")
        else:
            if not self.state:
                self._begin_part("t", token)
            else:
                self._append_token(token)

    def get_parts(self):
        if self.state:
            self._end_part()
        return self.parts


def split_metavar(text):
    if not text:
        return []
    assembler = ArgumentPartAssembler()
    start = 0
    while True:
        end = find_end_of_argument_token(text, start)
        if end == start:
            break
        assembler.add_token(text[start:end])
        start = end
    return assembler.get_parts()


def deduce_arguments(args):
    affected = []
    for arg in args:
        if arg.metavar:
            if not arg.flags:
                arg.arguments = split_metavar(arg.metavar)
                affected.append(arg)
            else:
                if arg.metavar[0] != "<" and arg.metavar[-1] != ">":
                    fmt = "<%s>"
                elif arg.metavar[0] != "<":
                    fmt = "<%s"
                elif arg.metavar[-1] != ">":
                    fmt = "%s>"
                else:
                    fmt = "%s"
                arg.arguments = [fmt % arg.metavar]
                affected.append(arg)
    return affected
