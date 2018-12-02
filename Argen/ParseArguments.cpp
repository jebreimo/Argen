//****************************************************************************
// Copyright © 2018 Jan Erik Breimo. All rights reserved.
// Created by Jan Erik Breimo on 2018-12-02.
//
// This file is distributed under the BSD License.
// License text is included with the source distribution.
//****************************************************************************
#include "StdAfx.h"
#include "ParseArguments.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string_view>
#if defined(__APPLE__) || defined(unix) || defined(__unix) || defined(__unix__)
    #include <sys/ioctl.h>
    #include <unistd.h>
#elif defined(WIN32)
    #include <Windows.h>
#endif

namespace Foo { namespace Bar
{
    struct Argument
    {
        Argument() = default;

        Argument(std::string_view argument,
                 bool is_option,
                 bool is_short_option)
                : string(argument),
                  is_option(is_option),
                  is_short_option(is_short_option)
        {}

        explicit operator bool() const {return !string.empty();}

        std::string_view string;
        bool is_option = false;
        bool is_short_option = false;
    };

    std::string to_string(const std::string_view& wrapper)
    {
        return std::string(wrapper.data(), wrapper.size());
    }

    std::string to_string(const Argument& argument)
    {
        if (argument.is_short_option && argument.string.size() == 1)
            return "-" + to_string(argument.string);
        else
            return to_string(argument.string);
    }

    std::ostream& operator<<(std::ostream& os, const Argument& argument)
    {
        return os << to_string(argument);
    }

    inline bool resembles_short_option(const char* s)
    {
        return s[0] == '-' && s[1] != 0
               && (s[1] != '-' || s[2] == 0 || s[2] == '=');
    }

    inline bool resembles_option(const char* s)
    {
        return s[0] == '-' && s[1] != 0;
    }

    class ArgumentIterator
    {
    public:
        ArgumentIterator(int argc, char* argv[])
                : m_ArgIt(*argv), m_ArgvIt(&argv[0]), m_ArgvEnd(&argv[argc])
        {}

        Argument next_argument()
        {
            if (m_ArgvIt == m_ArgvEnd)
                return {};

            if (m_ArgIt != *m_ArgvIt)
            {
                auto arg = m_ArgIt++;
                size_t length = 1;
                if (*m_ArgIt == 0)
                    m_ArgIt = *++m_ArgvIt;
                return {{arg, length}, true, true};
            }

            if (resembles_short_option(m_ArgIt))
            {
                auto arg = m_ArgIt;
                size_t length = 2;
                m_ArgIt += 2;
                if (*m_ArgIt == 0)
                    m_ArgIt = *++m_ArgvIt;
                return {{arg, length}, true, true};
            }

            auto arg = m_ArgIt;
            size_t length = 0;
            bool is_option = resembles_option(m_ArgIt);
            if (is_option)
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

            return {{arg, length}, is_option, false};
        }

        std::string_view next_value()
        {
            if (m_ArgvIt == m_ArgvEnd)
                return {};
            auto value = m_ArgIt;
            size_t length = strlen(value);
            m_ArgIt = *++m_ArgvIt;
            return {value, length};
        }

        bool has_next() const
        {
            return m_ArgIt != *m_ArgvEnd;
        }
    private:
        char* m_ArgIt;
        char** m_ArgvIt;
        char** m_ArgvEnd;
    };

    #if defined(__APPLE__) || defined(unix) || defined(__unix) || defined(__unix__)

    unsigned get_console_width()
    {
        winsize ws = {};
        if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) <= -1)
            return 0;
        return unsigned(ws.ws_col);
    }

    #elif defined(WIN32)

    unsigned get_console_width()
    {
      HANDLE hCon = GetStdHandle(STD_OUTPUT_HANDLE);
      if (hCon == INVALID_HANDLE_VALUE)
        return 0;

      CONSOLE_SCREEN_BUFFER_INFO conInfo;
      if (!GetConsoleScreenBufferInfo(hCon, &conInfo))
        return 0;

      return unsigned(conInfo.srWindow.Right - conInfo.srWindow.Left + 1);
    }

    #else

    constexpr unsigned get_console_width()
    {
        return 80;
    }

    #endif

    std::string program_name = "<program>";

    const char HELP_TEXT[] =
        "USAGE\n"
        "  \001${PROGRAM} \001[-e] [-h] [-l\002FILE] [-q] [-v] [--version]"
        " [--info] [--version2] [--junit] [--text] [--fulltext] [--host=HOST]"
        " [--foo=N1,N2,...] [-@] [--flag] [--size=ROWSxCOLS] [--rect=LENxWID]"
        " [--line=LEN] [--antiflag] [-%\002N] [-s\002TEXT] [--special]"
        " [-n\002X,Y] [-p\002X,Y,Z] [--string=STR] [--kjell] [--] [-i\002PATH]"
        " [--sysinclude] [--stygg=N] [-u\002NAME:ID] [-] [-z] <-f\002FILE>"
        " <--ting> <--tang=N> <--cuboid=LENxWIDxHEI> <-m\002NUM> <test\002name>"
        " <the-list> unnamed <out-file>\n"
        "\n"
        "Executes unit tests.\n"
        "\n"
        "ARGUMENTS\n"
        "  \001\n"
        "  \001<test name> \n"
        "    \001The name of the test or tests that will be run. All tests are"
        " run if no test names are given. If the --exclude option is used, all"
        " tests except the given ones are run.\n"
        "\n"
        "    \001Tests are typically arranged in a two-level hierarchy with a"
        " parent and several child-tests. To disable a parent test and all its"
        " children, just enter the name of the parent. To disable a spesific"
        " child enter the names of both the parent and the child, separated with"
        " a single \"/\"\n"
        "  \001<the-list>\n"
        "  \001<out-file>\n"
        "    \001The name of the file that some kind of output will be written"
        " to. This is a text file.\n"
        "\n"
        "    \001Here's a backslash: \\\n"
        "    \001Ei lita liste:\n"
        "        * \001en og to\n"
        "        * \001tre og fire\n"
        "        * \001fem og seks\n"
        "\n"
        "GENERAL OPTIONS\n"
        "  \001-e, --exclude             \001Exclude the tests whose names appear"
        " after the options and run everything else. This is the opposite of the"
        " default behavior.\n"
        "  \001-h, --help                \001Show program help.\n"
        "  \001-l FILE, --log-file=FILE  \001Redirect all the output the tests"
        " normally write to stdout or stderr to a file named FILE instead. (This"
        " does not affect the test reports).\n"
        "  \001-q, --quiet               \001Don't display extra information"
        " while running tests. (Opposite of -v.)\n"
        "  \001-v, --verbose             \001Display extra information while"
        " running tests.\n"
        "  \001--version\n"
        "  \001--info\n"
        "  \001--version2\n"
        "\n"
        "REPORT OPTIONS\n"
        "  \001--junit                   \001Produce a test report in the JUnit"
        " XML format.\n"
        "  \001--text                    \001Produce a plain text test report"
        " that only list failed tests. This is the default.\n"
        "  \001--fulltext                \001Produce a plain text test report"
        " that lists all tests.\n"
        "  \001-f FILE, --file=FILE      \001The name of the report file. If"
        " multiple report files are produced, FILE will have the suitable file"
        " type extension appended to it (txt, xml etc.). Test reports are written"
        " to stdout if this option isn't used.\n"
        "  \001--host=HOST               \001Set the host name. This option has"
        " no effect on tests, it is only used in the export.\n"
        "\n"
        "OTHER OPTIONS\n"
        "  \001--ting                    \001Text\n"
        "  \001--tang=N                  \001Text\n"
        "  \001--foo=N1,N2,... \n"
        "  \001-@                        \001Text\n"
        "  \001--flag                    \001Text\n"
        "  \001--size=ROWSxCOLS\n"
        "  \001--cuboid=LENxWIDxHEI\n"
        "  \001--rect=LENxWID\n"
        "  \001--line=LEN\n"
        "  \001--antiflag\n"
        "  \001-%=N, --percentage=N\n"
        "  \001-s TEXT\n"
        "  \001--special\n"
        "  \001-n X,Y\n"
        "  \001-p X,Y,Z\n"
        "  \001-m NUM, --month=NUM\n"
        "  \001--string=STR\n"
        "  \001--kjell                   \001Option that specify non-boolean"
        " type, but no argument or value\n"
        "  \001--                        \001End of options\n"
        "  \001-i PATH, --include=PATH\n"
        "  \001--sysinclude\n"
        "  \001--stygg=N\n"
        "  \001-u, --user=NAME:ID\n"
        "  \001-                         \001Read input from stdin.\n"
        "Another option (-z) is the zombie-option.\n"
        "\n";

    const char BRIEF_HELP_TEXT[] =
        "usage: ${PROGRAM} \001[-e] [-h] [-l\002FILE] [-q] [-v] [--version]"
        " [--info] [--version2] [--junit] [--text] [--fulltext] [--host=HOST]"
        " [--foo=N1,N2,...] [-@] [--flag] [--size=ROWSxCOLS] [--rect=LENxWID]"
        " [--line=LEN] [--antiflag] [-%\002N] [-s\002TEXT] [--special]"
        " [-n\002X,Y] [-p\002X,Y,Z] [--string=STR] [--kjell] [--] [-i\002PATH]"
        " [--sysinclude] [--stygg=N] [-u\002NAME:ID] [-] [-z] <-f\002FILE>"
        " <--ting> <--tang=N> <--cuboid=LENxWIDxHEI> <-m\002NUM> <test\002name>"
        " <the-list> unnamed <out-file>\n";

    class HelpTextWriter
    {
    public:
        HelpTextWriter(std::ostream& stream, unsigned line_width)
            : m_Stream(stream),
              m_LineWidth(line_width)
        {
            m_AlignmentColumns.push_back(0);
        }

        void write_character(char c)
        {
            m_Buffer.push_back(c);
            ++m_Column;
            if (m_Column >= m_LineWidth && !m_EmptyLine)
            {
                m_Stream.put('\n');
                m_EmptyLine = true;
                if (m_WhitespaceSize)
                {
                    m_Buffer.erase(m_Buffer.begin(),
                                   m_Buffer.begin() + m_WhitespaceSize);
                    m_WhitespaceSize = 0;
                }
                m_Column = m_AlignmentColumns.back()
                           + unsigned(m_Buffer.size());
                for (unsigned i = 0; i < m_AlignmentColumns.back(); ++i)
                    m_Stream.put(' ');
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
            ++m_Column;
        }

        void align()
        {
            if (m_Column < m_LineWidth / 2)
                m_AlignmentColumns.push_back(m_Column);
        }

        void new_line()
        {
            m_Stream.write(m_Buffer.data(), m_Buffer.size());
            m_Stream.put('\n');
            m_Buffer.clear();
            m_Column = 0;
            m_AlignmentColumns.resize(1);
            m_WhitespaceSize = 0;
            m_EmptyLine = true;
        }
    private:
        std::ostream& m_Stream;
        unsigned m_LineWidth;
        unsigned m_Column = 0;
        unsigned m_WhitespaceSize = 0;
        std::vector<char> m_Buffer;
        std::vector<unsigned> m_AlignmentColumns;
        bool m_EmptyLine = true;
    };

    void write_help_text(std::ostream& stream, const char* text, unsigned line_width)
    {
        if (line_width == 0)
            line_width = 79;
        HelpTextWriter writer(stream, line_width);
        for (unsigned i = 0; text[i]; ++i)
        {
            switch (text[i])
            {
            case '\n':
                writer.new_line();
                break;
            case ' ':
                writer.write_whitespace(' ');
                break;
            case '\001':
                writer.align();
                break;
            case '\002':
                writer.write_character(' ');
                break;
            case '$':
                if (strncmp(text + i, "${PROGRAM}", 10) == 0)
                {
                    writer.align();
                    for (unsigned j = 0; program_name[j]; ++j)
                        writer.write_character(program_name[j]);
                    i += 9;
                }
                else
                {
                    writer.write_character(text[i]);
                }
                break;
            default:
                writer.write_character(text[i]);
                break;
            }
        }
    }

    unsigned get_default_line_width()
    {
        return std::min(std::max(get_console_width(), 40u), 99u);
    }

    void write_help_text(std::ostream& stream, unsigned line_width)
    {
        if (line_width == 0)
            line_width = get_default_line_width();
        write_help_text(stream, HELP_TEXT, line_width);
    }

    void write_brief_help_text(std::ostream& stream, unsigned line_width)
    {
        if (line_width == 0)
            line_width = get_default_line_width();
        write_help_text(stream, BRIEF_HELP_TEXT, line_width);
    }

    void write_error_text(const std::string& error_text,
                          std::ostream& stream = std::cerr,
                          unsigned line_width = 0)
    {
        write_brief_help_text(stream, line_width);
        stream << '\n' << error_text << '\n';
    }

    enum Options
    {
        Option_exclude,
        Option_help,
        Option_log_file,
        Option_quiet,
        Option_verbose,
        Option_version,
        Option_info,
        Option_version2,
        Option_junit,
        Option_text,
        Option_fulltext,
        Option_file,
        Option_host,
        Option_ting,
        Option_tang,
        Option_foo,
        Option_symbols,
        Option_flag,
        Option_size,
        Option_cuboid,
        Option_rect,
        Option_line,
        Option_antiflag,
        Option_percentage,
        Option_s,
        Option_special,
        Option_n,
        Option_p,
        Option_month,
        Option_string,
        Option_kjell,
        Option_symbols_2,
        Option_include,
        Option_sysinclude,
        Option_stygg,
        Option_user,
        Option_symbols_3,
        Option_z
    };

    const char SHORT_OPTIONS[] = "%-@efhilmnpqsuvz";
    const char SHORT_OPTION_INDICES[] =
    {
        Option_percentage,
        Option_symbols_2,
        Option_symbols,
        Option_exclude,
        Option_file,
        Option_help,
        Option_include,
        Option_log_file,
        Option_month,
        Option_n,
        Option_p,
        Option_quiet,
        Option_s,
        Option_user,
        Option_verbose,
        Option_z
    };

    const char* OPTION_STRINGS[] =
    {
        "-",
        "--a\001ntiflag",
        "--c\001uboid",
        "--e\001xclude",
        "--fi\001le",
        "--fl\001ag",
        "--fo\001o",
        "--fu\001lltext",
        "--he\001lp",
        "--ho\001st",
        "--inc\001lude",
        "--inf\001o",
        "--j\001unit",
        "--k\001jell",
        "--li\001ne",
        "--lo\001g-file",
        "--m\001onth",
        "--p\001ercentage",
        "--q\001uiet",
        "--r\001ect",
        "--si\001ze",
        "--sp\001ecial",
        "--str\001ing",
        "--sty\001gg",
        "--sy\001sinclude",
        "--ta\001ng",
        "--te\001xt",
        "--ti\001ng",
        "--u\001ser",
        "--verb\001ose",
        "--version",
        "--version2"
    };

    const char OPTION_INDICES[] =
    {
        Option_symbols_3,
        Option_antiflag,
        Option_cuboid,
        Option_exclude,
        Option_file,
        Option_flag,
        Option_foo,
        Option_fulltext,
        Option_help,
        Option_host,
        Option_include,
        Option_info,
        Option_junit,
        Option_kjell,
        Option_line,
        Option_log_file,
        Option_month,
        Option_percentage,
        Option_quiet,
        Option_rect,
        Option_size,
        Option_special,
        Option_string,
        Option_stygg,
        Option_sysinclude,
        Option_tang,
        Option_text,
        Option_ting,
        Option_user,
        Option_verbose,
        Option_version,
        Option_version2
    };

    int compare_flag(const std::string_view& flag, const char* pattern)
    {
        size_t i = 0;
        while (true)
        {
            if (i == flag.size())
            {
                if (pattern[i] == 1)
                    return 0;
                else
                    return -pattern[i];
            }
            else if (pattern[i] == 1)
            {
                break;
            }
            else if (std::toupper(flag[i]) != std::toupper(pattern[i]))
            {
                return std::toupper(flag[i]) - std::toupper(pattern[i]);
            }
            ++i;
        }

        for (; i < flag.size(); ++i)
        {
            if (std::toupper(flag[i]) != std::toupper(pattern[i + 1]))
                return std::toupper(flag[i]) - std::toupper(pattern[i + 1]);
            else if (pattern[i + 1] == 0)
                break;
        }
        return 0;
    }

    template <typename RndAccIt>
    RndAccIt find_flag(RndAccIt begin, RndAccIt end,
                       const std::string_view& flag)
    {
        auto originalEnd = end;
        while (begin != end)
        {
            auto mid = begin + std::distance(begin, end) / 2;
            auto cmp = compare_flag(flag, *mid);
            if (cmp == 0)
                return mid;
            if (cmp < 0)
                end = mid;
            else
                begin = mid + 1;
        }
        return originalEnd;
    }

    int find_option_code(const Argument& argument)
    {
        auto str = argument.string;
        if (argument.is_short_option)
        {
            char c = str[str.size() - 1];
            auto pos = std::lower_bound(
                    std::begin(SHORT_OPTIONS),
                    std::end(SHORT_OPTIONS),
                    c,
                    [](auto a, auto b){return std::toupper(a) < std::toupper(b);});
            if (pos == std::end(SHORT_OPTIONS))
                return -1;
            return int(SHORT_OPTION_INDICES[pos - std::begin(SHORT_OPTIONS)]);
        }
        auto pos = find_flag(std::begin(OPTION_STRINGS),
                             std::end(OPTION_STRINGS),
                             argument.string);
        if (pos == std::end(OPTION_STRINGS))
            return -1;
        return int(OPTION_INDICES[pos - std::begin(OPTION_STRINGS)]);
    }

    bool show_help(Arguments& arguments, const std::string& argument)
    {
        write_help_text(std::cout);
        return true;
    }

    Arguments& abort(Arguments& arguments,
                     Arguments::Result result,
                     bool autoExit)
    {
        if (autoExit)
            exit(EINVAL);
        arguments.parse_arguments_result = result;
        return arguments;
    }

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
        if (!iterator.has_next())
        {
            write_error_text(to_string(argument) + ": no value given.");
            return false;
        }
        value = iterator.next_value();
        return true;
    }

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
            ss << argument << ": incorrect number of parts in value \""
               << value << "\".\nIt must have ";
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

    template <typename T>
    bool parse_and_assign(T& value,
                          const std::string_view& string,
                          const Argument& argument)
    {
        if (from_string(string, value))
            return true;

        write_error_text(to_string(argument) + ": invalid value \""
                         + to_string(string) + "\".");
        return false;
    }

    template <typename T>
    bool parse_and_assign(std::vector<T>& value,
                          const std::vector<std::string_view>& strings,
                          const Argument& argument)
    {
        value.clear();
        for (auto& string : strings)
        {
            T temp;
            if (!from_string(string, temp))
            {
                write_error_text(to_string(argument) + ": invalid value \""
                                 + to_string(string) + "\".");
                return false;
            }
            value.push_back(temp);
        }
        return true;
    }

    template <typename T>
    bool parse_and_append(std::vector<T>& value,
                          const std::string_view& string,
                          const Argument& argument)
    {
        value.clear();
        T temp;
        if (!from_string(string, temp))
        {
            write_error_text(to_string(argument) + ": invalid value \""
                             + to_string(string) + "\".");
            return false;
        }
        value.push_back(temp);
        return true;
    }

    template <typename T>
    bool append(std::vector<T>& values, T&& value)
    {
        values.push_back(std::forward<T>(value));
        return true;
    }

    template <typename T>
    bool extend(std::vector<T>& values, std::vector<T> newValues)
    {
        values.insert(values.end(), newValues.begin(), newValues.end());
        return true;
    }

    template <typename T>
    bool parse_and_extend(std::vector<T>& value,
                          const std::vector<std::string_view>& strings,
                          const Argument& argument)
    {
        for (auto& string : strings)
        {
            T temp;
            if (!from_string(string, temp))
            {
                write_error_text(to_string(argument) + ": invalid value \""
                                 + to_string(string) + "\".");
                return false;
            }
            value.push_back(temp);
        }
        return true;
    }

    template <typename T, typename CheckFunc>
    bool check_value(T value, CheckFunc check_func,
                     const char* legal_values_text,
                     const Argument& argument)
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

    template <typename T, typename CheckFunc>
    bool check_values(const std::vector<T>& values,
                      CheckFunc check_func,
                      const char* legal_values_text,
                      const Argument& argument)
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

    std::string get_base_name(const std::string& path)
    {
        size_t pos = path.find_last_of("/\\");
        if (pos == std::string::npos)
            return path;
        else
            return path.substr(pos + 1);
    }

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
        std::string_view value;
        std::vector<std::string_view> parts;
        switch (option_code)
        {
        case Option_exclude:
            result.exclude = true;
            break;
        case Option_help:
            result.help = true;
            if (!show_help(result, to_string(arg)))
            {
                return OptionResult::INVALID_OPTION;
            }
            result.parse_arguments_result = Arguments::OPTION_help;
            return OptionResult::ABORTING_OPTION;
        case Option_log_file:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.log_file, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_quiet:
            result.verbose = false;
            break;
        case Option_verbose:
            result.verbose = true;
            break;
        case Option_version:
            result.version = true;
            result.parse_arguments_result = Arguments::OPTION_version;
            break;
        case Option_info:
            result.info = true;
            result.parse_arguments_result = Arguments::OPTION_info;
            break;
        case Option_version2:
            result.version = result.info = true;
            result.parse_arguments_result = Arguments::OPTION_version2;
            break;
        case Option_junit:
            result.junit = true;
            break;
        case Option_text:
            result.text = true;
            break;
        case Option_fulltext:
            result.fulltext = true;
            break;
        case Option_file:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.file, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_host:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.host, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_ting:
            result.ting.push_back(10.0);
            break;
        case Option_tang:
            if (!read_value(value, arg_it, arg)
                || !parse_and_append(result.ting, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_foo:
            {
                std::vector<int> temp;
                if (!read_value(value, arg_it, arg)
                    || !split_value(parts, value, ',', 0, SIZE_MAX, arg)
                    || !parse_and_assign(temp, parts, arg)
                    || !extend(result.foo, std::move(temp)))
                {
                    return OptionResult::INVALID_OPTION;
                }
                break;
            }
        case Option_symbols:
            result.at = {2, 5, 3};
            break;
        case Option_flag:
            result.flag = true;
            break;
        case Option_size:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, 'x', 1, 1, arg)
                || !parse_and_assign(std::get<0>(result.size), parts[0], arg)
                || !parse_and_assign(std::get<1>(result.size), parts[1], arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_cuboid:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, 'x', 2, 2, arg)
                || !parse_and_assign(result.cuboid, parts, arg)
                || !check_values(result.cuboid, [](auto&& v){return -1000 <= v && v <= 1000;}, "-1000...1000", arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_rect:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, 'x', 1, 1, arg)
                || !parse_and_assign(result.cuboid, parts, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_line:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.cuboid, std::vector<std::string_view>{value}, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_antiflag:
            result.flag = false;
            break;
        case Option_percentage:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.percentage, value, arg)
                || !check_value(result.percentage, [](auto&& v){return (0 <= v && v <= 100) || 200 <= v;}, "0...100, 200...", arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_s:
            if (!read_value(value, arg_it, arg)
                || !parse_and_append(result.s, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_special:
            result.s = {"$spec$"};
            break;
        case Option_n:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, ',', 1, 1, arg)
                || !parse_and_assign(std::get<0>(result.n), parts[0], arg)
                || !parse_and_assign(std::get<1>(result.n), parts[1], arg)
                || !check_value(std::get<0>(result.n), [](auto&& v){return v == -9999 || (-1000 <= v && v <= -500) || (-100 <= v && v <= -10) || v == -5 || v == 0 || v == 5 || (10 <= v && v <= 100) || (500 <= v && v <= 1000) || 2000 <= v;}, "-9999, -1000...-500, -100...-10, -5, 0, 5, 10...100, 500...1000, 2000...", arg)
                || !check_value(std::get<1>(result.n), [](auto&& v){return v == -9999 || (-1000 <= v && v <= -500) || (-100 <= v && v <= -10) || v == -5 || v == 0 || v == 5 || (10 <= v && v <= 100) || (500 <= v && v <= 1000) || 2000 <= v;}, "-9999, -1000...-500, -100...-10, -5, 0, 5, 10...100, 500...1000, 2000...", arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_p:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, ',', 2, 2, arg)
                || !parse_and_assign(std::get<0>(result.p), parts[0], arg)
                || !parse_and_assign(std::get<1>(result.p), parts[1], arg)
                || !parse_and_assign(std::get<2>(result.p), parts[2], arg)
                || !check_value(std::get<0>(result.p), [](auto&& v){return -1000 <= v && v <= 1000;}, "-1000...1000", arg)
                || !check_value(std::get<1>(result.p), [](auto&& v){return -1000 <= v && v <= 1000;}, "-1000...1000", arg)
                || !check_value(std::get<2>(result.p), [](auto&& v){return 0 <= v;}, "0...", arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_month:
            if (!read_value(value, arg_it, arg)
                || !parse_and_append(result.month, value, arg)
                || !check_value(result.month.back(), [](auto&& v){return 1 <= v && v <= 12;}, "1...12", arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_string:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.string, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_kjell:
            result.kjell = 10;
            break;
        case Option_symbols_2:
            return OptionResult::FINAL_OPTION;
        case Option_include:
            if (!read_value(value, arg_it, arg)
                || !split_value(parts, value, ':', 0, SIZE_MAX, arg)
                || !parse_and_extend(result.include, parts, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            printf("hello!\n");
            break;
        case Option_sysinclude:
            result.include.insert(result.include.end(), {"foo", "bar", "baz"});
            break;
        case Option_stygg:
            if (!read_value(value, arg_it, arg)
                || !parse_and_assign(result.stygg, value, arg))
            {
                return OptionResult::INVALID_OPTION;
            }
            break;
        case Option_user:
            {
                std::tuple<std::string, int> temp;
                if (!read_value(value, arg_it, arg)
                    || !split_value(parts, value, ':', 1, 1, arg)
                    || !parse_and_assign(std::get<0>(temp), parts[0], arg)
                    || !parse_and_assign(std::get<1>(temp), parts[1], arg)
                    || !check_value(std::get<0>(temp), [](auto&& v){return v == "ab" || v == "ac" || v == "ad" || v == "bc" || v == "bd" || v == "cd";}, "\"ab\", \"ac\", \"ad\", \"bc\", \"bd\", \"cd\"", arg)
                    || !check_value(std::get<1>(temp), [](auto&& v){return 0 <= v && v <= 100;}, "0...100", arg)
                    || !append(result.user, std::move(temp)))
                {
                    return OptionResult::INVALID_OPTION;
                }
                break;
            }
        case Option_symbols_3:
            break;
        case Option_z:
            result.z = true;
            break;
        default:
            return OptionResult::UNKNOWN_OPTION;
        }
        return OptionResult::NORMAL_OPTION;
    }

    Arguments parse_arguments(int argc, char* argv[], bool auto_exit)
    {
        if (argc == 0)
            return Arguments();

        program_name = get_base_name(argv[0]);

        Arguments result;
        std::vector<std::string_view> arguments;
        ArgumentIterator arg_it(argc - 1, argv + 1);
        bool final_option = false;
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
                    result.parse_arguments_result = Arguments::RESULT_ERROR;
                    break;
                case OptionResult::UNKNOWN_OPTION:
                    write_error_text(to_string(arg) + ": unknown option.");
                    if (auto_exit)
                        exit(EINVAL);
                    result.parse_arguments_result = Arguments::RESULT_ERROR;
                    break;
                default:
                    break;
                }
                if (result.parse_arguments_result != Arguments::RESULT_OK)
                    return result;
            }
            else
            {
                arguments.push_back(arg.string);
            }
            if (final_option)
                break;
        }
        return result;
    }

    //[ [[error_messages]]]
    //[ [[set_value_functions]]]

}}