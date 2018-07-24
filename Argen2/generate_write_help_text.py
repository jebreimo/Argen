# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-24.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
from generate_synopsis import generate_help_text_string, escape_text


class WriteHelpTextGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.help_text = generate_help_text_string(session.help_text, session)
        self.error_text = generate_help_text_string(session.error_text, session)
        alignment_char = escape_text(session.syntax.alignment_char)
        self.has_alignment = any(alignment_char in s for s in self.help_text)
        self.has_tabs = any("\t" in s for s in self.help_text)
        nb_space = escape_text(session.syntax.non_breaking_space)
        self.has_non_breaking_space = any(nb_space in s for s in self.help_text)
        self.has_program_name = any("${PROGRAM}" in s for s in self.help_text)


def generate_write_help_text(session):
    return templateprocessor.make_lines(WRITE_HELP_TEXT_TEMPLATE,
                                        WriteHelpTextGenerator(session))


WRITE_HELP_TEXT_TEMPLATE = """\
const char helpText[] =
    [[[help_text]]];

const char errorText[] =
    [[[error_text]]];

class HelpTextWriter
{
public:
    HelpTextWriter(std::ostream& stream, size_t lineWidth)
        : m_Stream(stream),
          m_LineWidth(lineWidth)
[[[IF has_alignment]]]
    {
        m_AlignmentColumns.push_back(0);
    }
[[[ELSE]]]
    {}
[[[ENDIF]]]

    void writeCharacter(char c)
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
            m_Column = m_AlignmentColumns.back() + m_Buffer.size();
            for (size_t i = 0; i < m_AlignmentColumns.back(); ++i)
                m_Stream.put(' ');
[[[ELSE]]]
            m_Column = m_Buffer.size();
[[[ENDIF]]]
        }
    }

    void writeWhitespace(char c)
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

    void newline()
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
    size_t m_LineWidth;
    size_t m_Column = 0;
    size_t m_WhitespaceSize = 0;
    std::vector<char> m_Buffer;
[[[IF has_alignment]]]
    std::vector<size_t> m_AlignmentColumns;
[[[ENDIF]]]
    bool m_EmptyLine = true;
};

void print_help_text(std::ostream& stream, const char* text, size_t line_width)
{
    HelpTextWriter writer(stream, line_width);
    for (size_t i = 0; text[i]; ++i)
    {
        switch (text[i])
        {
        case '\\n':
            writer.newline();
            break;
        case ' ':
[[[IF has_tabs]]]
        case '\\t':
            writer.writeWhitespace(' ');
            break;
[[[ENDIF]]]
[[[IF has_alignment]]]
        case '\\001':
            writer.align();
            break;
[[[ENDIF]]]
[[[IF has_non_breaking_space]]]
        case '\\002':
            writer.writeCharacter(' ');
            break;
[[[ENDIF]]]
[[[IF has_program_name]]]
        case '$':
            if (strncmp(text + i, "${PROGRAM}", 10) == 0)
            {
                writer.align();
                for (size_t j = 0; programName[j]; ++j)
                    writer.writeCharacter(programName[j]);
                i += 9;
            }
            else
            {
                writer.writeCharacter(text[i]);
            }
            break;
[[[ENDIF]]]
        default:
            writer.writeCharacter(text[i]);
            break;
        }
    }
}"""