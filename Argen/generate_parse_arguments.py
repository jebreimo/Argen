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
    return "%s(%s, %s, %s, arg)" \
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
        lines.append(make_check_value("check_values", "temp",
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


def make_split_value(option):
    if option.separator_count[1]:
        max_count = str(option.separator_count[1])
    else:
        max_count = "SIZE_MAX"
    return "split_value(parts, value, '%s', %d, %s, arg)" \
           % (option.separator, option.separator_count[0], max_count)


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
    operation_type = get_operation_type(option)
    dest_name = "result." + option.member_name
    lines.append("read_value(value, arg_it, arg)")
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append("parse_and_assign(%s, value, arg)" % dest_name)
        append_check_value(lines, option, operation_type)
    elif operation_type == Operations.ASSIGN_TUPLE:
        lines.append(make_split_value(option))
        for i in range(len(option.value_type.subtypes)):
            name = "std::get<%d>(%s)" % (i, dest_name)
            lines.append("parse_and_assign(%s, parts[%d], arg)" % (name, i))
        append_check_value(lines, option, operation_type)
    elif operation_type == Operations.ASSIGN_VECTOR:
        if option.separator is None:
            lines.append("parse_and_assign(%s, std::vector<std::string_view>{value}, arg)"
                         % dest_name)
        else:
            lines.append(make_split_value(option))
            lines.append("parse_and_assign(%s, parts, arg)" % dest_name)
        append_check_value(lines, option, operation_type)
    elif operation_type == Operations.APPEND_VALUE:
        lines.append("parse_and_append(%s, value, arg)" % dest_name)
        append_check_value(lines, option, operation_type)
    elif operation_type == Operations.APPEND_TUPLE:
        lines.append(make_split_value(option))
        for i in range(len(option.value_type.subtypes)):
            name = "std::get<%d>(temp)" % i
            lines.append("parse_and_assign(%s, parts[%d], arg)" % (name, i))
        append_check_value(lines, option, operation_type)
        lines.append("append(%s, std::move(temp))" % dest_name)
    elif operation_type == Operations.APPEND_VECTOR:
        lines.append(make_split_value(option))
        for i in range(len(option.value_type.subtypes)):
            lines.append("parse_and_assign(temp, parts, arg)")
        lines.append("append(%s, std::move(temp))" % dest_name)
        append_check_value(lines, option, operation_type)
    elif operation_type == Operations.EXTEND_VECTOR:
        lines.append(make_split_value(option))
        if option.valid_values:
            lines.append("parse_and_assign(temp, parts, arg)")
            lines.append("extend(%s, std::move(temp))" % dest_name)
        else:
            lines.append("parse_and_extend(%s, parts, arg)" % dest_name)


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

enum class OptionResult
{
    NORMAL_OPTION,
    FINAL_OPTION,
    ABORTING_OPTION,
    INVALID_OPTION,
    UNKNOWN_OPTION
};

OptionResult process_option(Arguments& result,
                            Argument& arg,
                            int option_code,
                            ArgumentIterator& arg_it)
{
[[[IF has_values]]]
    std::string_view value;
[[[IF has_separators]]]
    std::vector<std::string_view> parts;
    switch (option_code)
    {
    [[[option_cases]]]
    default:
        return OptionResult::UNKNOWN_OPTION;
    }
[[[ENDIF]]]
    return OptionResult::NORMAL_OPTION;
}

[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool auto_exit)
{
    if (argc == 0)
        return [[[class_name]]]();

[[[IF has_program_name]]]
    program_name = get_base_name(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
    std::vector<std::string_view> arguments;
    ArgumentIterator arg_it(argc - 1, argv + 1);
[[[ENDIF]]]
[[[IF has_final_option]]]
    bool final_option = false;
[[[ENDIF]]]
    while (arg_it.has_next())
    {
        auto arg = arg_it.next_argument();
        if (arg.is_option)
        {
            auto option_code = find_option_code(arg);
            switch (process_option(result, arg, option_code, arg_it))
            {
            case OptionResult::FINAL_OPTION:
                final_option = true;
                break;
            case OptionResult::ABORTING_OPTION:
                if (auto_exit)
                    exit(0);
                break;
            case OptionResult::INVALID_OPTION:
                if (auto_exit)
                    exit(EINVAL);
                result.[[[function_name]]]_result = Arguments::RESULT_ERROR;
                break;
            case OptionResult::UNKNOWN_OPTION:
                write_error_text(to_string(arg) + ": unknown option.");
                if (auto_exit)
                    exit(EINVAL);
                result.[[[function_name]]]_result = Arguments::RESULT_ERROR;
                break;
            default:
                break;
            }
            if (result.[[[function_name]]]_result != Arguments::RESULT_OK)
                return result;
        }
        else
        {
            arguments.push_back(arg.string);
        }
[[[IF has_final_option]]]
        if (final_option)
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
