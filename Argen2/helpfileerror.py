# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================

class HelpFileError(Exception):
    def __init__(self, message="", line_number=-1, file_name=""):
        super().__init__()
        self.message = message
        self.line_number = line_number
        self.file_name = file_name

    def __str__(self):
        if self.file_name and self.line_number >= 0:
            return "%(file_name)s:%(line_number)d: %(message)s" % self.__dict__
        elif self.file_name:
            return "%(file_name)s: %(message)s" % self.__dict__
        elif self.line_number:
            return "line %(line_number)d: %(message)s" % self.__dict__
        else:
            return self.message
