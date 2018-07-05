# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


class HelpFileSyntax:
    def __init__(self):
        self.section_prefix = "$$$"
        self.argument_start = "{{"
        self.argument_end = "}}"
        self.argument_separator = "|"
        self.variable_start = "${"
        self.variable_end = "}"
        self.values_entry_separator = "$"
        self.value_separator = ","
        self.internal_variables = {"SOURCE_CONTENTS", "HEADER_CONTENTS",
                                   "SOURCE_INCLUDES", "HEADER_INCLUDES",
                                   "SOURCE_CODE", "HEADER_CODE",
                                   "HEADER", "SOURCE", "PROGRAM",
                                   "HEADER_NAME", "SOURCE_NAME", "OPTIONS",
                                   "ARGUMENTS", "ERROR"}
