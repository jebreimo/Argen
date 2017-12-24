#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#############################################################################
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-22.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
#############################################################################
import argparse
import sys

import argument
from helpfileerror import HelpFileError
from sections import read_sections
from parse_help_text import parse_help_text
from replace_variables import replace_variables
from session import Session


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


def main():
    args = make_argument_parser().parse_args()
    session = Session()
    syntax = session.syntax
    syntax.section_prefix = args.section_prefix
    sections = []
    for file_name in args.helpfiles:
        print(file_name)
        newSections = read_sections(file_name, syntax)
        sections.extend(newSections)
        parse_sections(newSections, session)
    for arg in session.arguments:
        deducedProps = argument.parse_argument_text(arg)
        arg.deduce_properties = deducedProps
        for key in deducedProps:
            if key not in arg.properties:
                arg.properties[key] = deducedProps[key]
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
