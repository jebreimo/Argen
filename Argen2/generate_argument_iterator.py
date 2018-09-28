# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-09.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class ArgumentIteratorGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.has_short_options = session.code_properties.short_options
        self.has_slash_options = any(k[0] == '/'
                                     for k in session.code_properties.options)
        self.has_dash_options = any(k[0] == '-'
                                     for k in session.code_properties.options)
        self.has_normal_options = self.has_slash_options or self.has_dash_options
        self.has_both_options = self.has_slash_options and self.has_dash_options
        self.has_values = session.code_properties.has_option_values
        self.has_delimited_values = session.code_properties.has_delimited_values


def generate_argument_iterator(session):
    return templateprocessor.make_lines(ARGUMENT_ITERATOR_TEMPLATE,
                                        ArgumentIteratorGenerator(session))


ARGUMENT_ITERATOR_TEMPLATE = """\
struct Argument
{
    Argument() = default;

[[[IF has_short_options]]]
    Argument(std::string_view argument, bool isShortOption)
            : string(argument),
              isShortOption(isShortOption)
    {}
[[[ELSE]]]
    Argument(std::string_view argument) : string(argument) {}
[[[ENDIF]]]

    explicit operator bool() const {return !string.empty();}

    std::string_view string;
[[[IF has_short_options]]]
    bool isShortOption = false;
[[[ENDIF]]]
};
[[[IF has_short_options]]]

inline bool resemblesShortOption(const char* s)
{
    return s[0] == '-' && s[1] != 0
           && (s[1] != '-' || s[2] == 0 || s[2] == '=');
}
[[[ENDIF]]]
[[[IF has_normal_options]]]

inline bool resemblesOption(const char* s)
{
[[[IF has_both_options]]]
    return (s[0] == '-' || s[0] == '/') && s[1] != 0;
[[[ELIF has_dash_options]]]
    return s[0] == '-' && s[1] != 0;
[[[ELSE]]]
    return s[0] == '/' && s[1] != 0;
[[[ENDIF]]]
}
[[[ENDIF]]]

class ArgumentIterator
{
public:
    ArgumentIterator(int argc, char* argv[])
            : m_ArgIt(*argv), m_ArgvIt(&argv[0]), m_ArgvEnd(&argv[argc])
    {}

    Argument nextArgument()
    {
        if (m_ArgvIt == m_ArgvEnd)
            return {};
[[[IF has_short_options]]]

        if (m_ArgIt != *m_ArgvIt)
        {
            auto arg = m_ArgIt++;
            size_t length = 1;
            if (*m_ArgIt == 0)
                m_ArgIt = *++m_ArgvIt;
            return {{arg, length}, true};
        }

        if (resemblesShortOption(m_ArgIt))
        {
            auto arg = m_ArgIt;
            size_t length = 2;
            m_ArgIt += 2;
            if (*m_ArgIt == 0)
                m_ArgIt = *++m_ArgvIt;
            return {{arg, length}, true};
        }
[[[ENDIF]]]

        auto arg = m_ArgIt;
        size_t length = 0;
        if (resemblesOption(m_ArgIt))
        {
            length += 2;
            while (m_ArgIt[length] != 0 && m_ArgIt[length] != '=')
                ++length;
            m_ArgIt += length;
            if (*m_ArgIt == '=')
                ++m_ArgIt;
            else if (*m_ArgIt == 0)
                m_ArgIt = *++m_ArgvIt;
        }
        else
        {
            while (m_ArgIt[length] != 0)
                ++length;
            m_ArgIt += length;
            if (*m_ArgIt == 0)
                m_ArgIt = *++m_ArgvIt;
        }

        return {{arg, length}, false};
    }
[[[IF has_values]]]

    std::string_view nextValue()
    {
        if (m_ArgvIt == m_ArgvEnd)
            return {};
        auto value = m_ArgIt;
        size_t length = strlen(value);
        m_ArgIt = *++m_ArgvIt;
        return {value, length};
    }

    bool hasValue() const
    {
        return m_ArgIt != *m_ArgvIt;
    }
[[[ENDIF]]]
[[[IF has_delimited_values]]]

    std::string_view nextDelimitedValue(char delimiter)
    {
        if (m_ArgvIt == m_ArgvEnd)
            return {};

        if (*m_ArgIt == 0)
        {
            m_ArgIt = *++m_ArgvIt;
            return {};
        }

        auto value = m_ArgIt;
        size_t length = 0;
        while (m_ArgIt[length] != 0 && m_ArgIt[length] != delimiter)
            ++length;
        m_ArgIt += length + m_ArgIt[length] == 0 ? 0 : 1;
        return {value, length};
    }
[[[ENDIF]]]
private:
    char* m_ArgIt;
    char** m_ArgvIt;
    char** m_ArgvEnd;
};
"""
