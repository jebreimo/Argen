# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-26.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
from find_shortest_unique_prefixes import find_shortest_unique_prefixes


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
        self.case_insensitive = session.code_properties.case_insensitive
        if self.case_insensitive:
            self._short_flags.sort(key=lambda f: f[0].upper())
            self._flags.sort(key=lambda f: f[0].upper())
        else:
            self._short_flags.sort(key=lambda f: f[0])
            self._flags.sort(key=lambda f: f[0])

    def has_any_options(self):
        return self._short_flags or self._flags

    def option_enums(self, *args):
        return make_enum_lines(self._options)

    def has_short_options(self, *args):
        return self._short_flags

    def short_option_chars(self, *args):
        return "".join(f[0][1] for f in self._short_flags)

    def short_option_indices(self, *args):
        return make_enum_lines(iterate_over_nth(self._short_flags, 1))

    def has_options(self, *args):
        return self._flags

    def enum_base_type(self, *args):
        return "char" if len(self._options) < 128 else "short"

    def option_indices(self, *args):
        return make_enum_lines(iterate_over_nth(self._flags, 1))

    def option_strings(self, *args):
        strings = []
        unique_prefixes = find_shortest_unique_prefixes(
            self._flags,
            self._session.code_properties.case_insensitive)
        for s, suffix, option in unique_prefixes:
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
const char SHORT_OPTIONS[] = "[[[short_option_chars]]]";
const [[[enum_base_type]]] SHORT_OPTION_INDICES[] =
{
    [[[short_option_indices]]]
};

[[[ENDIF]]]
[[[IF has_options]]]
const char* OPTION_STRINGS[] =
{
    [[[option_strings]]]
};

const [[[enum_base_type]]] OPTION_INDICES[] =
{
    [[[option_indices]]]
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
                return pattern[i];
        }
        else if (pattern[i] == 1)
        {
            break;
        }
[[[IF case_insensitive]]]
        else if (std::toupper(flag[i]) != std::toupper(pattern[i]))
        {
            return std::toupper(flag[i]) - std::toupper(pattern[i]);
        }
[[[ELSE]]]
        else if (flag[i] != pattern[i])
        {
            return flag[i] - pattern[i];
        }
[[[ENDIF]]]
        ++i;
    }

    for (; i < flag.size(); ++i)
    {
[[[IF case_insensitive]]]
        if (std::toupper(flag[i]) != std::toupper(pattern[i + 1]))
            return std::toupper(flag[i]) - std::toupper(pattern[i + 1]);
[[[ELSE]]]
        if (flag[i] != pattern[i + 1])
            return flag[i] - pattern[i + 1];
[[[ENDIF]]]
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
[[[ENDIF]]]

int find_option_code(const Argument& argument)
{
    auto str = argument.string;
    if (argument.isShortOption)
    {
        char c = str[str.size() - 1];
[[[IF case_insensitive]]]
        auto pos = std::lower_bound(
                std::begin(SHORT_OPTIONS),
                std::end(SHORT_OPTIONS),
                c,
                [](auto a, auto b){return std::toupper(a) < std::toupper(b);});
[[[ELSE]]]
        auto pos = std::lower_bound(std::begin(SHORT_OPTIONS),
                                    std::end(SHORT_OPTIONS),
                                    c);
[[[ENDIF]]]
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
"""
