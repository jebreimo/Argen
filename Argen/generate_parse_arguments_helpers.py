# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-02-20.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
import tools
import generate_parse_option as gpo
import generate_argument_processors as gap


def join_text(words, separator, final_separator):
    if len(words) <= 2:
        return final_separator.join(words)
    return final_separator.join((separator.join(words[:-1]), words[-1]))


def format_count(count):
    if not count or not count[0] and not count[1]:
        return ""
    if count[0] == count[1]:
        if count[0] == 1:
            return "must be given"
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


def generate_test(value_range, variable):
    lo, hi = value_range
    if not lo and not hi:
        return None
    elif lo == hi:
        return f"{variable} != {lo}"
    elif lo and hi:
        return f"{variable} < {lo} || {hi} < {variable}"
    elif lo:
        return f"{variable} < {lo}"
    else:
        return f"{hi} < {variable}"


def get_all_flags(arguments):
    flags = []
    for arg in arguments:
        if arg.flags:
            flags.extend(arg.flags)
    return flags


class ParseArgumentsHelpersGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.has_final_option = any(o for o in self._session.arguments
                                    if o.post_operation == "final")
        self.has_program_name = session.code_properties.has_program_name
        self.has_delimited_options = session.code_properties.has_delimited_options
        self.has_delimited_arguments = session.code_properties.has_delimited_arguments
        self.has_values = any(a for a in session.arguments
                              if a.operation != "none" and a.value is None)
        self.has_member_counters = session.code_properties.counted_options
        self.argument_size = tools.get_accumulated_count(session.code_properties.arguments)
        self.has_argument_size_check = self.argument_size != (0, None)
        self.has_arguments = session.code_properties.arguments
        self.has_normal_arguments = not session.settings.immediate_callbacks \
            or len(session.code_properties.arguments) != 1 \
            or not session.code_properties.arguments[0].callback
        self.has_callback_argument = session.settings.immediate_callbacks \
            and len(session.code_properties.arguments) == 1 \
            and session.code_properties.arguments[0].callback
        self.has_options = session.code_properties.options

    def option_cases(self, *args):
        return gpo.generate_option_cases(self._session)

    def option_counters(self, *args):
        result = []
        for opt in self._session.code_properties.counted_options:
            result.append("size_t %s_counter = 0;" % opt.option_name)
        return result

    def option_counter_checks(self, *args):
        result = []
        for opt in self._session.code_properties.counted_options:
            test = generate_test(opt.count,
                                 "counters.%s_counter" % opt.option_name)
            result.append("if (%s)" % test)
            result.append("{")
            result.append("    write_error_text(\"%s %s.\");"
                          % (join_text(opt.flags, ", ", " or "),
                             format_count(opt.count)))
            result.append("    return false;")
            result.append("}")
        return result

    def member_size_checks(self, *args):
        result = []
        for mem in self._session.code_properties.sized_members:
            test = generate_test(mem.member_size, "result.%s.size()" % mem.name)
            result.append("if (%s)" % test)
            result.append("{")
            result.append("    write_error_text(\"%s %s.\");"
                          % (join_text(get_all_flags(mem.arguments),
                                       ", ", " or "),
                             format_count(mem.member_size)))
            result.append("    return false;")
            result.append("}")
        return result

    def argument_size_checks(self, *args):
        result = []
        lo, hi = self.argument_size
        if lo == hi:
            phrase = str(lo)
        elif lo and not hi:
            phrase = "%d or more" % lo
        elif not lo and hi:
            phrase = "at most %d" % hi
        elif lo == hi - 1:
            phrase = "%d or %d" % (lo, hi)
        else:
            phrase = "from %d to %d" % (lo, hi)
        test = generate_test(self.argument_size, "arguments.size()")
        result.append(f"if (%s)" % test)
        result.append("{")
        result.append("    write_error_text(\"Incorrect number of arguments."
                      " Requires %s, received \"" % phrase)
        result.append("                     + std::to_string(arguments.size())"
                      " + \".\");")
        result.append("    return false;")
        result.append("}")
        return result

    def argument_processors(self, *args):
        return gap.generate_argument_processors(self._session)

    def process_callback_argument(self, *args):
        return gap.generate_immediate_argument_processor(self._session)


def generate_parse_arguments_helpers(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsHelpersGenerator(session))


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
[[[IF has_options]]]
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
OptionResult process_option([[[class_name]]]& result,
[[[IF has_member_counters]]]
                            MemberCounters& counters,
[[[ENDIF]]]
                            const Argument& arg,
                            int option_code,
                            ArgumentIterator& arg_it)
{
[[[IF has_values]]]
    std::string_view value;
[[[ENDIF]]]
[[[IF has_delimited_options]]]
    std::vector<std::string_view> parts;
[[[ENDIF]]]
    switch (option_code)
    {
    [[[option_cases]]]
    default:
        return OptionResult::UNKNOWN_OPTION;
    }
    return OptionResult::NORMAL_OPTION;
}

[[[IF has_member_counters]]]
bool check_option_counts([[[class_name]]]& result, MemberCounters& counters)
{
    [[[option_counter_checks]]]
    [[[member_size_checks]]]
    return true;
}
[[[ENDIF]]]
[[[ENDIF]]]
[[[IF has_normal_arguments]]]

bool process_arguments([[[class_name]]]& result,
                       const std::vector<std::string_view>& arguments)
{
[[[IF has_argument_size_check]]]
    [[[argument_size_checks]]]
[[[ENDIF]]]
    size_t i = 0;
    const size_t n = arguments.size();
[[[IF has_delimited_arguments]]]
    std::vector<std::string_view> parts;
[[[ENDIF]]]
    [[[argument_processors]]]
    return true;
}
[[[ENDIF]]]
[[[IF has_callback_argument]]]

bool process_argument([[[class_name]]]& result, const Argument& arg)
{
[[[IF has_delimited_arguments]]]
    std::vector<std::string_view> parts;
[[[ENDIF]]]
    [[[process_callback_argument]]]
    return true;
}
[[[ENDIF]]]\
"""