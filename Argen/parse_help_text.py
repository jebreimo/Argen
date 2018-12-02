# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-12.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import re
from helpfileerror import HelpFileError
from replace_variables import replace_variables
from argument import make_argument
from properties import LEGAL_PROPERTIES, PROPERTY_ALIASES
import parser_tools


# Token types or state machine "events"
TEXT_TOKEN = 0
ARGUMENT_TOKEN = 1


# State machine states
AT_START_OF_LINE = 0
AFTER_INDENTATION = 1
AFTER_TEXT = 2
AFTER_FIRST_ARGUMENT = 3


# Look for the first character that is neither a whitespace nor bullet point
# character.
INDENTATION_REGEX = re.compile(r"^[\t ]*(?:[-*0-9] *)?")


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
        end_pos = parser_tools.find_next_separator(
            text, arg_pos + len(syntax.argument_start), syntax.argument_end)
        if end_pos == -1:
            ex = HelpFileError("Argument has no end tag.")
            raise ex
        start_pos = end_pos + len(syntax.argument_end)
        yield ARGUMENT_TOKEN, arg_pos, start_pos


def parse_argument(text, session):
    parts = parser_tools.split_and_unescape_text(
        text, session.syntax.argument_separator)
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


class HelpTextTokenHandlers:
    def __init__(self, text, first_line_number, session):
        self.state = AT_START_OF_LINE
        self.arg_groups = []
        self.arg_group = (None, None)
        self.session = session
        self.input_text = text
        self.output_text = []
        self.line_number = first_line_number
        self.arg_defs = []
        self.whitespace = None
        self.word_wrap = session.settings.word_wrap

    def on_text_at_start_of_line(self, event, start, end):
        token = self.input_text[start:end]
        match = INDENTATION_REGEX.search(token)
        newline = token[-1] == "\n"
        if not match:
            self.output_text.append(token)
            return AT_START_OF_LINE if newline else AFTER_TEXT
        pos = match.span()[1]
        if self.word_wrap and pos:
            self.output_text.append(token[:pos])
            self.output_text.append(self.session.syntax.alignment_char)
            self.output_text.append(token[pos:])
        else:
            self.output_text.append(token)
        if newline:
            return AT_START_OF_LINE
        elif pos == len(token):
            self.whitespace = token
            return AFTER_INDENTATION
        else:
            return AFTER_TEXT

    def on_text_after_argument(self, event, start, end):
        token = self.input_text[start:end]
        if token[-1] != "\n":
            self.output_text.append(token)
            return AFTER_TEXT
        if token.isspace():
            self.output_text.append(token)
            return AT_START_OF_LINE

        if self.whitespace != self.arg_group[0]:
            self.arg_group = (self.whitespace,
                              [(len(self.output_text) - 1,
                                self.line_number)])
            self.arg_groups.append(self.arg_group)
        else:
            self.arg_group[1].append((len(self.output_text) - 1,
                                      self.line_number))
        if self.word_wrap:
            pos = parser_tools.find_first_not_of(token, " \t\r\n")
            if pos:
                self.output_text.append(token[:pos])
                self.output_text.append(self.session.syntax.alignment_char)
                self.output_text.append(token[pos:])
            else:
                self.output_text.append(self.session.syntax.alignment_char),
                self.output_text.append(token)
        return AT_START_OF_LINE

    def on_text(self, event, start, end):
        self.output_text.append(self.input_text[start:end])
        return AT_START_OF_LINE if self.input_text[end-1] else AFTER_TEXT

    def __on_argument(self, event, start, end):
        syntax = self.session.syntax
        arg_start = start + len(syntax.argument_start)
        arg_end = end - len(syntax.argument_end)
        token = self.input_text[arg_start:arg_end]
        arg_text, props = parse_argument(token, self.session)
        self.arg_defs.append((arg_text, props, self.line_number))
        self.output_text.append(arg_text)
        return arg_text

    def on_first_argument(self, event, start, end):
        arg_text = self.__on_argument(event, start, end)
        if event[0] != AFTER_INDENTATION:
            self.whitespace = ""
        if "\n" not in arg_text:
            return AFTER_FIRST_ARGUMENT
        elif arg_text[-1] == "\n":
            return AT_START_OF_LINE
        else:
            return AFTER_TEXT

    def on_argument(self, event, start, end):
        arg_text = self.__on_argument(event, start, end)
        if arg_text or arg_text[-1] == "\n":
            return AT_START_OF_LINE
        else:
            return AFTER_TEXT


class StateMachine:
    def __init__(self, initial_state, context):
        self.context = context
        self.event_handlers = {}
        self.default_event_handler = StateMachine.ignore_event
        self.state = initial_state

    def set_default_event_handler(self, func):
        self.default_event_handler = func

    def add_event_handler(self, state, event, func):
        self.event_handlers[(state, event)] = func

    def handle_event(self, event, *args, **kwargs):
        handler = self.event_handlers.get((self.state, event),
                                           self.default_event_handler)
        self.state = handler(self.context, (self.state, event), *args, **kwargs)

    @staticmethod
    def ignore_event(context, event, *args, **kwargs):
        return event[0]


def parse_help_text_impl(text, session, line_number):
    handlers = HelpTextTokenHandlers(text, line_number, session)
    sm = StateMachine(AT_START_OF_LINE, handlers)
    sm.add_event_handler(AT_START_OF_LINE, TEXT_TOKEN,
                         HelpTextTokenHandlers.on_text_at_start_of_line)
    sm.add_event_handler(AT_START_OF_LINE, ARGUMENT_TOKEN,
                         HelpTextTokenHandlers.on_first_argument)
    sm.add_event_handler(AFTER_TEXT, TEXT_TOKEN,
                         HelpTextTokenHandlers.on_text)
    sm.add_event_handler(AFTER_TEXT, ARGUMENT_TOKEN,
                         HelpTextTokenHandlers.on_argument)
    sm.add_event_handler(AFTER_INDENTATION, TEXT_TOKEN,
                         HelpTextTokenHandlers.on_text)
    sm.add_event_handler(AFTER_INDENTATION, ARGUMENT_TOKEN,
                         HelpTextTokenHandlers.on_first_argument)
    sm.add_event_handler(AFTER_FIRST_ARGUMENT, TEXT_TOKEN,
                         HelpTextTokenHandlers.on_text_after_argument)
    sm.add_event_handler(AFTER_FIRST_ARGUMENT, ARGUMENT_TOKEN,
                         HelpTextTokenHandlers.on_argument)
    try:
        for token_type, start, end in find_tokens(text, session.syntax):
            sm.handle_event(token_type, start, end)
            handlers.line_number += text.count("\n", start, end)
        return handlers.arg_defs, handlers.output_text, handlers.arg_groups
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
        widths.append(len(text[index]))
    widths.sort()
    if len(widths) <= 3:
        width = widths[0]
    elif len(whitespace) + widths[-1] < 32:
        return widths[-1]
    else:
        n = len(widths)
        n_75 = (n * 75) // 100
        typical_width = widths[n_75]
        width = typical_width
        for i in range(n_75 + 1, n):
            if widths[i] < typical_width + 10:
                width = widths[i]
    return min(36 - len(whitespace), width)


def format_arguments(text, groups):
    for whitespace, locations in groups:
        if is_proper_group(whitespace, locations):
            width = calculate_group_width(text, whitespace, locations)
            for index, line_number in locations:
                if len(text[index]) < width:
                    text[index] = "%*s" % (-width, text[index])


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
