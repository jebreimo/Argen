# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-02-02.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import generator_tools as gt
import templateprocessor


class FromStringGenerator(templateprocessor.Expander):
    def __init__(self, session):
        self._session = session
        self.has_non_string_values = session.code_properties.has_non_string_values
        self.has_integer_values = session.code_properties.has_integers
        self.has_string_values = session.code_properties.has_strings


def generate_from_string(session):
    generator = FromStringGenerator(session)
    return templateprocessor.make_lines(FROM_STRING_TEMPLATE, generator)


FROM_STRING_TEMPLATE = """\
[[[IF has_integer_values]]]
template <typename T,
          typename std::enable_if<std::is_signed<T>::value, int>::type = 0>
bool try_parse_integer_impl(const char* str, size_t size, int base, T& value)
{
    errno = 0;
    char* parsed_end = nullptr;
    auto result = strtoll(str, &parsed_end, base);
    if (errno || parsed_end - str != size)
        return false;
    if (result < std::numeric_limits<T>::min()
        || std::numeric_limits<T>::max() < result)
        return false;
    value = T(result);
    return true;
}

template <typename T,
          typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
bool try_parse_integer_impl(const char* str, size_t size, int base, T& value)
{
    errno = 0;
    char* parsed_end = nullptr;
    auto result = strtoull(str, &parsed_end, base);
    if (errno || parsed_end - str != size)
        return false;
    if (std::numeric_limits<T>::max() < result)
        return false;
    value = T(result);
    return true;
}

template <typename T,
          typename std::enable_if<std::is_integral<T>::value, int>::type = 0>
bool from_string(const std::string_view& s, T& value)
{
    if (s.empty())
        return false;
    auto begin = s.data();
    auto end = begin + s.size();
    std::string copy;
    if (*begin == '-' || *begin == '+')
        copy.push_back(*begin++);

    int base = 10;
    if (end - begin > 2 && *begin == '0')
    {
        switch (*(begin + 1) & 0xDF)
        {
        case 'B': base = 2; begin += 2; break;
        case 'O': base = 8; begin += 2; break;
        case 'X': base = 16; begin += 2; break;
        default: break;
        }
    }

    std::copy_if(begin, end, back_inserter(copy), [](auto c){return c != '_';});
    return try_parse_integer_impl(copy.c_str(), copy.size(), base, value);
}
[[[ENDIF]]]
[[[IF has_non_string_values]]]

[[[IF has_integer_values]]]
template <typename T,
          typename std::enable_if<!std::is_integral<T>::value, int>::type = 0>
[[[ELSE]]]
template <typename T>
[[[ENDIF]]]
bool from_string(const std::string_view& str, T& value)
{
    std::istringstream stream(std::string(str.data(), str.size()));
    stream >> value;
    return !stream.fail() && stream.eof();
}
[[[ENDIF]]]
[[[IF has_string_values]]]

bool from_string(const std::string_view& str, std::string& value)
{
    value = str;
    return true;
}
[[[ENDIF]]]
"""
