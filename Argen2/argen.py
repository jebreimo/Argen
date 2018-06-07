#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-22.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argparse
import sys

from helpfileerror import HelpFileError
from sections import read_sections
from parse_help_text import parse_help_text
from replace_variables import replace_variables
from session import Session
import deduce_arguments as da
import deduce_flags_and_metavars as dfam
import deduce_help_option as dho
import deduce_indices as di
import deduce_member_names as dmn
import deduce_separator_counts as ds
import deduce_value_types as dvt
import make_members as mm


def tokenize_setting(line):
    parts = line.split("=", 1)
    if len(parts) != 2:
        raise HelpFileError("Incorrect setting: %s" % line)
    left_side = parts[0].split()
    if len(left_side) == 1:
        name = left_side[0]
        is_setting = True
    elif len(left_side) == 2 and left_side[0] == "set":
        name = left_side[1]
        is_setting = False
    else:
        raise HelpFileError("Incorrect option name: %s" % parts[0])
    value = parts[1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return name, value, is_setting


def parse_settings(section, session):
    for i, line in enumerate(section.lines):
        try:
            line = replace_variables(line, session)
            line = line.strip()
            if line:
                name, value, is_setting = tokenize_setting(line)
                if not is_setting:
                    session.variables[name] = value
                else:
                    session.set_setting(name, value)
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise


def parse_definition(section, session):
    lines = []
    for i, line in enumerate(section.lines):
        try:
            lines.append(replace_variables(line, session))
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise
    session.variables[section.parameter] = "".join(lines)


# def parse_section(section, session):
#     pass
#
#
# def deduce_missing_option_values(options):
#     pass
#
#
# def deduce_missing_argument_values(arguments):
#     pass
#
#
# def create_arguments(arguments):
#     pass
#
#
# def create_options(options):
#     pass
#
#
# def create_argument_members(arguments):
#     pass
#
#
# def create_option_members(options):
#     pass
#
#
# def create_code_properties(arguments, options, members):
#     pass
#
#
# def create_code(codeProperties, arguments, options, members):
#     pass


def parse_sections(sections, session):
    for section in sections:
        if section.type == "text":
            session.help_text = parse_help_text(section, session)
        elif section.type == "set":
            parse_definition(section, session)
        elif section.type == "settings":
            parse_settings(section, session)
        elif section.type == "errortext":
            session.error_text = parse_help_text(section, session)


class HelpText:
    def __init__(self):
        pass


def make_argument_parser():
    ap = argparse.ArgumentParser(description='Generates a C++ argument parser.')
    ap.add_argument("helpfiles", metavar="text file", action="append",
                    help="text files containing the help text")
    ap.add_argument("-i", "--indent", metavar="N", type=int, default=-1,
                    help="indentation width when option help text is word-wrapped")
    ap.add_argument("-d", "--define", metavar="NAME=VALUE", action="append",
                    help="define a value that can be used in the helpfiles")
    ap.add_argument("--no-pragma-once", action="store_const", const=True,
                    default=False,
                    help="don't insert a pragma once at the beginning of the header file")
    ap.add_argument("--section-prefix", default="$$$",
                    help="set the section prefix that are used to define sections in helpfiles")
    return ap


def update_properties(existing_properties, new_properties):
    for key in new_properties:
        if key not in existing_properties:
            existing_properties[key] = new_properties[key]


def make_deductions(session):
    affected, conflicts = dfam.deduce_flags_and_metavars(session.arguments)
    if conflicts:
        pass
    affected = da.deduce_arguments(session.arguments)
    affected, conflicts = dmn.deduce_member_names(session.arguments)
    if conflicts:
        pass
    affected = ds.deduce_separator_counts(session.arguments)
    session.members, conflicts = mm.make_members(session.arguments)
    if conflicts:
        pass
    affected, conflicts = di.deduce_indices(session.arguments)
    if conflicts:
        pass
    affected, conflicts = dho.deduce_help_option(session.arguments)
    if conflicts:
        pass
    affected, conflict = dvt.deduce_value_types(session.members)
    if conflicts:
        pass


def find_duplicated_flags(args):
    visited_flags = {}
    for arg in args:
        flags = arg.properties.get("flags")
        if flags:
            for flag in flags.split():
                if flag not in visited_flags:
                    visited_flags[flag] = {arg}
                else:
                    visited_flags[flag].add(arg)
    conflicts = {}
    for flag in visited_flags:
        if len(visited_flags[flag]) != 1:
            conflicts[flag] = visited_flags[flag]
    return conflicts


def list_conflicting_flags(conflicting_flags):
    for flag in conflicting_flags:
        print("Error: the flag '%s' is defined by multiple options:")
        for a in conflicting_flags[flag]:
            print("  Line %d: '%s'" % (a.line_number, a.properties["flags"]))


def print_error(file_name, line_number, message):
    if file_name and line_number:
        print(f"{file_name}:{line_number}: {message}", file=sys.stderr)
    elif file_name:
        print(f"{file_name}: {message}", file=sys.stderr)
    elif line_number:
        print(f"line {line_number}: {message}", file=sys.stderr)
    else:
        print(message, file=sys.stderr)


def print_member_property_conflicts(conflicts):
    for conflict in conflicts:
        arg1, arg2 = conflict["arguments"]
        name = conflict["property"]
        value1, value2 = conflict["values"]
        if arg2.file_name:
            other_pos = "%s:%d" % (arg2.file_name, arg2.line_number)
        else:
            other_pos = "line %d" % arg2.line_number
        print_error(arg1.file_name, arg1.line_number,
                    f"The value of property {name} ({value1}) conflicts with"
                    + f"the value given at {other_pos} ({value2}).")


def main():
    args = make_argument_parser().parse_args()
    session = Session()
    syntax = session.syntax
    syntax.section_prefix = args.section_prefix
    sections = []
    for file_name in args.helpfiles:
        print(file_name)
        new_sections = read_sections(file_name, syntax)
        sections.extend(new_sections)
        parse_sections(new_sections, session)
    make_deductions(session)
    # conflicting_flags = find_duplicated_flags(session.arguments)
    # if conflicting_flags:
    #     list_conflicting_flags(conflicting_flags)
    #     return 1
    # member_arguments = get_arguments_by_member_name(session.arguments)
    # members, conflicts = make_members(member_arguments)
    # if conflicts:
    #     print_member_property_conflicts(conflicts)
    #     return 1

    for section in sections:
        print(section)
    for variable in session.variables:
        print(variable)
        print(session.variables[variable])
    print("ERROR_TEXT")
    print(session.error_text)
    print("HELP_TEXT")
    print(session.help_text)
    print("ARGUMENTS")
    for arg in session.arguments:
        print(arg)
    for member in session.members:
        print(member)
    return 0


sys.exit(main())

## IndentationWidth=N
## PragmaOnce=BOOL
## Abbreviations=BOOL
## SectionPrefix=STR # Can't set SectionPrefix
## ArgumentPrefix=STR
## ArgumentSuffix=STR
## ArgumentSeparator=CHAR
## VariablePrefix=STR
## VariableSuffix=STR
## ClassName=STR
## FileName=STR
## HeaderExtension=STR
## SourceExtension=STR
## Namespace=STR
## FunctionName=STR
## LineWidth=N
## Test=BOOL
