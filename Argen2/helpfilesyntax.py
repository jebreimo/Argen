# -*- coding: UTF-8 -*-
#############################################################################
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
#############################################################################

class HelpFileSyntax:
    def __init__(self):
        self.section_prefix = "$$$"
        self.argument_start = "{{"
        self.argument_end = "}}"
        self.argument_separator = "|"
        self.variable_start = "${"
        self.variable_end = "}"
        self.internal_variables = {"CONTENTS", "HEADER", "SOURCE", "PROGRAM", "HPPNAME", "CPPNAME", "OPTIONS",
                                   "ARGUMENTS", "ERROR"}
