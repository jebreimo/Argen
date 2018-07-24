# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-20.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def find_shortest_string(strings):
    if not strings:
        return None
    min_len = len(strings[0])
    min_str = strings[0]
    for i in range(1, len(strings)):
        if len(strings[i]) < min_len:
            min_str = strings[i]
            min_len = len(min_str)
    return min_str


def is_mandatory(option):
    if not option.member or not option.member.count:
        return False
    return option.member.count[0] > 0 and len(option.member.arguments) == 1


def format_option(arg, session):
    if not arg.flags:
        return None
    flag = find_shortest_string(arg.flags)
    var = arg.metavar or ""
    cp = session.code_properties
    if not var:
        sep = ""
    elif not cp.equal_is_separator:
        sep = " "
    elif cp.short_options and len(flag) == 2 and flag[0] == "-":
        sep = " "
    else:
        sep = "="
    if is_mandatory(arg):
        format_string = "<%s%s%s>"
    else:
        format_string = "[%s%s%s]"
    return format_string % (flag, sep, var)


def generate_options_text(session):
    optional = []
    mandatory = []
    for arg in session.arguments:
        string = format_option(arg, session)
        if string:
            string = string.replace(" ", session.syntax.non_breaking_space)
            if string[0] == "[":
                optional.append(string)
            else:
                mandatory.append(string)
    return " ".join((" ".join(optional), " ".join(mandatory)))


def generate_arguments_text(session):
    arguments = [a for a in session.arguments if not a.flags and a.metavar]
    arguments.sort(key=lambda a: a.index)
    return " ".join(a.metavar.replace(" ", session.syntax.non_breaking_space)
                    for a in arguments)


ESCAPED_CHARS = {
    '"': '\\"',
    '\t': '\\t',
    '\r': '\\r',
    '\\': '\\\\'
}


def escape_text(txt):
    parts = None
    prev_i = 0
    for i, ch in enumerate(txt):
        if ch in ESCAPED_CHARS or ord(ch) < 32:
            if not parts:
                parts = []
            if i != prev_i:
                parts.append(txt[prev_i:i])
            if ch in ESCAPED_CHARS:
                parts.append(ESCAPED_CHARS[ch])
            else:
                parts.append("\\%03o" % ord(ch))
            prev_i = i + 1

    if not parts:
        return txt
    if prev_i != i:
        parts.append(txt[prev_i:])
    return "".join(parts)


def find_all(text, pattern, start_pos=0):
    positions = []
    pos = start_pos
    while True:
        pos = text.find(pattern, pos)
        if pos == -1:
            return positions
        positions.append(pos)
        pos += len(pattern)

MAX_LINE_WIDTH = 72

def split_text(text, max_line_width=MAX_LINE_WIDTH):
    lines = []
    max_tail_length = (max_line_width + 2) // 3
    prev_pos = 0
    while len(text) - prev_pos > max_line_width:
        max_pos = prev_pos + max_line_width + 1
        next_pos = text.rfind(" ", prev_pos, max_pos)
        if next_pos == -1 or max_pos - next_pos > max_tail_length:
            next_pos = text.find(" ", max_pos)
            if next_pos == -1:
                break
        lines.append(text[prev_pos:next_pos])
        prev_pos = next_pos
    lines.append(text[prev_pos:])
    return lines


def generate_help_text_string(text, session):
    options_text = generate_options_text(session)
    arguments_text = generate_arguments_text(session)
    lines = []
    if "\r" in text:
        if "\n" in text:
            text = text.replace("\r", "")
        else:
            text = text.replace("\r", "\n")
    for line in text.split("\n"):
        opt_pos = find_all(line, "${OPTIONS}")
        arg_pos = find_all(line, "${ARGUMENTS}")
        if opt_pos or arg_pos:
            matches = []
            matches.extend((n, n + len("${OPTIONS}"), options_text)
                           for n in opt_pos)
            matches.extend((n, n + len("${ARGUMENTS}"), arguments_text)
                           for n in arg_pos)
            pos = 0
            new_line = []
            for f, e, txt in matches:
                new_line.append(line[pos:f])
                if pos == 0:
                    new_line.append(session.syntax.alignment_char)
                new_line.append(txt)
                pos = e
            new_line.append(line[pos:])
            line = "".join(new_line)
        line = escape_text(line) + "\\n"
        if len(line) <= MAX_LINE_WIDTH:
            lines.append('"%s"' % line)
        else:
            lines.extend('"%s"' % l for l in split_text(line))
    if lines[-1] == '"\\n"':
        del lines[-1]
    return lines
