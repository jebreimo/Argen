# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
from generate_parse_option import generate_option_cases


def join_text(words, separator, final_separator):
    if len(words) <= 2:
        return final_separator.join(words)
    return final_separator.join((separator.join(words[:-1]), words[-1]))


def format_count(count):
    if not count or not count[0] and not count[1]:
        return ""
    if count[0] == count[1]:
        if count[0] == 1:
            return "must be given 1 time"
        else:
            return "must be given %d times" % count[0]
    if count[0] and not count[1]:
        if count[0] == 1:
            return "must be given at least once"
        else:
            return "must be given at least %d times" % count[0]
    if not count[0]:
        if count[1] == 1:
            return "must not be given more than once"
        else:
            return "must not be given more than %d times" % count[1]
    if count[0] == count[1] - 1:
        return "must be given %d or %d times" % (count[0], count[1])
    else:
        return "must be given between %d and %d times" % (count[0], count[1])
    return ""


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
        self.has_member_counters = session.code_properties.counted_options

    def option_cases(self, *args):
        return generate_option_cases(self._session)

    def option_counters(self, *args):
        result = []
        for opt in self._session.code_properties.counted_options:
            result.append("size_t %s_counter = 0;" % opt.option_name)
        return result

    def option_counter_checks(self, *args):
        result = []
        for opt in self._session.code_properties.counted_options:
            result.append("if (counters.%s_counter != 3)" % opt.option_name)
            result.append("{")
            result.append("    write_error_text(\"%s %s.\");"
                          % (join_text(opt.flags, ", ", " or "),
                             format_count(opt.count)))
            result.append("    return false;")
            result.append("}")
        # if (result.month.size() != 3)
        # {
        #     write_error_text("-m or --month must be given 3 times.");
        #     return false;
        # }
        return result

def generate_parse_arguments(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsGenerator(session))


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

[[[IF has_member_counters]]]
struct MemberCounters
{
    [[[option_counters]]]
};
[[[ENDIF]]]

OptionResult process_option(Arguments& result,
[[[IF has_member_counters]]]
                            MemberCounters& counters,
[[[ENDIF]]]
                            Argument& arg,
                            int option_code,
                            ArgumentIterator& arg_it)
{
[[[IF has_values]]]
    std::string_view value;
[[[ENDIF]]]
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

[[[IF has_member_counters]]]
bool check_option_counts(Arguments& result, MemberCounters& counters)
{
    [[[option_counter_checks]]]
    return true;
}
[[[ENDIF]]]

[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool auto_exit)
{
    if (argc == 0)
        return [[[class_name]]]();

[[[IF has_program_name]]]
    program_name = get_base_name(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
[[[IF has_member_counters]]]
    MemberCounters counters;
[[[ENDIF]]]
    std::vector<std::string_view> arguments;
    ArgumentIterator arg_it(argc - 1, argv + 1);
[[[IF has_final_option]]]
    bool final_option = false;
[[[ENDIF]]]
    while (arg_it.has_next())
    {
        auto arg = arg_it.next_argument();
        if (arg.is_option)
        {
            auto option_code = find_option_code(arg);
[[[IF has_member_counters]]]
            switch (process_option(result, counters, arg, option_code, arg_it))
[[[ELSE]]]
            switch (process_option(result, arg, option_code, arg_it))
[[[ENDIF]]]
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
        {
            while (arg_it.has_next())
                arguments.push_back(arg_it.next_argument().string);
            break;
        }
[[[ENDIF]]]
    }
[[[IF has_member_counters]]]
    if (!check_option_counts(result, counters))
    {
        if (auto_exit)
            exit(EINVAL);
        result.parse_arguments_result = Arguments::RESULT_ERROR;
        return result;
    }
[[[ENDIF]]]
    return result;
}
"""
