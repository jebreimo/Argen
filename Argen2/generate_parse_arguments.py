# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype
import re
import templateprocessor


class ParseArgumentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self._options = [a for a in self._session.arguments if a.flags]
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.has_final_option = any(o for o in self._options
                                    if o.post_operation == "final")
        self.has_program_name = session.code_properties.has_program_name
        self.has_separators = session.code_properties.has_delimited_values
        self.has_values = any(a for a in session.arguments
                              if a.operation != "none" and a.value is None)

    def option_cases(self, *args):
        result = []
        option_gen = ParseOptionGenerator(self._session)
        for opt in self._options:
            option_gen.option = opt
            result.extend(templateprocessor.make_lines(
                OPTION_CASE_TEMPLATE,
                option_gen))
        return result


def generate_parse_arguments(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsGenerator(session))


class Operations:
    NO_OPERATION = 0
    ASSIGN_CONSTANT = 1
    ASSIGN_VALUE = 2
    ASSIGN_TUPLE = 3
    ASSIGN_VECTOR = 4
    APPEND_CONSTANT = 11
    APPEND_VALUE = 12
    APPEND_TUPLE = 13
    APPEND_VECTOR = 14
    EXTEND_CONSTANT = 21
    EXTEND_VECTOR = 24


def get_operation_type(option):
    if option.operation == "assign":
        op_value = 0
    elif option.operation == "append":
        op_value = 10
    elif option.operation == "extend":
        op_value = 20
    else:
        return Operations.NO_OPERATION
    if option.value:
        type_value = 1
    elif not option.value_type.subtypes:
        type_value = 2
    elif deducedtype.is_tuple(option.value_type):
        type_value = 3
    else:
        type_value = 4
    return op_value + type_value


def generate_check_value_lambda(valid_values):
    tests = []
    for entry in valid_values:
        lo, hi = entry
        if not lo and not hi:
            continue
        elif lo == hi:
            tests.append(f"v == {lo}")
        elif lo and hi:
            if len(valid_values) == 1:
                tests.append(f"{lo} <= v && v <= {hi}")
            else:
                tests.append(f"({lo} <= v && v <= {hi})")
        elif lo:
            tests.append(f"{lo} <= v")
        else:
            tests.append(f"v <= {hi}")
    return "[](auto&& v){return %s;}" % " || ".join(tests)


def generate_check_value_text(valid_values):
    tokens = []
    for entry in valid_values:
        lo, hi = entry
        if not lo and not hi:
            continue
        elif lo == hi:
            tokens.append(lo)
        elif lo and hi:
            tokens.append(f"{lo}...{hi}")
        elif lo:
            tokens.append(f"{lo}...")
        else:
            tokens.append(f"...{hi}")
    return '"%s"' % ", ".join(t.replace('"', '\\"') for t in tokens)


def make_check_value(function_name, value_name, valid_values):
    return "    || !%s(%s, %s, %s, arg)" \
           % (function_name, value_name,
              generate_check_value_lambda(valid_values),
              generate_check_value_text(valid_values))


def append_check_value(lines, option, operation_type):
    valid_values = option.valid_values
    if not valid_values:
        return
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append(make_check_value("check_value",
                                      "result." + option.member_name,
                                      valid_values[0]))
    elif operation_type == Operations.ASSIGN_VECTOR:
        lines.append(make_check_value("check_values",
                                      "result." + option.member_name,
                                      valid_values[0]))
    elif operation_type == Operations.APPEND_VALUE:
        lines.append(make_check_value("check_value",
                                      "result.%s.back()" % option.member_name,
                                      option.valid_values[0]))
    elif operation_type in (Operations.APPEND_VECTOR, Operations.EXTEND_VECTOR):
        lines.append(make_check_value("check_value", "temp",
                                      option.valid_values[0]))
    elif operation_type in (Operations.APPEND_TUPLE, Operations.ASSIGN_TUPLE):
        if operation_type == Operations.ASSIGN_TUPLE:
            variable = "result." + option.member_name
        else:
            variable = "temp"
        for i in range(len(valid_values)):
            lines.append(make_check_value("check_value",
                                          "std::get<%d>(%s)" % (i, variable),
                                          valid_values[i]))


def make_split_value(separator, separator_count):
    return "    || !split_value(parts, value, '%s', %d, %s, arg)" \
           % (separator, separator_count[0],
              str(separator_count[1]) if separator_count[1] else "SIZE_MAX")


def generate_read_value(option):
    operation_type = get_operation_type(option)
    if operation_type == Operations.ASSIGN_CONSTANT:
        return "result.%s = %s;" % (option.member_name, option.value)
    elif operation_type == Operations.APPEND_CONSTANT:
        return "result.%s.push_back(%s);" % (option.member_name, option.value)
    elif operation_type == Operations.EXTEND_CONSTANT:
        return "result.%s.insert(result.%s.end(), %s);" \
               % (option.member_name, option.member_name, option.value)
    elif operation_type == Operations.NO_OPERATION:
        return None

    parts = ["if (!read_value(value, argIt, arg)"]
    if operation_type == Operations.ASSIGN_VALUE:
        parts.append("    || !parse_and_assign(result.%s, value, arg)"
                     % option.member_name)
        append_check_value(parts, option, operation_type)
    elif operation_type == Operations.ASSIGN_TUPLE:
        parts.append(make_split_value(option.separator, option.separator_count))
        for i in range(len(option.value_type.subtypes)):
            parts.append("    || !parse_and_assign(std::get<%d>(result.%s), parts[%d], arg)"
                         % (i, option.member_name, i))
        append_check_value(parts, option, operation_type)
    elif operation_type == Operations.ASSIGN_VECTOR:
        if option.separator is None:
            parts.append("    || !parse_and_assign(result.%s, std::vector<std::string_view>{value}, arg)"
                         % option.member_name)
        else:
            parts.append(make_split_value(option.separator,
                                          option.separator_count))
            parts.append("    || !parse_and_assign(result.%s, parts, arg)"
                         % option.member_name)
        append_check_value(parts, option, operation_type)
    elif operation_type == Operations.APPEND_VALUE:
        parts.append("    || !parse_and_append(result.%s, value, arg)"
                     % option.member_name)
        append_check_value(parts, option, operation_type)
    elif operation_type == Operations.APPEND_TUPLE:
        parts.append(make_split_value(option.separator, option.separator_count))
        for i in range(len(option.value_type.subtypes)):
            parts.append(
                "    || !parse_and_assign(std::get<%d>(temp), parts[%d], arg)"
                % (i, i))
        append_check_value(parts, option, operation_type)
        parts.append("    || !append(result.%s, std::move(temp))"
                     % option.member_name)
    elif operation_type == Operations.APPEND_VECTOR:
        parts.append(make_split_value(option.separator, option.separator_count))
        for i in range(len(option.value_type.subtypes)):
            parts.append("    || !parse_and_assign(temp, parts, arg)")
        parts.append("    || !append(result.%s, std::move(temp))"
                     % option.member_name)
        append_check_value(parts, option, operation_type)
    elif operation_type == Operations.EXTEND_VECTOR:
        parts.append(make_split_value(option.separator, option.separator_count))
        if option.valid_values:
            parts.append("    || !parse_and_assign(temp, parts, arg)")
            parts.append("    || !extend(result.%s, std::move(temp))"
                         % option.member_name)
        else:
            parts.append("    || !parse_and_extend(result.%s, parts, arg)"
                         % option.member_name)

    parts[-1] += ")"
    parts.extend(("{",
                  "    return abort(result, Arguments::RESULT_ERROR, autoExit);",
                  "}"))
    return parts


class ParseOptionGenerator(templateprocessor.Expander):
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
        operation_type = get_operation_type(self.option)
        if operation_type in (Operations.APPEND_TUPLE,
                              Operations.APPEND_VECTOR):
            return True
        elif operation_type == Operations.EXTEND_VECTOR:
            return self.option.valid_values
        else:
            return False

    def case_implementation(self, *args):
        return templateprocessor.make_lines(OPTION_CASE_IMPL_TEMPLATE, self)

    def temp_variable_type(self, *args):
        return self.option.value_type


PARSE_ARGUMENTS_TEMPLATE = """\
[[[IF has_program_name]]]
std::string get_base_name(const std::string& path)
{
    size_t pos = path.find_last_of("/\\\\");
    if (pos == std::string::npos)
        return path;
    else
        return path.substr(pos + 1);
}
[[[ENDIF]]]

[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool autoExit)
{
    if (argc == 0)
        return [[[class_name]]]();

[[[IF has_program_name]]]
    programName = get_base_name(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
    ArgumentIterator argIt(argc - 1, argv + 1);
[[[IF has_values]]]
    std::string_view value;
[[[IF has_separators]]]
    std::vector<std::string_view> parts;
[[[ENDIF]]]
[[[ENDIF]]]
[[[IF has_final_option]]]
    bool finalOption = false;
[[[ENDIF]]]
    while (argIt.has_next())
    {
        auto arg = argIt.next_argument();
        auto optionCode = find_option_code(arg);
        switch (optionCode)
        {
        [[[option_cases]]]
        default:
            break;
        }

        if (autoExit && result.[[[function_name]]]_result == [[[class_name]]]::RESULT_ERROR)
            exit(EINVAL);
[[[IF has_final_option]]]
        if (finalOption)
            break;
[[[ENDIF]]]
    }
    return result;
}
"""

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
[[[callback]]]
[[[IF abort_option]]]
return abort(result, [[[class_name]]]::OPTION_[[[option_name]]], autoExit);
[[[ELIF return_option]]]
result.[[[function_name]]]_result = [[[class_name]]]::OPTION_[[[option_name]]];
return result;
[[[ELIF final_option]]]
finalOption = true;
break;
[[[ELSE]]]
break;
[[[ENDIF]]]\
"""
