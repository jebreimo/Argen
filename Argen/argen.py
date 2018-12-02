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
from logger import Logger
from parse_help_text import parse_help_text
from replace_variables import replace_variables
from sections import read_sections
from session import Session
import deduce_arguments as da
import deduce_flags_and_metavars as dfam
import deduce_indices as di
import deduce_member_names as dmn
import deduce_member_types as dmt
import deduce_operations as do
import deduce_option_names as don
import deduce_separator_counts as ds
import deduce_special_options as dso
import deduce_valid_values as dvv
import deduce_value_types as dvt
import deduce_values as dv
import make_members as mm
import code_properties
import generate_header
import generate_source
import validate_arguments as va


def tokenize_setting(line, logger):
    parts = line.split("=", 1)
    if len(parts) != 2:
        logger.warn("Incorrect setting: %s" % line)
        return None, None, None
    left_side = parts[0].split()
    if len(left_side) == 1:
        name = left_side[0]
        is_setting = True
    elif len(left_side) == 2 and left_side[0] == "set":
        name = left_side[1]
        is_setting = False
    else:
        logger.warn("Incorrect setting name: %s" % parts[0])
        return None, None, None
    value = parts[1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return name, value, is_setting


def parse_settings(section, session):
    for i, line in enumerate(section.lines):
        try:
            session.logger.line_number = section.line_number + i + 1
            line = replace_variables(line, session)
            line = line.strip()
            if line:
                name, value, is_setting = tokenize_setting(line, session.logger)
                if name:
                    if not is_setting:
                        session.variables[name] = value
                    elif not session.set_setting(name, value):
                        session.logger.warn("Unknown setting: " + name)
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise


def parse_definition(section, session):
    lines = []
    for i, line in enumerate(section.lines):
        try:
            lines.append(replace_variables(line.rstrip(), session))
        except HelpFileError as ex:
            ex.file_name = section.file_name
            ex.line_number = section.line_number + i + 1
            raise
    for i in range(2):
        if len(lines) > 1 and not lines[-1]:
            del lines[-1]
    session.variables[section.parameter] = "\n".join(lines)


# def create_code_properties(arguments, options, members):
#     pass
#
#
# def create_code(codeProperties, arguments, options, members):
#     pass


def parse_sections(sections, session):
    for section in sections:
        session.begin_processing_file(section.file_name)
        if section.type == "text":
            session.help_text = parse_help_text(section, session)
        elif section.type == "set":
            parse_definition(section, session)
        elif section.type == "settings":
            parse_settings(section, session)
        elif section.type == "briefhelptext":
            session.brief_help_text = parse_help_text(section, session)
        session.end_processing_file()


def make_deductions(session):
    functions = [
        dfam.deduce_flags_and_metavars,
        don.deduce_option_names,
        dso.deduce_special_options,
        da.deduce_arguments,
        dmn.deduce_member_names,
        ds.deduce_separator_counts,
        mm.make_members,
        di.deduce_indices,
        dv.deduce_values,
        do.deduce_operations,
        dvt.deduce_value_types,
        dmt.deduce_member_types,
        dvv.deduce_valid_values,
        va.validate_arguments
    ]
    for func in functions:
        func(session)
        if session.has_errors():
            return


def process_files(file_names, session):
    sections = []
    for file_name in file_names:
        print(file_name)
        new_sections = read_sections(file_name, session.syntax)
        sections.extend(new_sections)
        parse_sections(new_sections, session)
    if session.has_errors():
        return False
    make_deductions(session)
    return not session.has_errors()


def print_result(result, session):
    print(result + " %d error(s) %d warning(s)"
          % (session.logger.counters[Logger.ERROR],
             session.logger.counters[Logger.WARNING]))


def make_argument_parser():
    ap = argparse.ArgumentParser(description='Generates source files for a C++ command line argument parser.')
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
    ap.add_argument("--debug", action="store_const", const=True,
                    default=False,
                    help="show debug messages")
    return ap


def main():
    args = make_argument_parser().parse_args()
    session = Session()
    syntax = session.syntax
    syntax.section_prefix = args.section_prefix
    session.logger.error_level = Logger.DEBUG if args.debug else Logger.INFO
    if not process_files(args.helpfiles, session):
        print_result("Failure.", session)
        return 1
    session.code_properties = code_properties.make_code_properties(session)
    # print(session.code_properties.source_template)
    file = open(session.header_file_path(), "w")
    file.write(generate_header.generate_header(session))
    file.close()
    file = open(session.source_file_path(), "w")
    file.write(generate_source.generate_source(session))
    file.close()
    # print(generate_source.generate_source(session))
    print_result("Success.", session)


    # for section in sections:
    #     print(section)
    # print("==== VARIABLES ====")
    # for variable in session.variables:
    #     print("%s=%s" % (variable, session.variables[variable]))
    # print("==== BRIEF_HELP_TEXT ====")
    # print(session.brief_help_text)
    # print("==== HELP_TEXT ====")
    # print(session.help_text)
    # print("==== ARGUMENTS ====")
    # for arg in session.arguments:
    #     print(arg)
    # for member in session.members:
    #     print(member)
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
