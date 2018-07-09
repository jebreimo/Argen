# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-03.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class HeaderFileGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.header_includes = ["#include " + s for s in
                                session.code_properties.header_includes]

    def header_code(self, params, context):
        return generate_header_contents(self._session)


def generate_header(session):
    return templateprocessor.make_text(session.code_properties.header_template,
                                       HeaderFileGenerator(session))


class HeaderContentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.has_namespace = session.code_properties.namespace_start
        self.namespace_start = session.code_properties.namespace_start
        self.namespace_end = session.code_properties.namespace_end
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.has_member_counters = session.code_properties.counted_members

    def code(self, params, context):
        return templateprocessor.make_lines(HEADER_CONTENTS_TEMPLATE, self)

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


def generate_header_contents(session):
    return templateprocessor.make_lines(HEADER_NAMESPACE_TEMPLATE,
                                        HeaderContentsGenerator(session))


HEADER_NAMESPACE_TEMPLATE = """\
[[[IF has_namespace]]]
[[[namespace_start]]]
    [[[code]]]
[[[namespace_end]]]
[[[ELSE]]]
[[[code]]]
[[[ENDIF]]]\
"""


HEADER_CONTENTS_TEMPLATE = """\
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
    Result [[[function_name]]]_result = RESULT_OK;
[[[IF has_member_counters]]]

    /** This member is reserved for internal use in [[[function_name]]].
      *
      * It's always nullptr.
      */
    struct MemberCounters* reserved_for_internal_use = nullptr;
[[[ENDIF]]]
};

/** @brief Parses the arguments in @a argv.
  *
  * @param argc the number of values in argv.
  * @param argv the arguments (an array of char-strings).
  * @returns an instance of [[[class_name]]] with values in
  *     accordance with the parsed arguments. If @a argc is 0 the
  *     returned value is a nullptr.
  */
[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool autoExit = true);

void write_help_text(std::ostream& stream, size_t lineWidth = 0);

void write_synopsis(std::ostream& stream, size_t lineWidth = 0);\
"""


RESULT_ENUM_TEMPLATE = """\
/** @brief The %s option was given.
  */
OPTION_%s,\
"""
