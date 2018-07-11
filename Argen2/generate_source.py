# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-07-09.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
from generate_argument_iterator import generate_argument_iterator


class SourceFileGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.source_includes = ["#include " + s for s in
                                session.code_properties.source_includes]

    def source_code(self, params, context):
        return generate_source_contents(self._session)


def generate_source(session):
    return templateprocessor.make_text(session.code_properties.source_template,
                                       SourceFileGenerator(session))


class SurceContentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.has_namespace = session.code_properties.namespace_start
        self.namespace_start = session.code_properties.namespace_start
        self.namespace_end = session.code_properties.namespace_end
        # self.class_name = session.settings.class_name
        # self.function_name = session.settings.function_name
        # self.has_member_counters = session.code_properties.counted_members

    def code(self, params, context):
        return templateprocessor.make_lines(SOURCE_CONTENTS_TEMPLATE,
                                            self)

    def argument_iterator(self, params, context):
        return generate_argument_iterator(self._session)


def generate_source_contents(session):
    return templateprocessor.make_lines(SOURCE_NAMESPACE_TEMPLATE,
                                        SurceContentsGenerator(session))


SOURCE_NAMESPACE_TEMPLATE = """\
[[[IF has_namespace]]]
[[[namespace_start]]]
    [[[code]]]
[[[namespace_end]]]
[[[ELSE]]]
[[[code]]]
[[[ENDIF]]]\
"""


SOURCE_CONTENTS_TEMPLATE = """\
[[string_view_class]]
[[argument_class]]
[[[argument_iterator]]]
[[help_text]]
[[synopsis_text]]
[[get_console_width]]
[[print_text_function]]
[[option_enum]]
[[short_option_string]]
[[option_strinigs]]
[[error_messages]]
[[set_value_functions]]
[[check_value_functions]]\
"""

SOURCE_CONTENTS = """\
#include "[[[header_file_name]]]"

[[[IF namespace]]]

[[[beginNamespace]]]
[[[ENDIF]]]
[[[IF hasTrackedOptions]]]

/** @brief Keeps track of which options have been parsed at least once.
  *
  * Only options with minimum and maximum count of 1, and list options
  * with default values are tracked.
  */
struct TrackedOptions
{
    TrackedOptions()
        : [[[initializeTrackedOptions]]]
    {}

    [[[trackedOptions]]]
};
[[[ENDIF]]]

namespace
{
    std::string programName;
    std::string helpText =
        [[[helpText]]];

    void writeHelp()
    {
        std::string s = "$prog$";
        auto first = begin(helpText);
        while (first != end(helpText))
        {
            auto last = std::search(first, end(helpText), begin(s), end(s));
            if (last == end(helpText))
                break;
            std::cout.write(&*first, distance(first, last));
            std::cout << programName;
            first = last + 6;
        }
        std::cout.write(&*first, distance(first, end(helpText)));
        std::cout.flush();
    }

[[[SET unknownOptionCheck=]]]
[[[IF hasShortOptions]]]
    [[[SET unknownOptionCheck=resemblesShortOption]]]
    bool resemblesShortOption(const char* s)
    {
    [[[IF hasDashOptions]]]
        if ((s[0] == '-') && (s[1] != '\0') &&
            (s[1] != '-' || s[2] == '\0' || s[2] == '='))
            return true;
        [[[IF hasSlashOptions]]]
        else if (s[0] == '/' && s[1] != '\0')
            return true;
        [[[ENDIF]]]
        else
            return false;
    [[[ELSE]]]
        return s[0] == '/' && s[1] != '\0';
    [[[ENDIF]]]
    }

[[[ENDIF]]]
[[[IF hasNormalOptions]]]
    [[[SET unknownOptionCheck=resemblesOption]]]
    bool resemblesOption(const char* s)
    {
    [[[IF hasDashOptions]]]
        [[[IF hasSlashOptions]]]
        return (s[0] == '-' || s[0] == '/') && s[1] != '\0';
        [[[ELSE]]]
        return s[0] == '-' && s[1] != '\0';
        [[[ENDIF]]]
    [[[ELSE]]]
        return s[0] == '/' && s[1] != '\0';
    [[[ENDIF]]]
    }

[[[ENDIF]]]
    class ArgumentIterator
    {
    public:
        ArgumentIterator(int argc, char* argv[])
            : m_ArgIt(*argv),
              m_ArgsIt(&argv[0]),
              m_ArgsEnd(&argv[argc])
        {}

        bool nextArgument(std::string& arg)
        {
            arg.clear();
            if (m_ArgsIt == m_ArgsEnd)
            {
                return false;
            }
[[[IF hasShortOptions]]]
            else if (m_ArgIt != *m_ArgsIt)
            {
                arg = "[[[IF hasDashOptions]]]-[[[ELSE]]]/[[[ENDIF]]]";
                arg.push_back(*m_ArgIt);
                if (!*++m_ArgIt)
                    m_ArgIt = *++m_ArgsIt;
                return true;
            }
[[[ENDIF]]]

[[[IF hasShortOptions]]]
            if (resemblesShortOption(m_ArgIt))
            {
                arg.assign(m_ArgIt, m_ArgIt + 2);
                if (*(m_ArgIt + 2))
                    m_ArgIt += 2;
                else
                    m_ArgIt = *++m_ArgsIt;
                return true;
            }

[[[ENDIF]]]
            char* end = m_ArgIt;
[[[IF hasNormalOptions]]]
            if (resemblesOption(m_ArgIt))
            {
    [[[IF hasShortOptions]]]
                end += 3;
    [[[ELSE]]]
                end += 2;
    [[[ENDIF]]]
                while (*end && *end != '=')
                    ++end;
            }
            else
            {
                while (*end)
                    ++end;
            }
[[[ELSE]]]
            while (*end)
                ++end;
[[[ENDIF]]]

            arg.assign(m_ArgIt, end);
[[[IF hasNormalOptions]]]
            if (*end)
                m_ArgIt = end + 1;
            else
                m_ArgIt = *++m_ArgsIt;
[[[ELSE]]]
            m_ArgIt = *++m_ArgsIt;
[[[ENDIF]]]
            return true;
        }

[[[IF requiresNextValue]]]
        bool nextValue(std::string& value)
        {
            if (m_ArgsIt == m_ArgsEnd)
                return false;
            value = m_ArgIt;
            m_ArgIt = *++m_ArgsIt;
            return true;
        }

[[[ENDIF]]]
[[[IF hasDelimitedValues]]]
        bool nextDelimitedValue(std::string& value, char delimiter)
        {
            if (m_ArgsIt == m_ArgsEnd)
            {
                return false;
            }
            else if (!*m_ArgIt)
            {
                m_ArgIt = *++m_ArgsIt;
                return false;
            }
            char* end = m_ArgIt;
            while (*end && *end != delimiter)
                ++end;
            value.assign(m_ArgIt, end);
            m_ArgIt = end + (*end ? 1 : 0);
            return true;
        }

[[[ENDIF]]]
[[[IF hasNormalOptions]]]
        bool hasValue() const
        {
            return m_ArgIt != *m_ArgsIt;
        }
[[[ENDIF]]]
    private:
        char* m_ArgIt;
        char** m_ArgsIt;
        char** m_ArgsEnd;
    };

[[[IF requiresFromString]]]
    template <typename T>
    bool fromString(const std::string& s, T& value)
    {
        std::istringstream stream(s);
        stream >> std::boolalpha >> value;
        return !stream.fail();
    }

[[[ENDIF]]]
    bool error(const std::string& flag,
               [[[className]]]& result,
               const std::string& errorMsg)
    {
        std::cerr << "Error: " << flag << ": " << errorMsg << "\n"
                  << "Run \"" << programName
                  << " [[[helpFlag]]]\" for help.\n";
        result.[[[functionName]]]_result = [[[className]]]::RESULT_ERROR;
        return false;
    }

[[[IF hasValueWithoutCheck]]]
    template <typename T>
    bool getValue(T& value,
                  const std::string& flag,
                  ArgumentIterator& argIt,
                  [[[className]]]& result)
    {
        std::string strValue;
        if (!argIt.nextValue(strValue))
            return error(flag, result, "no value provided");
        if (!fromString(strValue, value))
            return error(flag, result, "invalid option value \"" + strValue + "\".");
        return true;
    }

[[[ENDIF]]]
[[[IF hasValueWithCheck]]]
    template <typename T, typename UnaryPred>
    bool getValue(T& value,
                  UnaryPred checkValue,
                  const std::string& flag,
                  ArgumentIterator& argIt,
                  [[[className]]]& result)
    {
        std::string strValue;
        if (!argIt.nextValue(strValue))
            return error(flag, result, "no value provided");
        if (!fromString(strValue, value))
            return error(flag, result, "invalid option value \"" + strValue + "\".");
        if (!checkValue(value))
            return error(flag, result, "illegal option value \"" + strValue + "\".");
        return true;
    }

[[[ENDIF]]]
[[[IF hasDelimitedValuesWithoutCheck]]]
    template <typename T>
    bool addDelimitedValues(std::vector<T>& dest,
                            char delimiter,
                            const std::string& flag,
                            ArgumentIterator& argIt,
                            [[[className]]]& result)
    {
        std::string strValue;
        while (argIt.nextDelimitedValue(strValue, delimiter))
        {
            T value;
            if (!fromString(strValue, value))
                return error(flag, result, "invalid option value \"" + strValue + "\".");
            dest.push_back(value);
        }
        return true;
    }

[[[ENDIF]]]
[[[IF hasDelimitedValuesWithCheck]]]
    template <typename T, typename UnaryPred>
    bool addDelimitedValues(std::vector<T>& dest,
                            char delimiter,
                            UnaryPred checkValue,
                            const std::string& flag,
                            ArgumentIterator& argIt,
                            [[[className]]]& result)
    {
        std::string strValue;
        while (argIt.nextDelimitedValue(strValue, delimiter))
        {
            T value;
            if (!fromString(strValue, value))
                return error(flag, result, "invalid option value \"" + strValue + "\".");
            if (!checkValue(value))
                return error(flag, result, "illegal option value \"" + strValue + "\".");
            dest.push_back(value);
        }
        return true;
    }

[[[ENDIF]]]
    [[[implementOtionProcessors]]]
    typedef bool (*ProcessOptionFunc)(const std::string&,
                                      ArgumentIterator&,
                                      [[[className]]]&);
    typedef std::pair<std::string, ProcessOptionFunc> OptionProcessor;

    OptionProcessor optionProcessors[] = {
        [[[declareOptionProcessors]]]
    };

    ProcessOptionFunc findOptionProcessor(const std::string& flag)
    {
        const OptionProcessor* op = std::find_if(
                std::begin(optionProcessors),
                std::end(optionProcessors),
                [&](const OptionProcessor& o) {return o.first == flag;});
        if (op == std::end(optionProcessors))
            return nullptr;
        return op->second;
    }

[[[IF hasMandatoryOptions]]]
    bool checkMandatoryOptions([[[className]]]& result)
    {
        [[[mandatoryOptionChecks]]]
        return true;
    }

[[[ENDIF]]]
[[[IF hasMinimumListLengths]]]
    bool checkListLengths([[[className]]]& result)
    {
        [[[checkListLengths]]]
        return true;
    }

[[[ENDIF]]]
    [[[implementArgumentProcessors]]]
[[[IF hasTrackedOptions]]]

    [[[className]]]& cleanReservedInternals([[[className]]]>& result)
    {
        result.reserved_for_internal_use = nullptr;
        return result;
    }
[[[ENDIF]]]
}

[[[className]]]::[[[className]]]()
    : [[[memberInitializers]]],
      [[[functionName]]]_result(RESULT_OK)
{
    [[[multiValueInitialization]]]
}

[[[className]]]::operator bool() const
{
    return [[[functionName]]]_result == RESULT_OK;
}

[[[className]]] [[[functionName]]](int argc, char* argv[], bool autoExit)
{
    if (argc == 0)
        return [[[className]]]();

    size_t pos = std::string(argv[0]).find_last_of("/\\");
    if (pos == std::string::npos)
        programName = argv[0];
    else
        programName = &argv[0][pos + 1];

    [[[className]]] result;
[[[IF hasTrackedOptions]]]
    TrackedOptions trackedOptions;
    result.reserved_for_internal_use = &trackedOptions;
[[[ENDIF]]]
    std::vector<std::string> args;

    ArgumentIterator argIt(argc - 1, argv + 1);
    std::string arg;
    while (argIt.nextArgument(arg))
    {
        ProcessOptionFunc func = findOptionProcessor(arg);
        if (func)
        {
            if (!func(arg, argIt, result))
            {
                if (autoExit)
                    exit(result.parse_arguments_result);
                return result;
            }
        }
[[[IF hasFinalOption]]]
        else if ([[[checkFinalOption]]])
        {
            while (argIt.nextValue(arg))
                args.push_back(arg);
        }
[[[ENDIF]]]
[[[IF unknownOptionCheck]]]
        else if ([[[unknownOptionCheck]]](arg.c_str()))
        {
            error(arg, result, "unknown option.");
            if (autoExit)
                exit(result.parse_arguments_result);
            return result;
        }
[[[ENDIF]]]
        else
        {
            args.push_back(arg);
        }
    }

[[[IF hasInfoOptions]]]
    if (result.[[[functionName]]]_result == [[[className]]]::RESULT_INFO)
        return result;

[[[ENDIF]]]
[[[IF hasMandatoryOptions]]]
    if (!checkMandatoryOptions(result))
    {
        if (autoExit)
            exit(result.parse_arguments_result);
        return result;
    }

[[[ENDIF]]]
[[[IF hasMinimumListLengths]]]
    if (!checkListLengths(result))
    {
        if (autoExit)
            exit(result.parse_arguments_result);
        return result;
    }

[[[ENDIF]]]
[[[IF hasFixedNumberOfArguments]]]
    if (args.size() != [[[minArguments]]])
    {
        std::cerr << "Error: incorrect number of arguments";
        if (args.size() != 0)
            std::cerr << "(expected [[[minArguments]]], but received "
                      << args.size() << ")";
        std::cerr << ".\nRun \"" << programName << " [[[helpFlag]]]\" for help.\n";
        result.[[[functionName]]]_result = [[[className]]]::RESULT_ERROR;
        if (autoExit)
            exit(result.parse_arguments_result);
        return result;
    }

[[[ELSE]]]
    [[[IF hasMinArguments]]]
    if (args.size() < [[[minArguments]]])
    {
        std::cerr << "Error: too few arguments";
        if (args.size() != 0)
            std::cerr << "(expected at least [[[minArguments]]], "
                      << "but received " << args.size() << ")";
        std::cerr << ".\nRun \"" << programName << " [[[helpFlag]]]\" for help.\n";
        result.[[[functionName]]]_result = [[[className]]]::RESULT_ERROR;
        if (autoExit)
            exit(result.parse_arguments_result);
        return result;
    }
    [[[ENDIF]]]
    [[[IF hasMaxArguments]]]
    if (args.size() > [[[maxArguments]]])
    {
        std::cerr << "Error: too many arguments (expected at most [[[maxArguments]]], but received "
                  << args.size() << ")\n"
                  << "Run \"" << programName << " [[[helpFlag]]]\" for help.\n";
        result.[[[functionName]]]_result = [[[className]]]::RESULT_ERROR;
        if (autoExit)
            exit(result.parse_arguments_result);
        return result;
    }

    [[[ENDIF]]]
    size_t excess = args.size() - [[[minArguments]]];
[[[ENDIF]]]
    std::vector<std::string>::const_iterator it = args.begin();

    [[[processArguments]]]
[[[IF hasMemberActionsOrConditions]]]
    [[[memberConditionsAndActions]]]
[[[ENDIF]]]
    return result;
}

[[[IF namespace]]]
[[[endNamespace]]]
[[[ENDIF]]]
[[[IF includeTest]]]

#include <iomanip>

template <typename It>
void printAllValues(It begin, It end)
{
    if (begin == end)
        return;
    std::cout << *begin;
    for (++begin; begin != end; ++begin)
        std::cout << ", " << *begin;
}

#define PRINT_VALUE(member) \
    std::cout << std::setw([[[memberWidth]]]) << #member ":" << " "<< args.member << "\n"
#define PRINT_STRING(member) \
    std::cout << std::setw([[[memberWidth]]]) << #member ":" << " \"" << args.member << "\"\n"
#define PRINT_LIST(member) \
    std::cout << std::setw([[[memberWidth]]]) << #member ":" << " {"; \
    printAllValues(begin(args.member), end(args.member)); \
    std::cout << "}\n"

int main(int argc, char* argv[])
{
    std::cout << "\n============================= Input Arguments "
                    "============================\n";
    for (int i = 0; i < argc; ++i)
        std::cout << "argv[" << i << "] = \"" << argv[i] << "\"\n";

    std::cout << "\n============================== Parser output "
                    "=============================\n";
    auto args = [[[qualifiedFunctionName]]](argc, argv, false);

    std::cout << "\n================================= Values "
                    "=================================\n";
    std::cout.setf(std::ios_base::boolalpha);
    std::cout.setf(std::ios_base::left, std::ios_base::adjustfield);
    [[[printMembers]]]
    return 0;
}

[[[ENDIF]]]\
"""
