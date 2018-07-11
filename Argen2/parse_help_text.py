# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-12.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
from helpfileerror import HelpFileError
from replace_variables import replace_variables
from argument import make_argument
from properties import LEGAL_PROPERTIES, PROPERTY_ALIASES
from parser_tools import split_and_unescape_text, find_next_separator


TEXT_TOKEN = 0
ARGUMENT_TOKEN = 1


def find_tokens(text, syntax):
    start_pos = 0
    while True:
        arg_pos = text.find(syntax.argument_start, start_pos)
        while start_pos != arg_pos:
            n_pos = text.find("\n", start_pos, arg_pos)
            if n_pos != -1:
                yield TEXT_TOKEN, start_pos, n_pos + 1
                start_pos = n_pos + 1
            else:
                yield TEXT_TOKEN, start_pos, arg_pos if arg_pos != -1 else len(text)
                start_pos = arg_pos
        if start_pos == -1:
            return
        end_pos = find_next_separator(text,
                                      arg_pos + len(syntax.argument_start),
                                      syntax.argument_end)
        if end_pos == -1:
            ex = HelpFileError("Argument has no end tag.")
            raise ex
        start_pos = end_pos + len(syntax.argument_end)
        yield ARGUMENT_TOKEN, arg_pos, start_pos


def parse_argument(text, session):
    parts = split_and_unescape_text(text, session.syntax.argument_separator)
    properties = {}
    for part in parts[1:]:
        subparts = part.split(":", 1)
        if len(subparts) != 2:
            session.logger.warn('Ignoring property without ":": "%s".' % part)
            continue
        name = subparts[0].strip()
        value = subparts[1].strip()
        property_name = name.lower()
        property_name = PROPERTY_ALIASES.get(property_name, property_name)
        if property_name not in LEGAL_PROPERTIES:
            session.logger.warn('Ignoring unknown property: "%s".' % name)
        else:
            properties[property_name] = value
    return parts[0], properties


def parse_help_text_impl(text, session, file_name, line_number):
    out_text = []
    syntax = session.syntax
    try:
        for token, start, end in find_tokens(text, syntax):
            if token == TEXT_TOKEN:
                token_text = text[start:end]
                out_text.append(token_text)
                if token_text[-1] == "\n":
                    line_number += 1
            else:
                arg_start = start + len(syntax.argument_start)
                arg_end = end - len(syntax.argument_end)
                token_text = text[arg_start:arg_end]
                line_number += token_text.count("\n")
                session.logger.line_number = line_number
                arg_text, props = parse_argument(token_text, session)
                argument = make_argument(arg_text, props, session,
                                         file_name, line_number)
                out_text.append(arg_text)
                session.arguments.append(argument)
        return "".join(out_text)
    except HelpFileError as ex:
        if ex.line_number == -1:
            ex.line_number = line_number
        raise


def parse_help_text(section, session):
    lines = []
    for i, line in enumerate(section.lines):
        try:
            session.logger.line_number = section.line_number + i
            lines.append(replace_variables(line, session))
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise
    try:
        return parse_help_text_impl("".join(lines), session,
                                    section.file_name, section.line_number)
    except HelpFileError as ex:
        ex.file_name = section.file_name
        raise
