# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-23.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import os.path
import re
from replace_variables import replace_variables
from deducedtype import add_all_type_names


class CodeProperties:
    def __init__(self):
        self.header_includes = None
        self.source_includes = None
        self.source_file_name = ""
        self.source_file_path = ""
        self.header_file_name = ""
        self.header_file_path = ""
        # self.class_name = None
        # self.parse_function_name = None
        # self.expose_helptext_functions = None
        # self.shortest_option_length = 0
        self.case_insensitive = True
        # self.abbreviated_options = True
        # self.non_short_options = True
        # self.special_options = True
        self.header_template = None
        self.source_template = None
        self.tracked_members = None
        self.namespace_start = None
        self.namespace_end = None
        self.namespace = None
        self.short_options = None
        self.options = None
        self.arguments = None
        self.equal_is_separator = False
        self.has_program_name = False
        self.default_line_width = 79
        self.max_line_width = 0
        self.min_line_width = 40
        self.dynamic_line_width = True
        self.has_option_values = False
        self.has_delimited_values = False
        self.parsed_type_names = None


def get_internal_variables(session):
    internals = {
        "HEADER_CONTENTS": "${HEADER_INCLUDES}\n\n${HEADER_CODE}",
        "SOURCE_CONTENTS": "${SOURCE_INCLUDES}\n\n${SOURCE_CODE}",
        "HEADER_INCLUDES": "[[[header_includes]]]",
        "SOURCE_INCLUDES": "[[[source_includes]]]",
        "HEADER_CODE": "[[[header_code]]]",
        "SOURCE_CODE": "[[[source_code]]]",
        "HEADER": "#pragma once\n${HEADER_CONTENTS}",
        "SOURCE": "${SOURCE_CONTENTS}",
        "PROGRAM": "[[[program_name]]]",
        "HEADER_NAME": "[[[header_file_name]]]",
        "SOURCE_NAME": "[[[source_file_name]]]",
        "OPTIONS": "[[[options]]]",
        "ARGUMENTS": "[[[arguments]]]",
        "ERROR": ""
    }
    for key in internals:
        if key in session.variables:
            internals[key] = session.variables[key]
    return internals


def get_argument_type_names(session):
    all_type_names = set()
    parsed_type_names = set()
    for arg in session.arguments:
        if arg.member:
            member_type = arg.member.member_type
            if arg.value is None and arg.operation != "none":
                add_all_type_names(parsed_type_names, member_type)
            add_all_type_names(all_type_names, member_type)
    return all_type_names, parsed_type_names


def _replace_variables(text, session, internal_variables):
    prev_text = None
    while text != prev_text:
        prev_text = text
        text = replace_variables(text, session, internal_variables)
    return text


def get_header_file_name(settings):
    return settings.file_name + settings.header_extension


def get_header_file_path(session):
    name = session.get_header_file_name()
    if session.settings.header_dir_name:
        name = os.path.join(session.settings.header_dir_name, name)
    return name


def get_source_file_name(session):
    name = session.settings.file_name + session.settings.source_extension
    if session.settings.source_dir_name:
        name = os.path.join(session.settings.source_dir_name,
                            session.settings.file_name)
    return name


INCLUDE_FILES_REXPS = {
    r"\btuple\b": "<tuple>",
    r"\bu?int(?:8|16|32|64)_t\b": "<cstdint>",
    r"\bvector\b": "<vector>",
    r"\bw?string\b": "<string>"
}


def get_header_includes(type_names):
    includes = {"<iosfwd>"}
    rexps = {k: re.compile(k) for k in INCLUDE_FILES_REXPS}
    for type_name in type_names:
        for rexp_key in rexps:
            if rexps[rexp_key].search(type_name):
                includes.add(INCLUDE_FILES_REXPS[rexp_key])
    return sorted(includes)


def get_counted_members(session):
    has_count = lambda a, b: a or b
    return [m for m in session.members
            if m.count and has_count(*m.count) and m.is_option()]


def get_argument_groups(session):
    short_options = {}
    options = {}
    arguments = []
    for arg in session.arguments:
        if not arg.flags:
            arguments.append(arg)
        else:
            for flag in arg.flags:
                if short_options is not None and len(flag) == 2 \
                        and flag[0] == '-':
                    short_options[flag] = arg
                else:
                    if short_options is not None and len(flag) > 2 \
                            and flag[0] == '-' and flag[1] != '-':
                        options.update(short_options)
                        short_options = None
                    options[flag] = arg
    return short_options, options, arguments


def can_use_equal_as_separator(session, code_properties):
    if not code_properties.options:
        return False
    if code_properties.short_options:
        def is_non_short_option(s): return len(s) != 2 or s[0] != "-"
    else:
        def is_non_short_option(s): return True
    has_option_arguments = False
    for arg in session.arguments:
        if arg.flags:
            for flag in arg.flags:
                if is_non_short_option(flag):
                    if "=" in flag:
                        return False
                    if arg.metavar:
                        has_option_arguments = True
    return has_option_arguments


def find_problematic_argument_callbacks(arguments):
    problematic_arguments = []
    known_index = True
    for i, arg in enumerate(arguments):
        count = arg.member.count
        if arg.callback:
            if not known_index:
                problematic_arguments.append(arg)
            elif count and count[0] != count[1] and i + 1 != len(arguments):
                problematic_arguments.append(arg)
        if count and count[0] != count[1]:
            known_index = False
    return problematic_arguments


def can_have_case_insensitive_flags(session):
    all_flags = {}
    result = True
    for argument in session.arguments:
        if argument.flags:
            flags = [(f.lower(), f) for f in argument.flags]
            for key, flag in flags:
                if key in all_flags:
                    session.logger.error("Cannot use case insensitive flags:"
                                         " %s and %s are ambiguous."
                                         % (all_flags[key], flag),
                                         argument=argument)
                    result = False
                for c in flag:
                    if ord(c) >= 128:
                        session.logger.error("Case-insensitive flags can not"
                                             " contain non-ASCII characters"
                                             " (the %s in %s)."
                                             % (c, flag), argument=argument)
                        break
            for key, flag in flags:
                all_flags[key] = flag
    return result


def determine_line_width_members(code_properties, settings):
    min_width = max(settings.min_line_width, 0)
    max_width = max(settings.max_line_width, 0)
    if min_width == max_width and min_width != 0:
        code_properties.dynamic_line_width = False
        code_properties.default_line_width = min_width
        code_properties.min_line_width = min_width
        code_properties.max_line_width = max_width
    else:
        default_width = max(settings.line_width, min_width, 40)
        code_properties.default_line_width = default_width
        code_properties.min_line_width = max(min_width, 40)
        if max_width != 0:
            code_properties.max_line_width = max(max_width, default_width)
        else:
            code_properties.max_line_width = int(1.25 * default_width + 0.5)


def has_non_string_type_names(type_names):
    return any(tn for tn in type_names if tn != "std::string"
               and not tn.startswith("std::vector")
               and not tn.startswith("std::pair"))


def make_code_properties(session):
    settings = session.settings
    result = CodeProperties()

    name = settings.file_name + settings.header_extension
    result.header_file_name = name
    if session.settings.header_dir_name:
        name = os.path.join(settings.header_dir_name, name)
    result.header_file_path = name

    name = settings.file_name + settings.header_extension
    result.header_file_name = name
    if session.settings.header_dir_name:
        name = os.path.join(settings.header_dir_name, name)
    result.header_file_path = name

    internal_variables = get_internal_variables(session)
    result.header_template = _replace_variables(
        internal_variables["HEADER"], session, internal_variables)
    result.source_template = _replace_variables(
        internal_variables["SOURCE"], session, internal_variables)

    all_type_names, parsed_type_names = get_argument_type_names(session)
    result.header_includes = get_header_includes(all_type_names)
    result.counted_members = get_counted_members(session)
    result.parsed_type_names = parsed_type_names

    result.source_includes = ['"%s"' % session.header_file_name()]

    for argument in session.arguments:
        if argument.separator:
            result.has_delimited_values = True
        if argument.flags and not argument.value:
            result.has_option_values = True

    if result.has_delimited_values:
        result.source_includes.append("<algorithm>")
    result.source_includes.extend(["<iostream>", "<string_view>"])
    if has_non_string_type_names(result.parsed_type_names):
        result.source_includes.append("<sstream>")
    result.source_includes.sort()

    if session.settings.namespace:
        ns = " { namespace ".join(session.settings.namespace)
        result.namespace_start = ["namespace " + ns, "{"]
        result.namespace_end = "}" * len(session.settings.namespace)
        result.namespace = "::".join(session.settings.namespace)

    groups = get_argument_groups(session)
    result.short_options = groups[0]
    result.options = groups[1]
    result.arguments = sorted(groups[2], key=lambda a: a.index)
    if result.options:
        result.equal_is_separator = can_use_equal_as_separator(session, result)

    determine_line_width_members(result, settings)

    if settings.immediate_callbacks:
        problematic_args = find_problematic_argument_callbacks(result.arguments)
        for arg in problematic_args:
            count = arg.member.count
            is_are = "s are" if count[1] != 1 else " is"
            session.logger.warn("It is necessary to read all the arguments and"
                                " options to determine which argument%s %s."
                                " The callback for this argument will therefore"
                                " see the final state of the options, not"
                                " necessarily the state when the argument"
                                " appears on the command line."
                                % (is_are, arg.metavar))

    if not settings.case_sensitive:
        result.case_insensitive = can_have_case_insensitive_flags(session)
    result.has_program_name = ("${PROGRAM}" in session.help_text
                               or "${PROGRAM}" in session.brief_help_text)
    return result
