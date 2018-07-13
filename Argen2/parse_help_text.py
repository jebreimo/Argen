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


def parse_help_text_impl(text, session, line_number):
    out_text = []
    argument_definitions = []
    syntax = session.syntax
    groups = []
    current_group = (None, None)
    state = "START_OF_LINE"
    whitespace = ""
    try:
        for token, start, end in find_tokens(text, syntax):
            if token == TEXT_TOKEN:
                token_text = text[start:end]
                if token_text[-1] == "\n":
                    if state == "AFTER_ARGUMENT" and not token_text.isspace():
                        if whitespace != current_group[0]:
                            current_group = (whitespace,
                                             [(len(out_text), line_number)])
                            groups.append(current_group)
                        else:
                            current_group[1].append((len(out_text),
                                                     line_number))
                    line_number += 1
                    state = "START_OF_LINE"
                    whitespace = ""
                elif state == "START_OF_LINE" and token_text.isspace():
                    whitespace = token_text
                else:
                    state = "CANNOT_FORMAT"
                    whitespace = None
                out_text.append(token_text)
            else:
                arg_start = start + len(syntax.argument_start)
                arg_end = end - len(syntax.argument_end)
                token_text = text[arg_start:arg_end]
                line_number += token_text.count("\n")
                session.logger.line_number = line_number
                arg_text, props = parse_argument(token_text, session)
                argument_definitions.append((arg_text, props, line_number))
                out_text.append(arg_text)
                if state == "START_OF_LINE" and "\n" not in arg_text:
                    state = "AFTER_ARGUMENT"
                else:
                    state = "CANNOT_FORMAT"
        return argument_definitions, out_text, groups
    except HelpFileError as ex:
        if ex.line_number == -1:
            ex.line_number = line_number
        raise


def is_proper_group(whitespace_prefix, locations):
    if len(locations) > 4 or (whitespace_prefix and len(locations) > 2):
        return True
    prev_line_number = -99
    for index, line_number in locations:
        if line_number == prev_line_number + 1:
            return True
        prev_line_number = line_number
    return False


def calculate_group_width(text, whitespace, locations):
    widths = []
    for index, line_number in locations:
        widths.append(len(text[index - 1]))
    widths.sort()
    if len(widths) <= 3:
        typical_width = widths[0]
    elif len(whitespace) + widths[-1] < 24:
        typical_width = widths[-1]
    else:
        n = len(widths)
        typical_width = widths[min((n * 9) // 10, n - 2)]
    if widths[-1] < typical_width + 10:
        return widths[-1]
    else:
        return typical_width


def format_arguments(text, groups):
    for whitespace, locations in groups:
        if is_proper_group(whitespace, locations):
            width = calculate_group_width(text, whitespace, locations)
            for index, line_number in locations:
                if len(text[index - 1]) < width:
                    text[index - 1] = "%*s" % (-width, text[index - 1])


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
        arg_defs, text, groups = parse_help_text_impl("".join(lines), session,
                                                      section.line_number)
        if session.settings.auto_format:
            format_arguments(text, groups)
        text = "".join(text)
        for arg_text, props, line_number in arg_defs:
            argument = make_argument(arg_text, props, session,
                                     section.file_name, line_number)
            session.arguments.append(argument)
        return text
    except HelpFileError as ex:
        ex.file_name = section.file_name
        raise


if __name__ == "__main__":
    import session

    _text = """
    {{-f,     --foo}}  Some text.
    {{-h}}  Show help.
    {{        --konge}}  Helt konge!
    {{-q NUM, --quantity=NUM}}  Antall.
    """

    _text2 = """
    {{-h}}  Show help.
    {{-q NUM, --quantity=NUM}}  Antall.
    """

    def test(txt):
        s = session.Session()
        args, text, groups = parse_help_text_impl(txt, s, 1)
        print(args)
        print(groups)
        format_arguments(text, groups)
        print("".join(text))

    test(_text)
