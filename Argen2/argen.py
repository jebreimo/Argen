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

import argument
import member
from helpfileerror import HelpFileError
from sections import read_sections
from parse_help_text import parse_help_text
from replace_variables import replace_variables
from session import Session
import text_deductions
import member_name_deduction


def tokenize_setting(line):
    parts = line.split("=", 1)
    if len(parts) != 2:
        raise HelpFileError("Incorrect setting: %s" % line)
    leftSide = parts[0].split()
    if len(leftSide) == 1:
        name = leftSide[0]
        isSetting = True
    elif len(leftSide) == 2 and leftSide[0] == "set":
        name = leftSide[1]
        isSetting = False
    else:
        raise HelpFileError("Incorrect option name: %s" % parts[0])
    value = parts[1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return name, value, isSetting


def parse_settings(section, session):
    for i, line in enumerate(section.lines):
        try:
            line = replace_variables(line, session)
            line = line.strip()
            if line:
                name, value, isSetting = tokenize_setting(line)
                if not isSetting:
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


def parse_section(section, session):
    pass


def deduce_missing_option_values(options):
    pass


def deduce_missing_argument_values(arguments):
    pass


def create_arguments(arguments):
    pass


def create_options(options):
    pass


def create_argument_members(arguments):
    pass


def create_option_members(options):
    pass


def create_code_properties(arguments, options, members):
    pass


def create_code(codeProperties, arguments, options, members):
    pass


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


def update_properties(arg, props):
    for key in props:
        if key not in arg.properties:
            arg.properties[key] = props[key]


def make_deductions(session):
    generated_names = set()
    for arg in session.arguments:
        props = text_deductions.parse_argument_text(arg)
        update_properties(arg, props)
        props = dict(member_name=member_name_deduction.deduce_member_name(arg, generated_names))
        update_properties(arg, props)


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


def get_arguments_by_member_name(arguments):
    member_arguments = {}
    for arg in arguments:
        member_name = arg.properties["member_name"]
        if member_name not in member_arguments:
            member_arguments[member_name] = [arg]
        else:
            member_arguments[member_name].append(arg)
    return member_arguments


def make_members(member_arguments):
    members = []
    conflicts = []
    for member_name in member_arguments:
        args = member_arguments[member_name]
        member_props = {}
        if len(args) <= 1:
            for prop_name in argument.MEMBER_PROPERTIES:
                prev_arg = None
                prev_value = None
                for arg in args:
                    value = arg.properties.get(prop_name)
                    if value is not None:
                        if prev_arg and value != prev_value:
                            conflicts.append(dict(property=prop_name,
                                                  values=[value, prev_value],
                                                  arguments=[arg, prev_arg]))
                        else:
                            prev_arg, prev_value = arg, value
                if prev_value:
                    member_props[prop_name] = prev_value
        m = member.Member(member_name, member_props)
        members.append(m)
        for arg in args:
            arg.member = m
    return members, conflicts


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


# def make_members(member_arguments):
#     for member_name in member_arguments:


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
    conflicting_flags = find_duplicated_flags(session.arguments)
    if conflicting_flags:
        list_conflicting_flags(conflicting_flags)
        return 1
    member_arguments = get_arguments_by_member_name(session.arguments)
    members, conflicts = make_members(member_arguments)
    if conflicts:
        print_member_property_conflicts(conflicts)
        return 1

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
