# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-24.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
from generate_help_text_string import generate_help_text_string, escape_text


class WriteHelpTextGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.line_width = session.settings.line_width
        self.min_line_width = session.code_properties.min_line_width
        self.max_line_width = session.code_properties.max_line_width
        self.has_min_max_line_width = self.min_line_width \
                                      and self.max_line_width
        self.help_text = generate_help_text_string(session.help_text, session)
        self.brief_help_text = generate_help_text_string(
            session.brief_help_text, session)
        alignment_char = escape_text(session.syntax.alignment_char)
        self.has_alignment = any(alignment_char in s for s in self.help_text)
        self.has_tabs = any("\t" in s for s in self.help_text)
        nb_space = escape_text(session.syntax.non_breaking_space)
        self.has_non_breaking_space = any(nb_space in s for s in self.help_text)
        self.has_program_name = any("${PROGRAM}" in s for s in self.help_text)


def  generate_write_help_text(session):
    return templateprocessor.make_lines(WRITE_HELP_TEXT_TEMPLATE,
                                        WriteHelpTextGenerator(session))


WRITE_HELP_TEXT_TEMPLATE = """\
[[[IF has_program_name]]]
std::string programName = "<program>";

[[[ENDIF]]]
const char HELP_TEXT[] =
    [[[help_text]]];

const char BRIEF_HELP_TEXT[] =
    [[[brief_help_text]]];

class HelpTextWriter
{
public:
    HelpTextWriter(std::ostream& stream, unsigned lineWidth)
        : m_Stream(stream),
          m_LineWidth(lineWidth)
[[[IF has_alignment]]]
    {
        m_AlignmentColumns.push_back(0);
    }
[[[ELSE]]]
    {}
[[[ENDIF]]]

    void write_character(char c)
    {
        m_Buffer.push_back(c);
        ++m_Column;
        if (m_Column >= m_LineWidth && !m_EmptyLine)
        {
            m_Stream.put('\\n');
            m_EmptyLine = true;
            if (m_WhitespaceSize)
            {
                m_Buffer.erase(m_Buffer.begin(),
                               m_Buffer.begin() + m_WhitespaceSize);
                m_WhitespaceSize = 0;
            }
[[[IF has_alignment]]]
            m_Column = m_AlignmentColumns.back()
                       + unsigned(m_Buffer.size());
            for (unsigned i = 0; i < m_AlignmentColumns.back(); ++i)
                m_Stream.put(' ');
[[[ELSE]]]
            m_Column = m_Buffer.size();
[[[ENDIF]]]
        }
    }

    void write_whitespace(char c)
    {
        if (m_WhitespaceSize != m_Buffer.size())
        {
            m_Stream.write(m_Buffer.data(), m_Buffer.size());
            m_Buffer.clear();
            m_WhitespaceSize = 0;
            m_EmptyLine = false;
        }
        m_Buffer.push_back(c);
        ++m_WhitespaceSize;
[[[IF has_tabs]]]        if (c == '\\t')
            m_Column += 8 - m_Column % 8;
        else
    [[[ENDIF]]]        ++m_Column;
    }
[[[IF has_alignment]]]

    void align()
    {
        if (m_Column < m_LineWidth / 2)
            m_AlignmentColumns.push_back(m_Column);
    }
[[[ENDIF]]]

    void new_line()
    {
        m_Stream.write(m_Buffer.data(), m_Buffer.size());
        m_Stream.put('\\n');
        m_Buffer.clear();
        m_Column = 0;
[[[IF has_alignment]]]
        m_AlignmentColumns.resize(1);
[[[ENDIF]]]
        m_WhitespaceSize = 0;
        m_EmptyLine = true;
    }
private:
    std::ostream& m_Stream;
    unsigned m_LineWidth;
    unsigned m_Column = 0;
    unsigned m_WhitespaceSize = 0;
    std::vector<char> m_Buffer;
[[[IF has_alignment]]]
    std::vector<unsigned> m_AlignmentColumns;
[[[ENDIF]]]
    bool m_EmptyLine = true;
};

void write_help_text(std::ostream& stream, const char* text, unsigned lineWidth)
{
    if (lineWidth == 0)
        lineWidth = [[[line_width]]];
    HelpTextWriter writer(stream, lineWidth);
    for (unsigned i = 0; text[i]; ++i)
    {
        switch (text[i])
        {
        case '\\n':
            writer.new_line();
            break;
        case ' ':
[[[IF has_tabs]]]
        case '\\t':
[[[ENDIF]]]
            writer.write_whitespace(' ');
            break;
[[[IF has_alignment]]]
        case '\\001':
            writer.align();
            break;
[[[ENDIF]]]
[[[IF has_non_breaking_space]]]
        case '\\002':
            writer.write_character(' ');
            break;
[[[ENDIF]]]
[[[IF has_program_name]]]
        case '$':
            if (strncmp(text + i, "${PROGRAM}", 10) == 0)
            {
                writer.align();
                for (unsigned j = 0; programName[j]; ++j)
                    writer.write_character(programName[j]);
                i += 9;
            }
            else
            {
                writer.write_character(text[i]);
            }
            break;
[[[ENDIF]]]
        default:
            writer.write_character(text[i]);
            break;
        }
    }
}

unsigned get_default_line_width()
{
[[[IF has_min_max_line_width]]]
    return std::min(std::max(get_console_width(), [[[min_line_width]]]u), [[[max_line_width]]]u);
[[[ELIF min_line_width]]]
    return std::max(get_console_width(), [[[min_line_width]]]u);
[[[ELIF max_line_width]]]
    return std::min(get_console_width(), [[[max_line_width]]]u);
[[[ELSE]]]
    return get_console_width());
[[[ENDIF]]]
}

void write_help_text(std::ostream& stream, unsigned lineWidth)
{
    if (lineWidth == 0)
        lineWidth = get_default_line_width();
    write_help_text(stream, HELP_TEXT, lineWidth);  
}

void write_brief_help_text(std::ostream& stream, unsigned lineWidth)
{
    if (lineWidth == 0)
        lineWidth = get_default_line_width();
    write_help_text(stream, BRIEF_HELP_TEXT, lineWidth);
}

void write_error_text(const std::string& errorText,
                      std::ostream& stream = std::cerr,
                      unsigned lineWidth = 0)
{
    write_brief_help_text(stream, lineWidth);
    stream << '\\n' << errorText << '\\n';
}
"""
