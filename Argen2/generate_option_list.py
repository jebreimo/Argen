# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


def make_enum_lines(options):
    lines = []
    prev_option = None
    for option in options:
        if prev_option:
            lines.append("Option_%s," % prev_option.option_name)
        prev_option = option
    if prev_option:
        lines.append("Option_%s" % prev_option.option_name)
    return lines


def iterate_over_nth(items, n):
    for item in items:
        yield item[n]


def find_min_prefix_length(s):
    if s[0] == "/":
        return 1
    elif s[0] == "-":
        if len(s) > 1 and s[1] == "-":
            return 2
        else:
            return 1
    else:
        return 0


def find_first_unique_char(str1, str2):
    max_index = min(len(str1), len(str2))
    for i in range(find_min_prefix_length(str2), max_index):
        if str1[i] != str2[i]:
            return i + 1
    return max_index


def make_minimal_flag_strings(flags):
    prefixes = []
    for flag in flags:
        text = flag[0]
        if not prefixes:
            index = find_min_prefix_length(text) + 1
            prefixes.append((text[:index], text[index:], text))
        else:
            index = find_first_unique_char(prefixes[-1][0], text)
            if index == len(prefixes[-1][0]):
                prev_text = prefixes[-1][2]
                index = find_first_unique_char(prev_text, text)
                prefixes[-1] = prev_text[:index], prev_text[index:], prev_text
                if index == len(prev_text):
                    index += 1
            prefixes.append((text[:index], text[index:], text))
    return [(p[0], p[1], f[1]) for p, f in zip(prefixes, flags)]


class OptionGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self._flags = []
        if session.code_properties.short_options:
            self._short_flags = []
        else:
            self._short_flags = self._flags
        self._options = []
        for opt in (a for a in self._session.arguments if a.flags):
            self._options.append(opt)
            for flag in opt.flags:
                if len(flag) == 2 and flag[0] == "-":
                    self._short_flags.append((flag, opt))
                else:
                    self._flags.append((flag, opt))
        self._short_flags.sort(key=lambda f: f[0])
        self._flags.sort(key=lambda f: f[0])

    def has_any_options(self):
        return self._short_flags or self._flags

    def option_enums(self, params, context):
        return make_enum_lines(self._options)

    def has_short_options(self, params, context):
        return self._short_flags

    def short_option_chars(self, params, context):
        return "".join(f[0][1] for f in self._short_flags)

    def short_option_indices(self, params, context):
        return make_enum_lines(iterate_over_nth(self._short_flags, 1))

    def has_options(self, params, context):
        return self._flags

    def enum_base_type(self, params, context):
        return "char" if len(self._options) < 128 else "short"

    def option_indices(self, params, context):
        return make_enum_lines(iterate_over_nth(self._flags, 1))

    def option_strings(self, params, context):
        strings = []
        for s, suffix, option in make_minimal_flag_strings(self._flags):
            if suffix:
                strings.append('"%s\\001%s",' % (s, suffix))
            else:
                strings.append('"%s",' % s)
        strings[-1] = strings[-1][:-1]
        return strings


def generate_options(session):
    generator = OptionGenerator(session)
    if not generator.has_any_options():
        return None
    return templateprocessor.make_lines(OPTIONS_TEMPLATE, generator)


OPTIONS_TEMPLATE = """\
enum Options
{
    [[[option_enums]]]
};    

[[[IF has_short_options]]]
const char shortOptions[] = "[[[short_option_chars]]]";
const [[[enum_base_type]]] shortOptionIndices[] =
{
    [[[short_option_indices]]]
};

[[[ENDIF]]]
[[[IF has_options]]]
const char* optionStrings[] =
{
    [[[option_strings]]]
};

const [[[enum_base_type]]] optionIndices[] =
{
    [[[option_indices]]]
};

int compareFlag(const std::string_view& flag, const char* pattern)
{
    size_t i = 0;
    while (true)
    {
        if (i == flag.size())
        {
            if (pattern[i] == 1)
                return 0;
            else
                return pattern[i];
        }
        else if (pattern[i] == 1)
        {
            break;
        }
        else if (flag[i] != pattern[i])
        {
            return flag[i] - pattern[i];
        }
        ++i;
    }

    for (; i < flag.size(); ++i)
    {
        if (flag[i] != pattern[i + 1])
            return flag[i] - pattern[i + 1];
        else if (pattern[i + 1] == 0)
            break;
    }
    return 0;
}

template <typename RndAccIt>
RndAccIt findFlag(RndAccIt begin, RndAccIt end, const std::string_view& flag)
{
    auto originalEnd = end;
    while (begin != end)
    {
        auto mid = begin + std::distance(begin, end) / 2;
        auto cmp = compareFlag(flag, *mid);
        if (cmp == 0)
            return mid;
        if (cmp < 0)
            end = mid;
        else
            begin = mid + 1;
    }
    return originalEnd;
}
[[[ENDIF]]]

int findOptionCode(const Argument& argument)
{
    auto str = argument.string;
    if (argument.isShortOption)
    {
        char c = str[str.size() - 1];
        auto pos = std::lower_bound(std::begin(shortOptions),
                                    std::end(shortOptions),
                                    c);
        if (pos == std::end(shortOptions))
            return -1;
        return int(shortOptionIndices[pos - std::begin(shortOptions)]);
    }
    auto pos = findFlag(std::begin(optionStrings),
                        std::end(optionStrings),
                        argument.string);
    if (pos == std::end(optionStrings))
        return -1;
    return int(optionIndices[pos - std::begin(optionStrings)]);
}
"""

# def option_enum(self, params, context):
#     options = [a for a in self._session.arguments if a.flags]
#     if not options:
#         return None
#     lines = ["enum class Options : char", "{"]
#     lines.extend(["    Option_%s," % o.option_name for o in options[:-1]])
#     lines.append("    Option_%s" % options[-1].option_name)
#     lines.append("};")
#     return lines
#
#
# def short_option_list(self, params, context):
#     flags = []
#     for opt in (a for a in self._session.arguments if a.flags):
#         for flag in opt.flags:
#             if len(flag) == 2 and flag[0] == "-":
#                 flags.append((flag, opt))
#     if not flags:
#         return None
#     flags.sort(key=lambda f: f[0])
#     flags_string = "".join(f[0][1] for f in flags)
#     lines = ['const char shortOptions = "%s";' % flags_string,
#              "const char shortOptionIndices[] =",
#              "{"]
#     lines.extend("    Option_%s," % f[1].option_name for f in flags[:-1])
#     lines.append("    Option_%s" % flags[-1][1].option_name)
#     lines.append("};")
#     return lines
#
#
# def option_list(self, params, context):
#     flags = []
#     for opt in (a for a in self._session.arguments if a.flags):
#         for flag in opt.flags:
#             if len(flag) != 2 or flag[0] != "-":
#                 flags.append((flag, opt))
#     if not flags:
#         return None
