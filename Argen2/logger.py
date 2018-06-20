# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import sys


class Logger:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    Labels = {
        DEBUG: "debug",
        INFO: "info",
        WARNING: "warning",
        ERROR: "error"
    }

    def __init__(self, stream=sys.stdout, error_level=DEBUG):
        self.stream = stream
        self.error_level = error_level
        self.file_name = None
        self.line_number = None,
        self.argument = None
        self.counters = [0] * 4

    def _file_name_and_line_number(self, file_name=None, line_number=None,
                                   argument=None):
        if file_name is None and argument:
            file_name = argument.file_name
        if not file_name and self.argument:
            file_name = self.argument.file_name
        if not file_name:
            file_name = self.file_name
        if line_number is None and argument:
            line_number = argument.line_number
        if not line_number and self.argument:
            line_number = self.argument.line_number
        if not line_number:
            line_number = self.line_number
        return file_name, line_number

    def _write(self, error_level, message,
               file_name=None, line_number=None, argument=None):
        if Logger.DEBUG <= error_level <= Logger.ERROR:
            self.counters[error_level] += 1
        if error_level < self.error_level:
            return
        file_name, line_number = self._file_name_and_line_number(file_name,
                                                                 line_number,
                                                                 argument)
        label = Logger.Labels.get(error_level, "unknown")
        if file_name and line_number is not None:
            print("%s:%d: %s: %s" % (file_name, line_number, label, message))
        elif file_name:
            print("%s: %s: %s" % (file_name, label, message))
        elif line_number is not None:
            print("%d: %s: %s" % (line_number, label, message))
        else:
            print("%s: %s" % (label, message))

    def debug(self, message, file_name=None, line_number=None, argument=None):
        self._write(self.DEBUG, message, file_name, line_number, argument)

    def info(self, message, file_name=None, line_number=None, argument=None):
        self._write(self.INFO, message, file_name, line_number, argument)

    def warn(self, message, file_name=None, line_number=None, argument=None):
        self._write(self.WARNING, message, file_name, line_number, argument)

    def error(self, message, file_name=None, line_number=None, argument=None):
        self._write(self.ERROR, message, file_name, line_number, argument)
