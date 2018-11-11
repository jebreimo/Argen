# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import re
import templateprocessor
import deducedtype

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

    def option_cases(self, *args):
        result = []
        option_gen = ParseOptionGenerator(self._session)
        for opt in self._options:
            option_gen.option = opt
            result.extend(templateprocessor.make_lines(
                PARSE_OPTION_TEMPLATE,
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
    type_value = 0
    if option.value:
        type_value = 1
    elif not option.value_type.subtypes:
        type_value = 2
    elif deducedtype.is_tuple(option.value_type):
        type_value = 3
    else:
        type_value = 4
    return op_value + type_value


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
        parts.append("    || !assign_value(result.%s, value, arg)" % option.member_name)
    elif operation_type == Operations.ASSIGN_TUPLE:
        parts.append("    || !split_value(parts, value, '%s', %d, %d, arg)"
                     % (option.separator, option.separator_count[0],
                        option.separator_count[0]))
        for i in range(len(option.value_type.subtypes)):
            parts.append("    || !assign_value(std::get<%d>(result.%s), parts[%d], arg)"
                         % (i, option.member_name, i))
    parts[-1] += ")"
    parts.extend(("{",
                  "    return abort(result, Arguments::RESULT_ERROR, autoExit);",
                  "}"))
    return parts


class ParseOptionGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.option = None
        self.inline_regexp = re.compile("\$([^$]*)\$")

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


PARSE_ARGUMENTS_TEMPLATE = """\
template <typename T>
bool from_string(const std::string_view& str, T& value)
{
    std::istringstream stream(std::string(str.data(), str.size()));
    stream >> value;
    return !stream.fail() && stream.eof();
}

bool read_value(std::string_view& value,
                ArgumentIterator& iterator,
                const Argument& argument)
{
    if (!iterator.hasNext())
    {
        write_error_text(to_string(argument) + ": no value given.");
        return false;
    }
    value = iterator.nextValue();
    return true;
}

[[[IF has_separators]]]
std::vector<std::string_view> split_string(
        const std::string_view& string,
        char separator,
        size_t max_splits = SIZE_MAX)
{
    std::vector<std::string_view> result;
    auto from = string.data();
    auto end = from + string.size();
    while (result.size() < max_splits)
    {
        auto to = std::find(from, end, separator);
        if (to == end)
            break;
        result.emplace_back(from, to - from);
        from = to + 1;
    }
    result.emplace_back(from, end - from);
    return result;
}

bool split_value(std::vector<std::string_view>& parts,
                 const std::string_view& value,
                 char separator,
                 size_t min_splits, size_t max_splits,
                 const Argument& argument)
{
    parts = split_string(value, separator, max_splits);
    if (parts.size() < min_splits + 1)
    {
        std::stringstream ss;
        ss << argument << ": incorrect number of parts in value \\""
           << value << "\\".\\nIt must have ";
        if (min_splits == max_splits)
            ss << "exactly ";
        else
            ss << "at least ";
        ss << min_splits + 1 <<  " parts separated by " << separator
           << "'s.";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
[[[ENDIF]]]    
[[[IF has_program_name]]]
std::string getBaseName(const std::string& path)
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
    programName = getBaseName(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
    ArgumentIterator argIt(argc - 1, argv + 1);
[[[IF has_final_option]]]
    bool finalOption = false;
[[[ENDIF]]]
    while (argIt.hasNext())
    {
        auto arg = argIt.nextArgument();
        auto optionCode = findOptionCode(arg);
        switch (optionCode)
        {
        [[[option_cases]]]
        default:
            break;
        }

        if (autoExit && result.parseArguments_result == [[[class_name]]]::RESULT_ERROR)
            exit(EINVAL);
        [[[IF has_final_option]]]
        if (finalOption)
            break;
        [[[ENDIF]]]
    }
    return result;
}
"""

PARSE_OPTION_TEMPLATE = """\
case Option_[[[option_name]]]:
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
