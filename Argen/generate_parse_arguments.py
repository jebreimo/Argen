# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class ParseArgumentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.has_final_option = any(o for o in self._session.arguments
                                    if o.post_operation == "final")
        self.has_program_name = session.code_properties.has_program_name
        self.has_member_counters = session.code_properties.counted_options
        self.has_arguments = session.code_properties.arguments
        self.has_normal_arguments = not session.settings.immediate_callbacks \
            or len(session.code_properties.arguments) != 1 \
            or not session.code_properties.arguments[0].callback
        self.has_callback_argument = session.settings.immediate_callbacks \
            and len(session.code_properties.arguments) == 1 \
            and session.code_properties.arguments[0].callback
        self.has_final_checks = self.has_member_counters \
                                or self.has_normal_arguments
        self.has_options = session.code_properties.options

    def final_checks(self, *args):
        checks = []
        if self.has_member_counters:
            checks.append("!check_option_counts(result, counters)")
        if self.has_normal_arguments:
            checks.append("!process_arguments(result, arguments)")
        for i in range(1, len(checks)):
            checks[i] = "|| " + checks[i]
        return checks


def generate_parse_arguments(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsGenerator(session))


PARSE_ARGUMENTS_TEMPLATE = """\
[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool auto_exit)
{
    if (argc == 0)
        return [[[class_name]]]();

[[[IF has_program_name]]]
    program_name = get_base_name(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
[[[IF has_arguments]]]
    std::vector<std::string_view> arguments;
[[[ENDIF]]]
[[[IF has_options]]]
[[[IF has_member_counters]]]
    MemberCounters counters;
[[[ENDIF]]]
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
[[[IF has_final_option]]]
            case OptionResult::FINAL_OPTION:
                final_option = true;
                break;
[[[ENDIF]]]
            case OptionResult::ABORTING_OPTION:
                if (auto_exit)
                    exit(0);
                break;
            case OptionResult::INVALID_OPTION:
                if (auto_exit)
                    exit(Arguments::RESULT_ERROR);
                result.[[[function_name]]]_result = Arguments::RESULT_ERROR;
                break;
            case OptionResult::UNKNOWN_OPTION:
                write_error_text(to_string(arg) + ": unknown option.");
                if (auto_exit)
                    exit(Arguments::RESULT_ERROR);
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
[[[IF has_normal_arguments]]]
            arguments.push_back(arg.string);
[[[ELIF has_callback_argument]]]
            process_argument(result, arg);
[[[ELSE]]]
            write_error_text(to_string(arg) + ": the program doesn't take any arguments.");
            if (auto_exit)
                exit(Arguments::RESULT_ERROR);
            result.[[[function_name]]]_result = Arguments::RESULT_ERROR;
            return result;
[[[ENDIF]]]
        }
[[[IF has_final_option]]]
        if (final_option)
        {
[[[IF has_normal_arguments]]]
            while (arg_it.has_next())
                arguments.push_back(arg_it.next_argument().string);
[[[ELIF has_callback_argument]]]
            while (arg_it.has_next())
                process_argument(result, arg);
[[[ENDIF]]]
            break;
        }
[[[ENDIF]]]
    }
[[[ELSE]]]
    for (int i = 1; i < argc; ++i)
        arguments.emplace_back(argv[i], strlen(argv[i]));
[[[ENDIF]]]
[[[IF has_final_checks]]]
    if ([[[final_checks]]])
    {
        if (auto_exit)
            exit(Arguments::RESULT_ERROR);
        result.parse_arguments_result = Arguments::RESULT_ERROR;
        return result;
    }
[[[ENDIF]]]
    return result;
}

void write_help_text(std::ostream& stream, unsigned line_width)
{
    if (line_width == 0)
        line_width = get_default_line_width();
    write_formatted_text(stream, HELP_TEXT, line_width);  
}

void write_brief_help_text(std::ostream& stream, unsigned line_width)
{
    if (line_width == 0)
        line_width = get_default_line_width();
    write_formatted_text(stream, BRIEF_HELP_TEXT, line_width);
}
"""
