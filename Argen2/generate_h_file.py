# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor

template = """\
/** @brief The result returned by [[[function_name]]]
  */
struct [[[class_name]]]
{
    /** @brief Assigns default values to all members.
      */
    [[[class_name]]]();

    /** @brief Returns true if [[[function_name]]]_result is RESULT_OK, false otherwise.
      */
    explicit operator bool() const;

    [[[members]]]

    enum Result
    {
        /** @brief [[[function_name]]] parsed the arguments successfully.
          */
        RESULT_OK,
        [[[result_enums]]]
        /** @brief There are invalid or missing options or arguments.
          *
          * An error message has been displayed. The option and argument
          * members of this struct can not be relied upon.
          */
        RESULT_ERROR
    };

    /** @brief The exit status of [[[function_name]]].
      *
      * This member should always be checked before any of the other members
      * are read.
      */
    Result [[[function_name]]]_result;
};
"""

RESULT_ENUM_TEMPLATE = """\
/** @brief The %s option was given.
  */
OPTION_%s,\
"""

class ArgumentStructGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name

    def members(self, params, context):
        lines = []
        for mem in self._session.members:
            if mem.name and mem.member_type:
                lines.append("%s %s;" % (mem.member_type, mem.name))
        return lines

    def result_enums(self, params, context):
        lines = []
        for arg in self._session.arguments:
            if arg.option_name and arg.post_operation == "abort":
                lines.extend((RESULT_ENUM_TEMPLATE
                              % (arg.flags[-1], arg.option_name)).split("\n"))
        return lines


def generate_h_file(session):
    return templateprocessor.make_text(template,
                                       ArgumentStructGenerator(session))
