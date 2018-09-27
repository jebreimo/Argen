# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import datetime
import os

import properties
import logger
from helpfileerror import HelpFileError
from helpfilesyntax import HelpFileSyntax


def make_default_variables():
    today = datetime.date.today()
    variables = dict(YEAR=str(today.year),
                     MONTH="%02d" % today.month,
                     DAY="%02d" % today.day,
                     SYNOPSIS="${PROGRAM} ${OPTIONS} ${ARGUMENTS}")
    variables.update(dict(os.environ))
    return variables


def parse_bool(value):
    value = value.lower()
    if value in ("0", "false"):
        return False
    if value in ("1", "true"):
        return True
    raise HelpFileError("Invalid boolean value: %s" % value)


class Settings:
    def __init__(self):
        self.indentation = -1
        self.allow_abbreviations = True
        self.use_pragma_once = True
        self.class_name = "Arguments"
        self.file_name = "ParseArguments"
        self.header_extension = ".h"
        self.source_extension = ".cpp"
        self.dir_name = None
        self.header_dir_name = None
        self.source_dir_name = None
        self.header_only = False
        self.namespace = None
        self.function_name = "parse_arguments"
        self.add_test = False
        self.metavar_types = dict(properties.DEFAULT_METAVAR_TYPES)
        self.detect_separators = False
        self.case_sensitive = True
        self.auto_format = True
        self.word_wrap = True
        self.immediate_callbacks = False
        self.line_width = 79
        self.max_line_width = 0
        self.min_line_width = 0


class Session:
    def __init__(self):
        self.settings = Settings()
        self.variables = make_default_variables()
        self.syntax = HelpFileSyntax()
        self.help_text = "usage: ${SYNOPSIS}\n"
        self.error_text = "usage: ${SYNOPSIS}\n\n${ERROR}\n"
        self.metavar_types = dict(properties.DEFAULT_METAVAR_TYPES)
        self.arguments = []
        self.members = []
        self.code_properties = None
        self.logger = logger.Logger()

    def begin_processing_file(self, file_name):
        self.logger.file_name = file_name
        self.logger.line_number = None

    def end_processing_file(self):
        self.logger.file_name = None
        self.logger.line_number = None

    def has_errors(self):
        return self.logger.counters[logger.Logger.ERROR] != 0

    def header_file_name(self):
        return self.settings.file_name + self.settings.header_extension

    def source_file_name(self):
        return self.settings.file_name + self.settings.source_extension

    def header_file_path(self):
        file_name = self.header_file_name()
        if self.settings.header_dir_name:
            return os.path.join(self.settings.header_dir_name, file_name)
        else:
            return file_name

    def source_file_path(self):
        file_name = self.source_file_name()
        if self.settings.source_dir_name:
            return os.path.join(self.settings.source_dir_name, file_name)
        else:
            return file_name

    def set_setting(self, name, value):
        if name == "ArgumentPrefix":
            self.syntax.argument_start = value
        elif name == "ArgumentSuffix":
            self.syntax.argument_end = value
        elif name == "ArgumentSeparator":
            self.syntax.argument_separator = value
        elif name == "SectionPrefix":
            self.syntax.section_prefix = value
        elif name == "VariablePrefix":
            self.syntax.variable_start = value
        elif name == "VariableSuffix":
            self.syntax.variable_end = value
        elif name == "IndentationWidth":
            self.settings.indentation = int(value)
        elif name == "Abbreviations":
            self.settings.allow_abbreviations = parse_bool(value)
        elif name == "PragmaOnce":
            self.settings.use_pragma_once = parse_bool(value)
        elif name == "ClassName":
            self.settings.class_name = value
        elif name == "FileName":
            self.settings.file_name = value
        elif name == "HeaderExtension":
            self.settings.header_extension = value
        elif name == "SourceExtension":
            self.settings.source_extension = value
        elif name == "Namespace":
            self.settings.namespace = [s.strip() for s in value.split("::")]
        elif name == "FunctionName":
            self.settings.function_name = value
        elif name == "Test":
            self.settings.add_test = parse_bool(value)
        elif name == "DetectSeparators":
            self.settings.detect_separators = parse_bool(value)
        elif name == "DirName":
            self.settings.header_dir_name = value
            self.settings.source_dir_name = value
        elif name == "HeaderDirName":
            self.settings.header_dir_name = value
        elif name == "SourceDirName":
            self.settings.source_dir_name = value
        elif name == "HeaderOnly":
            self.settings.header_only = parse_bool(value)
        elif name == "AutoFormat":
            self.settings.auto_format = parse_bool(value)
        elif name == "WordWrap":
            self.settings.word_wrap = parse_bool(value)
        elif name == "ImmediateCallbacks":
            self.settings.immediate_callbacks = parse_bool(value)
        elif name == "LineWidth":
            self.settings.line_width = int(value)
        elif name == "MinLineWidth":
            self.settings.min_line_width = int(value)
        elif name == "MaxLineWidth":
            self.settings.max_line_width = int(value)
        elif name == "CaseSensitive":
            self.settings.case_sensitive = parse_bool(value)
        else:
            return False
        return True
