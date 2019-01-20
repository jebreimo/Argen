# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-10-10.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import generator_tools as gt
import templateprocessor


class OptionFunctionsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        self._session = session
        self.function_name = session.settings.function_name
        self.has_separators = session.code_properties.has_delimited_options \
                              or session.code_properties.has_delimited_arguments
        self.has_non_string_values = session.code_properties.has_non_string_values
        self.has_options = session.code_properties.options
        methods = gt.get_assignment_methods(session.arguments)
        self.has_parse_and_assign = "parse_and_assign" in methods
        self.has_parse_and_assign_vector = "parse_and_assign_vector" in methods
        self.has_parse_and_append = "parse_and_append" in methods
        self.has_parse_and_extend = "parse_and_extend" in methods
        self.has_append = "append" in methods
        self.has_extend = "extend" in methods
        self.has_check_value = any(a for a in self._session.arguments if a.valid_values and a.member and str(a.value_type).find("vector") == -1)
        self.has_check_vector = any(a for a in self._session.arguments if a.valid_values and a.member and str(a.value_type).find("vector") != -1)


def generate_option_functions(session):
    generator = OptionFunctionsGenerator(session)
    return templateprocessor.make_lines(OPTION_FUNCTIONS_TEMPLATE, generator)


OPTION_FUNCTIONS_TEMPLATE = """\
bool show_help(Arguments& arguments, const std::string& argument)
{
    write_help_text(std::cout);
    return true;
}

[[[IF has_non_string_values]]]
template <typename T>
bool from_string(const std::string_view& str, T& value)
{
    std::istringstream stream(to_string(str));
    stream >> value;
    return !stream.fail() && stream.eof();
}

[[[ENDIF]]]
bool from_string(const std::string_view& str, std::string& value)
{
    value = str;
    return true;
}

[[[IF has_options]]]
bool read_value(std::string_view& value,
                ArgumentIterator& iterator,
                const Argument& argument)
{
    if (!iterator.has_next())
    {
        write_error_text(to_string(argument) + ": no value given.");
        return false;
    }
    value = iterator.next_value();
    return true;
}

[[[ENDIF]]]
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

template <typename Arg>
bool split_value(std::vector<std::string_view>& parts,
                 const std::string_view& value,
                 char separator,
                 size_t min_splits, size_t max_splits,
                 const Arg& argument)
{
    parts = split_string(value, separator, max_splits);
    if (parts.size() < min_splits + 1)
    {
        std::stringstream ss;
        ss << to_string(argument)
           << ": incorrect number of parts in value \\""
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
[[[IF has_parse_and_assign]]]
    
template <typename T, typename Arg>
bool parse_and_assign(T& value,
                      const std::string_view& string,
                      const Arg& argument)
{
    if (from_string(string, value))
        return true;

    write_error_text(to_string(argument) + ": invalid value \\""
                     + to_string(string) + "\\".");
    return false;
}
[[[ENDIF]]]
[[[IF has_parse_and_assign_vector]]]

template <typename T, typename Arg>
bool parse_and_assign(std::vector<T>& value,
                      const std::vector<std::string_view>& strings,
                      const Arg& argument)
{
    value.clear();
    for (auto& string : strings)
    {
        T temp;
        if (!from_string(string, temp))
        {
            write_error_text(to_string(argument) + ": invalid value \\""
                             + to_string(string) + "\\".");
            return false;
        }
        value.push_back(temp);
    }
    return true;
}
[[[ENDIF]]]
[[[IF has_parse_and_append]]]

template <typename T, typename Arg>
bool parse_and_append(std::vector<T>& value,
                      const std::string_view& string,
                      const Arg& argument)
{
    value.clear();
    T temp;
    if (!from_string(string, temp))
    {
        write_error_text(to_string(argument) + ": invalid value \\""
                         + to_string(string) + "\\".");
        return false;
    }
    value.push_back(temp);
    return true;
}
[[[ENDIF]]]
[[[IF has_append]]]

template <typename T>
bool append(std::vector<T>& values, T&& value)
{
    values.push_back(std::forward<T>(value));
    return true;
}
[[[ENDIF]]]
[[[IF has_extend]]]

template <typename T>
bool extend(std::vector<T>& values, std::vector<T> newValues)
{
    values.insert(values.end(), newValues.begin(), newValues.end());
    return true;
}
[[[ENDIF]]]
[[[IF has_parse_and_extend]]]

template <typename T, typename Arg>
bool parse_and_extend(std::vector<T>& value,
                      const std::vector<std::string_view>& strings,
                      const Arg& argument)
{
    for (auto& string : strings)
    {
        T temp;
        if (!from_string(string, temp))
        {
            write_error_text(to_string(argument) + ": invalid value \\""
                             + to_string(string) + "\\".");
            return false;
        }
        value.push_back(temp);
    }
    return true;
}
[[[ENDIF]]]
[[[IF has_check_value]]]

template <typename T, typename CheckFunc, typename Arg>
bool check_value(T value, CheckFunc check_func,
                 const char* legal_values_text,
                 const Arg& argument)
{
    if (!check_func(value))
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value
           << ". (Legal values: " << legal_values_text << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
[[[ENDIF]]]
[[[IF has_check_vector]]]

template <typename T, typename CheckFunc, typename Arg>
bool check_values(const std::vector<T>& values,
                  CheckFunc check_func,
                  const char* legal_values_text,
                  const Arg& argument)
{
    for (auto&& value : values)
    {
        if (!check_func(value))
        {
            std::stringstream ss;
            ss << argument << ": illegal value: " << value
               << ". (Legal values: " << legal_values_text << ")";
            write_error_text(ss.str());
            return false;
        }
    }
    return true;
}
[[[ENDIF]]]
"""