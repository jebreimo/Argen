# -*- coding: UTF-8 -*-
#############################################################################
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-12.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
#############################################################################
from helpfileerror import HelpFileError
from replace_variables import replace_variables
from argument import Argument, LEGAL_PROPERTIES, PROPERTY_ALIASES


def find_argument(text, start_pos, syntax):
    start = text.find(syntax.argument_start, start_pos)
    if start < 0:
        return None
    end = text.find(syntax.variable_end, start + len(syntax.argument_start))
    if end < 0:
        ex = HelpFileError("Argument has no end tag.")
        ex.line_number = text[:start].count("\n")
        raise ex
    return start, end + len(syntax.argument_end)


def parse_argument(text, syntax):
    parts = text.split(syntax.argument_separator)
    properties = {}
    for part in parts[1:]:
        subParts = part.split(":", 1)
        if len(subParts) != 2:
            raise HelpFileError('Invalid property: "%s".' % part)
        name = subParts[0].strip()
        value = subParts[1].strip()
        propertyName = name.lower()
        propertyName = PROPERTY_ALIASES.get(propertyName, propertyName)
        if propertyName not in LEGAL_PROPERTIES:
            raise HelpFileError('Unknown property: "%s".' % name)
        properties[propertyName] = value
    argument = Argument(parts[0], properties)
    return argument


def parse_help_text_impl(text, session):
    fromPos = 0
    outText = []
    syntax = session.syntax
    try:
        while True:
            argRange = find_argument(text, fromPos, syntax)
            if not argRange:
                outText.append(text[fromPos:])
                break
            toPos = argRange[0]
            outText.append(text[fromPos:toPos])
            argStart = toPos + len(syntax.argument_start)
            argEnd = argRange[1] - len(syntax.argument_end)
            argument = parse_argument(text[argStart:argEnd], syntax)
            outText.append(argument.raw_text)
            session.arguments.append(argument)
            fromPos = argRange[1]
        return "".join(outText)
    except HelpFileError as ex:
        ex.line_number = text[:toPos].count("\n")
        raise


def parse_help_text(section, session):
    lines = []
    for i, line in enumerate(section.lines):
        try:
            lines.append(replace_variables(line, session))
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise
    try:
        return parse_help_text_impl("".join(lines), session)
    except HelpFileError as ex:
        ex.file_name = section.file_name
        raise
