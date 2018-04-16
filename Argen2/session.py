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
from helpfileerror import HelpFileError
from helpfilesyntax import HelpFileSyntax


def make_default_variables():
    today = datetime.date.today()
    variables = dict(YEAR=str(today.year),
                     MONTH="%02d" % today.month,
                     DAY="%02d" % today.day)
    variables.update(dict(os.environ))
    return variables


def parse_bool(value):
    value = value.lower()
    if value in ("0", "false"):
        return False
    if value in ("1", "true"):
        return True
    raise HelpFileError("Invalid boolean value: %s" % value)


class Session:
    def __init__(self):
        self.variables = make_default_variables()
        self.indentation = -1
        self.allow_abbreviations = True
        self.use_pragma_once = True
        self.class_name = "ArgumentParser"
        self.file_name = None
        self.header_extension = "h"
        self.source_extension = "cpp"
        self.namespace = ""
        self.function_name = "parse_arguments"
        self.line_width = 79
        self.add_test = False
        self.syntax = HelpFileSyntax()
        self.help_text = ""
        self.error_text = ""
        self.metavar_types = dict(properties.DEFAULT_METAVAR_TYPES)
        self.arguments = []
        self.detect_separators = False

    def set_setting(self, name, value):
        if name == "ArgumentPrefix":
            self.syntax.argument_start = value
        elif name == "ArgumentSuffix":
            self.syntax.argument_end = value
        elif name == "ArgumentSeparator":
            self.syntax.argument_separator = value
        elif name == "IndentationWidth":
            self.indentation = int(value)
        elif name == "Abbreviations":
            self.allow_abbreviations = parse_bool(value)
        elif name == "PragmaOnce":
            self.use_pragma_once = parse_bool(value)
        elif name == "SectionPrefix":
            self.syntax.section_prefix = value
        elif name == "VariablePrefix":
            self.syntax.variable_start = value
        elif name == "VariableSuffix":
            self.syntax.variable_end = value
        elif name == "Class_name":
            self.class_name = value
        elif name == "File_name":
            self.file_name = value
        elif name == "HeaderExtension":
            self.header_extension = value
        elif name == "SourceExtension":
            self.source_extension = value
        elif name == "Namespace":
            self.namespace = value
        elif name == "FunctionName":
            self.function_name = value
        elif name == "LineWidth":
            self.line_width = int(value)
        elif name == "Test":
            self.add_test = parse_bool(value)
        elif name == "DetectSeparators":
            self.detect_separators = parse_bool(value)
