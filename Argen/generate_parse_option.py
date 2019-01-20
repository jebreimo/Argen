# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-04.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import generator_tools as gt
import re
import templateprocessor


def generate_constant_assignment(lines, option):
    if not option.value:
        return option.operation == "none"
    name = "result." + option.member_name
    if option.operation == "assign":
        lines.append("%s = %s;" % (name, option.value))
    elif option.operation == "append":
        lines.append("%s.push_back(%s);" % (name, option.value))
    elif option.operation == "extend":
        lines.append("%s.insert(%s.end(), %s);" % (name, name, option.value))
    return True


def generate_parameter_assignment(lines, option):
    lines.append("read_value(value, arg_it, arg)")
    gt.append_assignment_conditions(lines, option, "value", "arg")


def generate_read_value(option):
    lines = []
    conditions = []
    if not generate_constant_assignment(lines, option):
        generate_parameter_assignment(conditions, option)

    if option.callback:
        conditions.append("%s(result, to_string(arg))" % option.callback)

    if conditions:
        lines.append("if (!" + conditions[0])
        for i in range(1, len(conditions)):
            lines.append("    || !" + conditions[i])
        lines[-1] += ")"
        lines.extend(("{",
                      "    return OptionResult::INVALID_OPTION;",
                      "}"))
    return lines


class OptionCaseGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.option = None
        self.inline_regexp = re.compile("\\$([^$]*)\\$")

    def operation(self, *args):
        return generate_read_value(self.option)

    def inline(self, *args):
        if self.option.inline:
            parts = []
            pos = 0
            for match in self.inline_regexp.finditer(self.option.inline):
                if match.start(0) != pos:
                    parts.append(self.option.inline[pos:match.start(0)])
                parts.append("result.")
                parts.append(match.group(1))
                pos = match.end(0)
            if pos != len(self.option.inline):
                parts.append(self.option.inline[pos:])
            if parts and parts[-1][-1] != ";":
                parts.append(";")
            return "%s" % "".join(parts)
        else:
            return None

    def callback(self, *args):
        if self.option.callback:
            return "%s(result, to_string(arg));" % self.option.callback
        else:
            return None

    def option_name(self, *args):
        return self.option.option_name

    def abort_option(self, *args):
        return self.option.post_operation == "abort"

    def return_option(self, *args):
        return self.option.post_operation == "return"

    def final_option(self, *args):
        return self.option.post_operation == "final"

    def has_temp_variable(self, *args):
        operation_type = gt.get_operation_type(self.option)
        if operation_type in (gt.Operations.APPEND_TUPLE,
                              gt.Operations.APPEND_VECTOR):
            return True
        elif operation_type == gt.Operations.EXTEND_VECTOR:
            return self.option.valid_values
        else:
            return False

    def case_implementation(self, *args):
        return templateprocessor.make_lines(OPTION_CASE_IMPL_TEMPLATE, self)

    def temp_variable_type(self, *args):
        return self.option.value_type

    def counter_increment(self, *args):
        if self.option in self._session.code_properties.counted_options:
            return "++counters.%s_counter;" % self.option.option_name
        return None


def generate_option_cases(session):
    result = []
    option_gen = OptionCaseGenerator(session)
    for opt in [o for o in session.arguments if o.flags]:
        option_gen.option = opt
        result.extend(templateprocessor.make_lines(
            OPTION_CASE_TEMPLATE,
            option_gen))
    return result


OPTION_CASE_TEMPLATE = """\
case Option_[[[option_name]]]:
[[[IF has_temp_variable]]]
    {
        [[[temp_variable_type]]] temp;
        [[[case_implementation]]]
    }
[[[ELSE]]]
    [[[case_implementation]]]
[[[ENDIF]]]\
"""

OPTION_CASE_IMPL_TEMPLATE = """\
[[[operation]]]
[[[inline]]]
[[[counter_increment]]]
[[[IF abort_option]]]
result.[[[function_name]]]_result = [[[class_name]]]::OPTION_[[[option_name]]];
return OptionResult::ABORTING_OPTION;
[[[ELIF return_option]]]
result.[[[function_name]]]_result = [[[class_name]]]::OPTION_[[[option_name]]];
break;
[[[ELIF final_option]]]
return OptionResult::FINAL_OPTION;
[[[ELSE]]]
break;
[[[ENDIF]]]\
"""
