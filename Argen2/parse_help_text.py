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


def find_argument(text, start_pos, syntax):
    start = text.find(syntax.argument_start, start_pos)
    if start < 0:
        return None
    end = find_next_separator(text, start + len(syntax.argument_start),
                              syntax.argument_end)
    if end < 0:
        ex = HelpFileError("Argument has no end tag.")
        ex.line_number = text[:start].count("\n") + 1
        raise ex
    return start, end + len(syntax.argument_end)


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
    from_pos = to_pos = 0
    out_text = []
    syntax = session.syntax
    try:
        while True:
            arg_range = find_argument(text, from_pos, syntax)
            if not arg_range:
                out_text.append(text[from_pos:])
                break
            to_pos = arg_range[0]
            out_text.append(text[from_pos:to_pos])
            arg_start = to_pos + len(syntax.argument_start)
            arg_end = arg_range[1] - len(syntax.argument_end)
            line_number += text.count("\n", from_pos, arg_range[0])
            session.logger.line_number = line_number
            arg_text, props = parse_argument(text[arg_start:arg_end], session)
            argument = make_argument(arg_text, props, session,
                                     file_name, line_number)
            line_number += text.count("\n", arg_range[0], arg_range[1])
            out_text.append(arg_text)
            session.arguments.append(argument)
            from_pos = arg_range[1]
        return "".join(out_text)
    except HelpFileError as ex:
        if ex.line_number == -1:
            ex.line_number = text[:to_pos].count("\n") + 1
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
